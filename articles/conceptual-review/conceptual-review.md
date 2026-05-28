# Architectures for Adaptive Scientific Reasoning Under Uncertainty

## Abstract

Scientific intelligence increasingly depends on systems that can reason from interventions rather than merely fit observations. Across artificial intelligence, cognitive science, information theory, causal inference, and systems biology, a convergent research program is emerging: intelligent systems should build internal models of the world, use those models to choose actions or experiments, update their beliefs from the resulting transitions, and preserve evidence in forms that support future generalization. This review synthesizes conceptual foundations from model-based reinforcement learning, learned planning systems, the free-energy principle, structural causal modeling, information theory, biological perturbation resources, cell atlas initiatives, and abstract measures of intelligence.

The reviewed literature suggests that adaptive scientific reasoning is not a single algorithmic capability but an architecture-level property. Dreamer and MuZero show how learned world models can support decision-making through imagination and planning. The free-energy principle reframes adaptation as uncertainty reduction through perception and action. Pearl's causal framework clarifies why predictive models are insufficient for scientific reasoning unless they distinguish observation from intervention and counterfactual dependence. Information theory provides language for uncertainty, compression, and experiment value. LINCS L1000, scPerturb, and the Human Cell Atlas show how modern biology is becoming an intervention-rich, high-dimensional state space in which reasoning systems must learn from perturbation-response structure rather than static measurements. Chollet's measure of intelligence adds a complementary criterion: general intelligence should be evaluated by skill-acquisition efficiency under bounded experience and priors.

Taken together, these works point toward adaptive scientific reasoning systems organized around state representation, transition modeling, action semantics, causal hypothesis generation, uncertainty-aware intervention selection, evidence memory, and model revision. Yet major gaps remain: scalable causal representation learning, calibrated uncertainty in high-dimensional biological spaces, interpretable abstraction, memory consolidation, benchmark design, and the gap between interactive decision environments and real scientific experimentation. Future systems will likely combine world models, causal graphs, active inference, symbolic abstraction, and biological foundation models into architectures capable of proposing, testing, and revising scientific hypotheses under uncertainty.

## 1. Introduction

The central challenge of scientific intelligence is not prediction alone. A scientific agent must distinguish what is observed from what is controlled, what is correlated from what is caused, what is already known from what remains uncertain, and what intervention would most improve its understanding. This requirement becomes especially visible in modern biology, where large-scale perturbation screens, single-cell technologies, and cell atlas projects produce high-dimensional measurements of cellular systems under changing conditions. A system that merely classifies samples or predicts gene expression may be useful, but it is not yet reasoning scientifically. Scientific reasoning requires an architecture that can form hypotheses, choose experiments, update models from transitions, and preserve evidence across contexts.

Several intellectual traditions now converge on this problem. In artificial intelligence, model-based reinforcement learning has revived the idea that agents should learn world models and use them for planning. Dreamer demonstrates that agents can learn compact latent dynamics and improve behavior by imagining trajectories inside those models (Hafner et al., 2019). MuZero shows that planning can be performed with a learned model that need not reconstruct the full environment, as long as it supports action-conditioned prediction relevant to reward and policy (Schrittwieser et al., 2020). These systems do not solve scientific reasoning, but they establish a crucial architectural principle: adaptive behavior can emerge from learned transition models coupled to action selection.

In theoretical neuroscience and cognitive science, the free-energy principle offers a broader account of adaptive systems as entities that minimize uncertainty or surprise through perception and action (Friston, 2010). Although the free-energy principle is not an engineering recipe by itself, it provides a unifying interpretation of active inference: agents do not passively receive data; they act to sample the world in ways that reduce uncertainty relative to their internal generative models. This idea is closely aligned with scientific experimentation, where interventions are chosen to expose informative differences among hypotheses.

Causal inference contributes another essential layer. Pearl's structural causal model framework separates statistical association from intervention and counterfactual reasoning (Pearl, 2009). This distinction is indispensable for scientific agents. A system trained only to predict observed outcomes cannot answer what would happen under a new perturbation unless its representation supports intervention semantics. Biological reasoning, in particular, requires this distinction because gene expression, cell state, pathway activity, and phenotypic response are entangled in networks of regulation and feedback.

Information theory provides a vocabulary for the value of observations, the compression of representations, and the selection of experiments. Entropy, mutual information, channel capacity, and rate-distortion concepts clarify how agents may trade off predictive accuracy, representational compactness, and uncertainty reduction (Cover and Thomas, 2006). These concepts appear implicitly in many adaptive systems: world models compress observations into latent states; planners prefer actions that reduce uncertainty or increase expected value; biological experiments seek perturbations that reveal regulatory structure.

