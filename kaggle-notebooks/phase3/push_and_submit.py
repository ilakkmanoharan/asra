#!/usr/bin/env python3
"""Push Phase 3 notebook to Kaggle (Run All) and submit to ARC-AGI-3."""

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

HERE = Path(__file__).resolve().parent
KERNEL_SLUG = "ilakkmanoharan/asra-phase-3-arc-prize-2026"
COMP = "arc-prize-2026-arc-agi-3"
NOTEBOOK = HERE / "asra-phase-3-arc-prize-2026.ipynb"


def _token() -> str:
    if os.environ.get("KAGGLE_API_TOKEN"):
        return os.environ["KAGGLE_API_TOKEN"].strip()
    path = os.path.expanduser("~/.kaggle/access_token")
    if os.path.isfile(path):
        return open(path, encoding="utf-8").read().strip()
    sys.exit("Set KAGGLE_API_TOKEN or ~/.kaggle/access_token")


def push(client: KaggleClient) -> int:
    text = NOTEBOOK.read_text(encoding="utf-8")
    req = ApiSaveKernelRequest()
    req.slug = KERNEL_SLUG
    req.new_title = "ASRA Phase 3 — ARC Prize 2026"
    req.text = text
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


def wait_for_run(client: KaggleClient, timeout_s: int = 900) -> None:
    owner, slug = KERNEL_SLUG.split("/", 1)
    deadline = time.time() + timeout_s
    while time.time() < deadline:
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
            has_agent = any(n == "my_agent.py" or n.endswith("/my_agent.py") for n in names)
            has_sub = any(n == "submission.parquet" or n.endswith("/submission.parquet") for n in names)
            print(f"Outputs: my_agent.py={has_agent} submission.parquet={has_sub} (listed {len(names)} files)")
            if not has_agent or not has_sub:
                top = sorted(n for n in names if not n.startswith("asra_venv"))[:30]
                raise RuntimeError(f"Missing outputs. Sample: {top}")
            return
        if st.status == KernelWorkerStatus.ERROR:
            raise RuntimeError(f"Kernel run failed: {st.failure_message}")
        time.sleep(20)
    raise TimeoutError(f"Kernel did not complete within {timeout_s}s")


def submit(client: KaggleClient, version: int, message: str) -> int:
    owner, slug = KERNEL_SLUG.split("/", 1)
    req = ApiCreateCodeSubmissionRequest()
    req.competition_name = COMP
    req.file_name = "submission.parquet"
    req.kernel_owner = owner
    req.kernel_slug = slug
    req.kernel_version = version
    req.submission_description = message
    resp = client.competitions.competition_api_client.create_code_submission(req)
    print(f"Submitted ref={resp.ref} message={resp.message!r}")
    return int(resp.ref)


def main() -> None:
    p = argparse.ArgumentParser(description="Push + submit ASRA Phase 3 Kaggle notebook")
    p.add_argument("--message", default="ASRA v0.5-phase3 exploration memory hints")
    p.add_argument("--skip-push", action="store_true")
    p.add_argument("--skip-wait", action="store_true", help="Submit without waiting for Run All")
    p.add_argument("--version", type=int, default=0, help="Kernel version to submit (0 = pushed)")
    p.add_argument("--push-only", action="store_true", help="Push and wait only; do not submit")
    args = p.parse_args()

    if not NOTEBOOK.is_file():
        sys.exit(f"Notebook not found: {NOTEBOOK}")

    client = KaggleClient(api_token=_token())
    with client:
        version = args.version
        if not args.skip_push:
            version = push(client)
        if version <= 0:
            version = 1
        if not args.skip_wait:
            wait_for_run(client)
        if args.push_only:
            print(f"Push complete. Submit manually with version={version}")
            return
        submit(client, version, args.message)


if __name__ == "__main__":
    main()
