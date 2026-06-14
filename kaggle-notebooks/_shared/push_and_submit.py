#!/usr/bin/env python3
"""Push gateway notebook to Kaggle (Run All) and submit to ARC-AGI-3."""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

from kagglesdk import KaggleClient
from kagglesdk.competitions.types.competition_api_service import ApiCreateCodeSubmissionRequest
from kagglesdk.kernels.types.kernels_api_service import (
    ApiGetKernelSessionStatusRequest,
    ApiListKernelSessionOutputRequest,
    ApiSaveKernelRequest,
)
from kagglesdk.kernels.types.kernels_enums import KernelExecutionType, KernelWorkerStatus

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase_registry import COMP, PHASES, PhaseConfig


def _token() -> str:
    if os.environ.get("KAGGLE_API_TOKEN"):
        return os.environ["KAGGLE_API_TOKEN"].strip()
    path = os.path.expanduser("~/.kaggle/access_token")
    if os.path.isfile(path):
        return open(path, encoding="utf-8").read().strip()
    sys.exit("Set KAGGLE_API_TOKEN or ~/.kaggle/access_token")


def push(client: KaggleClient, phase: PhaseConfig) -> int:
    notebook = phase.notebook_path
    if not notebook.is_file():
        raise FileNotFoundError(f"Notebook not found: {notebook}")
    req = ApiSaveKernelRequest()
    req.slug = phase.kernel_slug
    req.new_title = phase.title
    req.text = notebook.read_text(encoding="utf-8")
    req.language = "python"
    req.kernel_type = "notebook"
    req.competition_data_sources = [COMP]
    req.is_private = True
    req.enable_internet = False
    req.enable_gpu = False
    req.kernel_execution_type = KernelExecutionType.SAVE_AND_RUN_ALL
    resp = client.kernels.kernels_api_client.save_kernel(req)
    if resp.error:
        raise RuntimeError(resp.error)
    print(f"Pushed {resp.ref} version={resp.version_number} url={resp.url}")
    return int(resp.version_number or 1)


def wait_for_run(client: KaggleClient, phase: PhaseConfig, timeout_s: int = 900) -> None:
    owner, slug = phase.kernel_slug.split("/", 1)
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            req = ApiGetKernelSessionStatusRequest()
            req.user_name = owner
            req.kernel_slug = slug
            st = client.kernels.kernels_api_client.get_kernel_session_status(req)
            print(f"Kernel status: {st.status.name}")
            if st.status == KernelWorkerStatus.COMPLETE:
                out = ApiListKernelSessionOutputRequest()
                out.user_name = owner
                out.kernel_slug = slug
                files = client.kernels.kernels_api_client.list_kernel_session_output(out)
                names = [f.file_name for f in (files.files or [])]
                has_sub = any(n == "submission.parquet" or n.endswith("/submission.parquet") for n in names)
                print(f"Outputs: submission.parquet={has_sub} (listed {len(names)} files)")
                if not has_sub:
                    top = sorted(names)[:30]
                    raise RuntimeError(f"Missing submission.parquet. Sample outputs: {top}")
                return
            if st.status == KernelWorkerStatus.ERROR:
                raise RuntimeError(f"Kernel run failed: {st.failure_message}")
        except Exception as e:
            print(f"poll error: {e}")
        time.sleep(20)
    raise TimeoutError(f"Kernel did not complete within {timeout_s}s")


def submit(client: KaggleClient, phase: PhaseConfig, version: int, message: str) -> int:
    owner, slug = phase.kernel_slug.split("/", 1)
    req = ApiCreateCodeSubmissionRequest()
    req.competition_name = COMP
    req.file_name = "submission.parquet"
    req.kernel_owner = owner
    req.kernel_slug = slug
    req.kernel_version = version
    req.submission_description = message
    resp = client.competitions.competition_api_client.create_code_submission(req)
    if resp.error:
        raise RuntimeError(resp.error)
    print(f"Submitted ref={resp.ref} message={resp.message!r}")
    return int(resp.ref)


def main() -> None:
    p = argparse.ArgumentParser(description="Push + submit ASRA Kaggle gateway notebook")
    p.add_argument("--phase", type=int, required=True, choices=sorted(PHASES))
    p.add_argument("--message", default="")
    p.add_argument("--skip-push", action="store_true")
    p.add_argument("--skip-wait", action="store_true")
    p.add_argument("--version", type=int, default=0)
    p.add_argument("--push-only", action="store_true")
    args = p.parse_args()

    phase = PHASES[args.phase]
    message = args.message or f"{phase.agent_tag} v3 official gateway pattern"

    client = KaggleClient(api_token=_token())
    with client:
        version = args.version
        if not args.skip_push:
            version = push(client, phase)
        if version <= 0:
            version = 1
        if not args.skip_wait:
            wait_for_run(client, phase)
        if args.push_only:
            print(f"Push complete. Submit with: --skip-push --skip-wait --version {version} --message {message!r}")
            return
        submit(client, phase, version, message)


if __name__ == "__main__":
    main()