Finally, the biological data landscape makes these ideas urgent. LINCS L1000 provides large-scale perturbational gene expression signatures (Subramanian et al., 2017). scPerturb organizes single-cell perturbation data that connect genetic or chemical interventions to heterogeneous cell responses (Peidli et al., 2024). The Human Cell Atlas aims to map human cell types and states at comprehensive scale (Regev et al., 2017). Together, these resources transform biology into a domain of state spaces, interventions, transitions, and multi-scale representation problems.

This review argues that these literatures form the foundation for adaptive scientific reasoning systems: architectures that learn from action-conditioned state transitions and use uncertainty-aware models to select future interventions. The aim is not to collapse all frameworks into a single theory, but to identify the shared abstractions that can support future systems. The review emphasizes mechanisms, assumptions, architectural patterns, and unresolved conceptual gaps.

## 2. Intellectual Foundations and Historical Context

Adaptive scientific reasoning inherits from several traditions that historically developed in partial isolation.

### 2.1 Cybernetics, control, and feedback

Cybernetics and control theory introduced the idea that intelligent behavior is organized through feedback loops. A system senses a state, compares it with a goal or model, acts, observes the resulting change, and updates future action. This loop is also the minimal structure of scientific experimentation. A scientist observes a system, proposes an intervention, measures the response, and refines the hypothesis. Modern AI often implements this loop computationally, but the underlying concept is older: intelligence is not static representation but regulation under uncertainty.

### 2.2 Reinforcement learning and world models

Reinforcement learning formalizes decision-making as interaction with an environment. Classical model-free reinforcement learning can learn policies without explicit transition models, but scientific reasoning usually demands more: an agent must understand what changed and why. Model-based reinforcement learning therefore becomes conceptually important. It asks the agent to learn or use a model of how actions transform states. Dreamer and MuZero represent two influential variants of this tradition. Dreamer learns latent dynamics and trains behavior inside imagined rollouts. MuZero learns a model optimized for planning, not reconstruction. Both show that world models need not be literal replicas of the world; they can be task-relevant abstractions that support action.

### 2.3 Active inference and the free-energy principle

The free-energy principle proposes that self-organizing systems maintain their integrity by minimizing variational free energy, a bound related to surprise under an internal generative model (Friston, 2010). In active inference, action becomes a means of sampling expected observations and reducing uncertainty. For scientific reasoning, this is a powerful abstraction: experiments are not merely actions that maximize reward; they are actions that distinguish among models. The free-energy tradition therefore connects perception, action, uncertainty, and model revision in a single conceptual framework.

### 2.4 Causal inference and intervention semantics

Pearl's causal framework provides the language needed to distinguish observing a variable from intervening on it. Structural causal models encode variables, causal relations, interventions, and counterfactuals. Scientific reasoning depends on these distinctions. A perturbation in biology is not simply another input feature; it is an intervention that changes the data-generating process. A reasoning system that lacks intervention semantics may discover predictive regularities but fail when asked to design experiments or infer mechanisms.

### 2.5 Information theory and representation

Information theory formalizes uncertainty and communication. In adaptive systems, information-theoretic principles appear in at least four ways. First, entropy quantifies uncertainty over states, models, or outcomes. Second, mutual information can measure how informative an action or experiment is about an unknown mechanism. Third, compression motivates latent representations that preserve relevant structure while discarding noise. Fourth, information gain offers a criterion for exploration. These ideas do not prescribe an entire architecture, but they provide objective functions and diagnostics for scientific learning.

### 2.6 Systems biology and perturbation atlases

Modern biological datasets increasingly resemble environments for scientific agents. LINCS L1000 records gene expression signatures under chemical and genetic perturbations. scPerturb aggregates single-cell perturbation experiments where cellular response is heterogeneous and context-dependent. The Human Cell Atlas maps cellular identity and state across tissues. These projects shift biology from a collection of isolated measurements toward an intervention-indexed state space. They make it possible to ask not only what a cell is, but how it changes under perturbation and how such transitions reveal underlying regulatory structure.

### 2.7 Intelligence as skill-acquisition efficiency

Chollet's critique of conventional AI evaluation reframes intelligence as the efficiency with which systems acquire new skills from limited prior knowledge and experience (Chollet, 2019). This is relevant to scientific reasoning because scientific environments rarely offer unlimited trials. A useful scientific agent must generalize from sparse interventions, adapt to new systems, and avoid overfitting to benchmark distributions. Skill-acquisition efficiency therefore complements world-model and causal perspectives: a system is more scientifically intelligent if it can infer useful abstractions from fewer experiments.

## 3. Core Terminology and Conceptual Definitions

A coherent review requires a shared vocabulary across fields whose terms often overlap without being identical.

**State** refers to a representation of the system at a time or condition. In reinforcement learning, state may be an observation or latent representation. In biology, state may include gene expression, chromatin accessibility, morphology, cell identity, pathway activity, or phenotypic readouts. In scientific reasoning, state should be treated as a representation chosen for inference, not as a complete description of reality.

**Action** is an operation performed by an agent or experimenter. In games, actions may be moves or controls. In biology, actions are perturbations such as gene knockdowns, CRISPR edits, drug treatments, dosage changes, or environmental shifts.

**Intervention** is an action with causal semantics. All interventions are actions, but not all actions are represented causally. An intervention changes the data-generating process and is ideally expressible in a do-operator or structural causal framework. Scientific reasoning requires intervention semantics because it asks what would happen if the system were manipulated.

**Transition** is a state-action-next-state relation. It is the basic unit that connects interaction to learning. Transition modeling is central to world models, experimental design, and biological perturbation analysis.

**World model** is an internal model that supports prediction or planning over future states, rewards, observations, or other task-relevant variables. A world model may be mechanistic, neural, symbolic, probabilistic, causal, or hybrid.

**Generative model** is a model of how observations arise from latent causes or states. In active inference, the generative model supports perception and action by allowing the agent to infer hidden causes and expected outcomes.

**Causal model** represents causal structure, interventions, and counterfactual dependencies. A causal model is stronger than a predictive model because it aims to support reasoning under distributional changes caused by interventions.

**Action semantics** refers to the learned meaning of actions in terms of their effects. In a biological setting, action semantics might describe how a drug shifts a cell state, which pathways are affected, or whether a perturbation reverses a disease signature.

**Evidence memory** is a stored record of observations, interventions, transitions, hypotheses, and outcomes. It differs from a parameterized model because it remains inspectable and can support replay, audit, retrieval, and reinterpretation.

**Uncertainty** may refer to uncertainty about the current state, the transition model, causal structure, parameters, observations, or goals. Scientific reasoning requires distinguishing these forms because different uncertainties motivate different experiments.

**Abstraction** is the compression of raw observations into variables, objects, mechanisms, or states that support reasoning. Abstraction is not merely dimensionality reduction; it is the construction of representations that preserve causal or functional relevance.

**Scientific reasoning system** denotes an architecture that can form, test, update, and reuse hypotheses about a domain. It is broader than a predictive model and more constrained than a general autonomous agent. Its defining loop is observation, hypothesis, intervention, evidence, model revision.

## 4. Theoretical Foundations

### 4.1 Dreamer: latent dynamics and imagined experience

Dreamer addresses the problem of learning control from high-dimensional observations by constructing a latent dynamics model and training behavior using imagined trajectories (Hafner et al., 2019). Its theoretical assumption is that useful control does not require exact reconstruction of the external world. Instead, the agent can learn a compact latent state that preserves information relevant to future prediction and reward. Reasoning is represented as rollout through a learned latent dynamics model, and adaptation occurs when imagined experience improves the policy.

The uncertainty problem in Dreamer is partially handled through probabilistic latent dynamics, although the system is primarily designed for control rather than explicit scientific hypothesis testing. Its contribution to scientific reasoning is architectural: observations can be encoded into latent states, action-conditioned transitions can be learned, and internal simulation can support decision-making. The limitation is that imagined rollouts optimized for reward are not equivalent to causal explanation. A Dreamer-like system may know what action is useful without knowing which mechanism explains its effect.

### 4.2 MuZero: planning with a task-relevant learned model

MuZero learns a model that supports planning without requiring direct reconstruction of environment observations (Schrittwieser et al., 2020). Its architecture includes representation, dynamics, and prediction functions. The representation function encodes observations into latent states; the dynamics function predicts future latent states and rewards after actions; the prediction function estimates policy and value. Planning is performed through search over this learned model.

The central conceptual innovation is that a world model can be useful even if it is not a faithful generative simulator. It needs to preserve the structure relevant to planning. For scientific reasoning, this raises a productive tension. Science often values mechanistic fidelity, while control may only require decision-relevant prediction. A scientific agent may therefore need both MuZero-like task relevance and Pearl-like causal interpretability. MuZero shows how planning can be integrated with learned representations, but it does not by itself solve causal identification or explanatory abstraction.

### 4.3 The free-energy principle: adaptation as uncertainty management

Friston's free-energy principle proposes that adaptive systems maintain their organization by minimizing variational free energy, which can be interpreted as a bound on surprise relative to a generative model (Friston, 2010). In this view, perception updates beliefs to explain observations, while action changes the world to bring observations into alignment with expectations. Active inference extends this to policy selection: agents choose actions expected to reduce uncertainty and satisfy prior preferences.

For scientific reasoning, the free-energy principle is most useful as a conceptual grammar for closed-loop learning. A scientific agent should not only fit existing data; it should select interventions that reduce uncertainty about hidden causes. However, the framework is broad and can become difficult to operationalize without specific model classes, objective functions, and experimental constraints. Its value in this synthesis is therefore architectural and epistemic: it explains why perception, action, and model revision should be unified rather than treated as separate modules.

### 4.4 Pearl's causality: intervention and counterfactual structure

Pearl's causal framework formalizes scientific questions that predictive models cannot answer reliably (Pearl, 2009). Structural causal models represent variables and causal dependencies. Interventions modify the structure, and counterfactuals ask what would have happened under alternative conditions. This framework is foundational for scientific reasoning because it clarifies the difference between learning patterns and learning mechanisms.

In biological perturbation settings, causal assumptions are unavoidable. A drug treatment, gene knockdown, or environmental change changes the system. If the model treats this only as another covariate, it may fail to generalize to new intervention combinations or contexts. Pearl's framework also reveals a limitation: causal identification often requires assumptions, experimental design, or prior knowledge. Autonomous scientific agents must therefore manage not only uncertainty over parameters but uncertainty over causal structure and identifiability.

### 4.5 Information theory: uncertainty, compression, and experiment value

Cover and Thomas provide the mathematical language for entropy, mutual information, channels, and compression (Cover and Thomas, 2006). These concepts help explain why adaptive systems need abstraction. A high-dimensional observation space cannot be used directly without selecting relevant structure. A world model compresses observations into latent variables. A causal model compresses dependencies into interpretable relations. An experiment is valuable when it reduces uncertainty about variables or models that matter.

Information theory also supports a view of scientific reasoning as resource-bounded inquiry. The agent has limited interventions, measurement capacity, compute, and prior knowledge. It must choose which questions are worth asking. Information gain is not the only criterion, since experiments have costs and may need to optimize goals, but it is a central component of principled exploration.

### 4.6 LINCS L1000: perturbation signatures as transition evidence

LINCS L1000 is important not merely as a dataset but as an example of perturbation-indexed biological measurement (Subramanian et al., 2017). It records gene expression signatures across many perturbagens, cell lines, doses, and conditions. Conceptually, it provides a state-response landscape: interventions induce measurable shifts in cellular expression space.

For adaptive scientific reasoning, such data can support action semantics. A perturbation's meaning is not its name alone but its observed effect across contexts. However, LINCS also illustrates major challenges: measurements are high-dimensional, context-dependent, noisy, incomplete, and partially indirect. Learning from them requires uncertainty, representation learning, and causal caution.

### 4.7 scPerturb: single-cell heterogeneity under intervention

scPerturb extends the perturbation-response paradigm into single-cell resolution (Peidli et al., 2024). This matters because interventions do not act on homogeneous cell populations. The same perturbation may produce different responses across cell types, states, lineages, or microenvironments. A scientific reasoning system must therefore represent distributions over cellular states rather than single aggregate outcomes.

The theoretical implication is that action semantics become conditional. A perturbation's effect depends on the starting state, context, and measurement scale. This aligns with state-conditioned world models in AI: an action has no universal effect independent of state. For biology, this point is essential. The meaning of a gene perturbation or drug is not fixed; it is defined by its transition pattern across cellular contexts.

### 4.8 Human Cell Atlas: state space construction

The Human Cell Atlas aims to map human cell types and states comprehensively (Regev et al., 2017). Its relevance to adaptive reasoning is representational. A scientific agent cannot reason about interventions unless it has a vocabulary of states. Cell atlases provide such vocabularies by organizing cellular diversity into types, states, trajectories, and tissue contexts.

Yet atlases are not intervention models by themselves. They describe the landscape of cellular identity and variation, while perturbation datasets describe how systems move through that landscape. The integration of atlases with perturbation-response data is therefore a central future direction: cell atlases define the state manifold, and intervention datasets define transition operators on that manifold.

### 4.9 Chollet's measure of intelligence: generalization under limited experience

Chollet argues that intelligence should be measured by skill-acquisition efficiency rather than performance on fixed task distributions (Chollet, 2019). This critique is directly relevant to scientific reasoning systems. A system trained on massive data but unable to adapt to a new biological context is not scientifically intelligent in the strong sense. Scientific reasoning often involves sparse data, novel conditions, and tasks whose structure must be inferred.

The conceptual contribution is to evaluate systems by their ability to acquire abstractions efficiently. This connects to ARC-style reasoning, causal generalization, and experiment design. A scientific agent should use prior knowledge without being trapped by it, learn from few interventions, and transfer abstract mechanisms across domains.

## 5. Architectural Analysis

The reviewed works suggest a general architecture for adaptive scientific reasoning. It can be expressed as a loop:

```text
Environment or biological system
  -> Observation and measurement
  -> State representation
  -> World or causal model
  -> Uncertainty estimation
  -> Hypothesis and intervention selection
  -> Action or experiment
  -> Transition evidence
  -> Memory and model update
  -> Revised abstraction
```

This loop is not identical to any single paper, but each paper contributes part of it.

Dreamer contributes the observation-to-latent-state-to-imagined-rollout pathway. Its architecture emphasizes the internal simulation of action-conditioned futures. In a scientific setting, this becomes a model for simulating possible experimental outcomes before performing costly interventions.

MuZero contributes the idea that a learned model can be optimized for planning utility rather than complete reconstruction. A scientific analogue would learn representations that preserve intervention-relevant structure: pathway activation, phenotype shifts, regulatory effects, or likely outcomes.

The free-energy principle contributes the closed-loop view in which perception and action are both ways of reducing uncertainty under a model. In scientific reasoning, this reframes experimentation as active sampling.

Causal inference contributes an intervention layer. Without this layer, actions are merely inputs and transitions are merely predictions. With it, actions become manipulations of structural mechanisms.

Information theory contributes metrics for uncertainty and evidence value. It can guide which experiment would maximally reduce ambiguity among hypotheses.

Biological perturbation and atlas datasets contribute the empirical substrate: high-dimensional state spaces, context-dependent interventions, and measured transitions.

These components can be organized into layers:

| Layer | Function | Representative foundations |
|---|---|---|
| Measurement layer | Collect observations, perturbation readouts, and context | LINCS, scPerturb, Human Cell Atlas |
| State layer | Encode observations into useful representations | Dreamer, MuZero, cell atlas state maps |
| Transition layer | Model action-conditioned changes | World models, perturbation signatures |
| Causal layer | Distinguish intervention from association | Pearl, experimental design |
| Uncertainty layer | Estimate ambiguity and information value | Free energy, Bayesian reasoning, information theory |
| Planning layer | Select actions or experiments | MuZero search, Dreamer imagination, active inference |
| Memory layer | Store traces, evidence, and revisions | Replay, transition datasets, evidence logs |
| Abstraction layer | Build reusable concepts and mechanisms | Chollet, symbolic abstraction, causal variables |

The architecture is fundamentally recursive. State representations improve as evidence accumulates. Better representations improve transition models. Better transition models improve experiment selection. Better experiments produce more informative evidence. Scientific reasoning emerges not from any one module but from the coordination of these loops.

## 6. Mechanisms and Reasoning Flows

### 6.1 From observation to state

The first mechanism is representation. Raw observations are too high-dimensional and often too noisy for direct reasoning. Dreamer and MuZero compress observations into latent states. Cell atlas projects organize biological measurements into cell types and states. In both cases, the key question is what information should be preserved. For control, the representation must support reward and policy prediction. For science, it must also support explanation, comparison, and intervention reasoning.

### 6.2 From action to transition

The second mechanism is transition learning. An action has meaning through its effect. In reinforcement learning, this effect may be a next state and reward. In biology, it may be a shift in gene expression, morphology, viability, lineage trajectory, or pathway activity. A scientific agent must infer action semantics from repeated state-action-next-state evidence. The same intervention may have different effects in different starting states, so transition models must be state-conditioned.

### 6.3 From prediction to hypothesis

Prediction is not the same as hypothesis formation. A hypothesis is a structured claim that can be tested: a perturbation affects a pathway; a cell state is resistant because of a regulatory circuit; two drugs converge on a shared mechanism; a latent variable captures differentiation trajectory. Predictive models can supply candidate regularities, but scientific reasoning requires packaging those regularities into testable claims.

### 6.4 From uncertainty to experiment selection

Uncertainty becomes actionable when it guides intervention. Information theory, active inference, and Bayesian experimental design all support this principle. A system should ask: which intervention would most reduce uncertainty about the model, causal structure, or decision-relevant outcome? This mechanism is especially important when experiments are expensive. In biological settings, an intervention may consume time, material, and measurement capacity. The agent must therefore balance expected information, expected utility, feasibility, and risk.

### 6.5 From evidence to memory

Scientific reasoning depends on memory that is more structured than learned parameters. A transition log preserves the context, intervention, observed response, uncertainty, and model state at the time of experimentation. Such memory supports auditability, replay, and reinterpretation. If a later model changes the meaning of a latent state, historical evidence can be reanalyzed. This distinguishes scientific memory from purely statistical training.

### 6.6 From memory to abstraction

Abstraction arises when repeated transitions reveal stable patterns. A model may learn that a class of perturbations induces similar transcriptional shifts, that certain cell states share vulnerability, or that an action changes position in an abstract environment. Chollet's emphasis on abstraction and skill-acquisition efficiency highlights the importance of forming reusable concepts rather than memorizing task-specific responses.

### 6.7 From abstraction to generalization

Generalization requires applying abstractions to new systems. In world-model systems, this may mean planning in unfamiliar environments. In biology, it may mean predicting perturbation response in a new cell type or disease context. The difficulty is that abstractions can fail under distribution shift. Causal abstraction is more robust than correlational abstraction when the causal structure is stable, but causal discovery itself requires assumptions and evidence.

## 7. Comparative Analysis

The reviewed works converge on interaction, representation, and uncertainty, but they differ in their theory of what makes a model useful.

| Framework | Core theory | World model | Adaptation strategy | Memory type | Reasoning mechanism | Causal inference | Uncertainty handling | Scientific utility | Limitations |
|---|---|---|---|---|---|---|---|---|---|
| Dreamer | Model-based reinforcement learning | Probabilistic latent dynamics | Learn policy from imagined rollouts | Latent recurrent model and replay | Imagination-based control | Indirect, not explicit | Probabilistic latent states | Shows how learned dynamics can support action selection | Reward-driven, limited causal explanation |
| MuZero | Learned planning model | Task-relevant latent dynamics | Search and value-policy learning | Learned representation and dynamics | Planning over learned model | Indirect, not explicit | Value uncertainty not primary | Demonstrates planning without full reconstruction | Optimized for games, not scientific explanation |
| Free-energy principle | Adaptive systems minimize variational free energy | Generative model | Perception and action reduce uncertainty | Belief states under model | Active inference | Compatible but not always explicit | Central concept | Unifies perception, action, and epistemic behavior | Broad framework, implementation-specific |
| Pearl causality | Structural causal modeling | Causal graph and structural equations | Intervene, identify, counterfactually reason | Explicit causal structure | Do-calculus and counterfactual logic | Central | Depends on assumptions and model uncertainty | Defines intervention semantics for science | Causal discovery and identification remain difficult |
| Information theory | Quantification of uncertainty and communication | Not a world model itself | Optimize information, compression, channel use | Entropy and information measures | Evidence value and representation analysis | Not causal by itself | Central | Guides experiment value and abstraction | Needs coupling to model class and goals |
| LINCS L1000 | Perturbational transcriptomics | Empirical state-response landscape | Learn signatures across perturbations | Large perturbation matrix | Response comparison and signature matching | Experimental but context-limited | Measurement and biological variability | Enables action semantics for molecular perturbations | Bulk-like signatures, context dependence, indirect measures |
| scPerturb | Single-cell perturbation compendium | Distributional cell-state response | Learn context-dependent perturbation effects | Single-cell perturbation records | Heterogeneity-aware response analysis | Perturbational evidence | Biological and sampling uncertainty | Supports state-conditioned intervention learning | Dataset heterogeneity, batch effects, sparse coverage |
| Human Cell Atlas | Comprehensive cell-state mapping | Cell-state manifold | Refine cellular taxonomy and context | Atlas-scale reference maps | State classification and trajectory context | Not primarily interventional | Measurement and annotation uncertainty | Defines state vocabulary for biology | Descriptive unless integrated with perturbations |
| Chollet intelligence | Skill-acquisition efficiency | Task abstraction, not necessarily dynamics | Generalize from limited experience | Priors and learned abstractions | Abstraction and transfer | Not primary | Implicit through task novelty | Evaluates general adaptive reasoning | Hard to operationalize across scientific domains |

Several paradigm conflicts emerge.

First, control-oriented world models and scientific models differ in their fidelity requirements. MuZero-like models may be sufficient for choosing successful actions but insufficient for explanation. Scientific reasoning often requires a model that can be inspected, challenged, and connected to mechanisms.

Second, active inference and reinforcement learning differ in their framing of action. Reinforcement learning often centers reward maximization, while active inference frames action as uncertainty reduction and preference satisfaction. Scientific experimentation often requires both: the agent may seek knowledge even when immediate reward is absent.

Third, causal models and neural world models differ in representation. Neural models scale to high-dimensional observations but may obscure causal variables. Causal models support intervention reasoning but require variables and assumptions that may be hard to identify automatically. Hybrid systems must therefore learn representations that are both predictive and causally meaningful.

Fourth, biological datasets expose a mismatch between benchmark environments and scientific systems. Games provide clean actions, fast feedback, and explicit rewards. Biology provides noisy measurements, delayed feedback, partial observability, confounding, batch effects, and ethical or practical constraints. An adaptive scientific reasoning architecture must be designed for this messier regime.

The complementary integration is nevertheless clear. Learned world models can propose possible futures. Causal models can constrain which futures correspond to interventions. Information theory can rank experiments by expected evidence. Active inference can frame the closed loop. Biological atlases and perturbation data can provide the state and transition substrate. Intelligence measures can evaluate whether the system adapts efficiently rather than memorizing.

## 8. Interdisciplinary Connections

The emerging architecture of adaptive scientific reasoning sits at the intersection of AI, neuroscience, systems biology, cybernetics, and philosophy of science.

In AI, the central contribution is the operationalization of learning and planning. Dreamer and MuZero demonstrate that action selection can be mediated by learned internal models. They also show the importance of representation: the system acts not on raw reality but on an internal state constructed for prediction and decision.

In neuroscience, the free-energy principle suggests that perception and action are coupled processes. This resonates with scientific inquiry: the scientist does not only receive data but acts to produce informative data. A laboratory experiment is an epistemic action.

In systems biology, perturbation datasets turn cells into dynamical systems under intervention. A cell is not simply an object to classify but a system that responds, adapts, and changes state. Perturbation atlases therefore invite world-model thinking.

In causal inference, intervention is formalized rather than treated informally. This is crucial for biology because the goal is not only to predict expression but to understand what controls it. Causal reasoning supplies the grammar of manipulation.

In information theory, scientific reasoning is constrained by uncertainty and limited measurement. Every experiment consumes resources and returns partial information. An adaptive agent must therefore select experiments whose expected information justifies their cost.

In cognitive science, abstraction and transfer are central. Chollet's view of intelligence as skill-acquisition efficiency highlights the difference between performance and adaptability. Scientific systems must be evaluated not only by benchmark accuracy but by their ability to construct new abstractions under limited evidence.

These fields share several transferable principles:

1. Intelligence is closed-loop: perception, action, and model revision cannot be fully separated.
2. Representation is selective: useful models preserve structure relevant to future reasoning.
3. Intervention changes the meaning of data: experimental observations have causal semantics.
4. Uncertainty is not merely noise: it guides exploration and experiment selection.
5. Memory must be structured: scientific evidence should be retrievable, auditable, and reusable.
6. Generalization depends on abstraction: systems must learn concepts that survive context shifts.

## 9. Challenges and Open Problems

### 9.1 Scalable causal representation learning

The largest conceptual gap is the integration of high-dimensional representation learning with causal interpretability. Neural world models can learn useful latent states, but those states may not correspond to causal variables. Causal models provide intervention semantics, but they typically require well-defined variables. Biological systems intensify this problem because causal structure spans genes, pathways, cell states, tissue context, and time.

### 9.2 Grounding action semantics

In many environments, the meaning of an action is learned from its effects. In biology, action semantics are state-dependent and multi-scale. A drug may affect multiple pathways; a gene perturbation may have compensatory effects; the same perturbation may differ across cell states. Grounding action semantics therefore requires transition evidence across contexts, not static labels.

### 9.3 Uncertainty calibration

Scientific agents must know when they do not know. Poorly calibrated uncertainty can lead to overconfident experiment selection, false mechanistic claims, or wasted interventions. Calibration is difficult in high-dimensional, distribution-shifted biological data. It is not enough to output probabilities; those probabilities must correspond to reliable epistemic distinctions.

### 9.4 Memory and evidence management

A scientific agent needs memory that supports both learning and accountability. Transition logs, experiment metadata, model versions, and hypothesis histories must be preserved. Pure end-to-end training can obscure the evidence trail. Future systems need memory architectures that combine statistical learning with explicit evidence records.

### 9.5 Benchmark limitations

Current AI benchmarks often reward performance on fixed distributions. Scientific reasoning requires adaptation to novel systems and sparse evidence. ARC-style benchmarks emphasize abstraction and skill acquisition, but they are still simplified compared with laboratory science. Biological datasets provide realism but often lack closed-loop interaction. Better benchmarks should combine structured intervention, limited budgets, uncertainty, causal goals, and out-of-distribution generalization.

### 9.6 Interpretability and mechanistic explanation

Scientific utility requires explanations that can be inspected and tested. A black-box predictor of perturbation response may be useful but insufficient if it cannot suggest mechanisms. Interpretable abstraction is not a cosmetic feature; it is part of scientific reasoning. The challenge is to build representations that are both expressive enough for complex data and structured enough for mechanistic inquiry.

### 9.7 Autonomous experimentation constraints

In simulated environments, agents can explore freely. In science, experiments are costly, slow, ethically constrained, and noisy. Autonomous scientific agents must therefore incorporate experimental feasibility, safety, cost, and domain constraints. Information gain alone cannot determine action selection.

### 9.8 Multi-scale dynamics

Biological reasoning spans molecular, cellular, tissue, organismal, and environmental scales. A perturbation may have immediate transcriptional effects and delayed phenotypic consequences. World models for biology must therefore handle temporal and scale-dependent structure. This remains an open problem for both AI and systems biology.

## 10. Emerging Directions and Future Research

### 10.1 Hybrid world-causal models

Future systems will likely combine neural world models with causal structure. Neural components can encode high-dimensional observations and predict transitions, while causal components can represent intervention semantics, constraints, and counterfactuals. The goal is not to replace one with the other but to align predictive representations with causal abstractions.

### 10.2 Intervention-centered foundation models

Most foundation models are trained primarily on observational data. Scientific reasoning may require foundation models organized around interventions: what was changed, in what context, with what measured response, and under what uncertainty. Perturbation datasets such as LINCS and scPerturb point in this direction, but future models will need richer metadata, causal structure, and multi-modal measurements.

### 10.3 Evidence-memory architectures

Adaptive scientific agents need memory systems that preserve transitions and hypotheses, not only embeddings. Such memory should support replay, retrieval, contradiction detection, uncertainty revision, and audit. A transition-first memory architecture would make scientific learning more transparent and reusable.

### 10.4 Active experimental design at biological scale

Information-theoretic experiment selection can be extended to biological perturbation systems. A system could choose perturbations that distinguish among pathway hypotheses, reveal cell-state vulnerabilities, or test model extrapolations. The difficulty is integrating information value with experimental cost, feasibility, and biological validity.

### 10.5 Cell atlases as state manifolds, perturbations as operators

An important future synthesis is to treat cell atlases as maps of biological state space and perturbation datasets as operators that move cells through that space. This framing makes biological reasoning more architectural: states, transitions, actions, and goals become explicit. It also enables comparisons with reinforcement learning and dynamical systems.

### 10.6 Skill-acquisition benchmarks for scientific agents

Scientific agents should be evaluated by how efficiently they learn new mechanisms under limited experiments. This extends Chollet's skill-acquisition principle into scientific domains. A benchmark might provide a new biological system, a limited intervention budget, noisy measurements, and hidden causal structure. The agent would be scored on hypothesis quality, experiment efficiency, predictive generalization, and interpretability.

### 10.7 Programmable scientific intelligence

The long-term direction is not a single monolithic model but programmable scientific intelligence: systems that can be configured with domain knowledge, measurement constraints, intervention spaces, and reasoning objectives. Such systems would combine learned models, symbolic constraints, causal assumptions, uncertainty estimation, and evidence memory. Their purpose would be to support scientific inquiry rather than replace scientific judgment.

## 11. Conclusion

The reviewed literature points toward a coherent but unfinished paradigm: adaptive scientific reasoning under uncertainty. Dreamer and MuZero show that learned world models can support action and planning. The free-energy principle frames adaptive behavior as closed-loop uncertainty management. Pearl's causal framework clarifies the semantics of intervention and counterfactual reasoning. Information theory supplies measures of uncertainty, compression, and experiment value. LINCS, scPerturb, and the Human Cell Atlas provide the biological state and transition resources that make these ideas scientifically consequential. Chollet's measure of intelligence reminds us that the ultimate test is not static performance but efficient adaptation to novelty.

The synthesis is architectural. Scientific intelligence requires state representation, transition modeling, causal abstraction, uncertainty-aware intervention selection, evidence memory, and model revision. No single reviewed framework provides all of these capabilities. Their integration defines the frontier.

The main conceptual shift is from predictive modeling to intervention-centered reasoning. In biology and other sciences, the important question is not only what pattern exists, but what change would occur under a controlled perturbation and what that change reveals about mechanism. Future systems that can answer this question reliably will need to combine the scalability of learned models with the discipline of causal inference, the economy of information theory, the adaptivity of active inference, and the abstraction standards of general intelligence evaluation.

Adaptive scientific reasoning systems should therefore be understood as experimental architectures: they observe, model, intervene, remember, abstract, and revise. Their promise lies not in automating science as a black box, but in making the cycle of hypothesis and evidence more explicit, scalable, and responsive to uncertainty.

## References

Cover, T. M., and Thomas, J. A. (2006). *Elements of Information Theory*. Wiley.

Chollet, F. (2019). On the measure of intelligence. arXiv:1911.01547.

Friston, K. (2010). The free-energy principle: a unified brain theory? *Nature Reviews Neuroscience*.

Hafner, D., Lillicrap, T., Ba, J., and Norouzi, M. (2019). Dream to control: learning behaviors by latent imagination. ICLR.

Pearl, J. (2009). *Causality*. Cambridge University Press.

Peidli, S., et al. (2024). scPerturb: harmonized single-cell perturbation data. *Nature Methods*.

Regev, A., et al. (2017). The Human Cell Atlas. *eLife*.

Schrittwieser, J., et al. (2020). Mastering Atari, Go, chess and shogi by planning with a learned model. *Nature*.

Subramanian, A., et al. (2017). A next generation connectivity map: L1000 platform and the first 1,000,000 profiles. *Cell*.
