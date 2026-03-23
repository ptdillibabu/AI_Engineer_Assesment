## How I Designed the Agent Prompts and Why

### Overview

The  each agent (Proposer, Critic, Summarizer) has strictly defined responsibilities, behavioral constraints, and output schemas. This is deliberate: it reduces ambiguity, prevents role collapse, and enables reliable termination and summarization.

The prompts are not generic instructions; they are contractual specifications. Each agent has its own prompts content:

- Clear role definition
- Behavioral rules
- Allowed actions
- Mandatory output formats (JSON-only)
- Round count to know which round it is performing

---

### Proposer Prompt Design

#### Purpose

The Proposer’s role is to transform a vague feature request into a concrete, defensible proposal.

#### Key Design Choices

1. **Structured Output from Round 1**
   - The initial proposer prompt forces:
     - Included scope
     - Excluded scope
     - Assumptions with confidence levels
     - Measurable success criteria

2. **Defense-Oriented Behavior after reciving the challenge response**
   - The behavioral rules state that the proposer should not agree with all criticism immediately.
   - This is critical; otherwise the proposer collapses into compliance and deliberation loses value.
   - The agent must defend positions unless convincingly challenged, simulating a real technical owner.

3. **Round-Based Evolution**
   - The proposer response prompt requires the agent to:
     - Respond to specific challenge IDs
     - Choose between `DEFEND`, `REVISE`, or `CONCEDE`
   - This produces a traceable reasoning chain across rounds.

4. **JSON-Only Constraint**
   - Enforced via retry prompts.
   - This ensures:
     - Machine-parseable deliberation
     - Downstream summarization reliability
     - Easy persistence and replay

---

### Critic Prompt Design

#### Purpose

The Critic exists to increase proposal quality, not to block progress.

#### Key Design Choices

1. **Challenge Categories**
   - Challenges must fall into one of:
     - ASSUMPTION
     - SCOPE_RISK
     - MISSING_CONSTRAINT
     - AMBIGUITY
     - OPERATIONAL
     - SECURITY
   - This prevents vague feedback like “this is unclear” and forces actionable critique.

2. **Minimum Rounds Rule**
   - The critic is forbidden from signaling satisfaction in round 1.
   - This guarantees at least one full challenge–response cycle.

3. **Acknowledgement of Resolution**
   - When a challenge is adequately addressed, the critic must acknowledge it.
   - This avoids adversarial looping and encourages convergence.

4. **Controlled Termination Authority**
   - Satisfaction can only be signaled when:
     - Minimum rounds completed
     - Scope is implementable
     - Remaining issues require human input or discussion
     - Proposal is now robust enough without any confusion
     - This ties termination to proposal quality, not round count alone.

### Summarizer Prompt Design

#### Purpose

The Summarizer converts deliberation into a decision artifact

#### Key Design Choices

1. **Focus on Tension**
   - The summarizer is instructed to preserve the tension and disagreements in the dialogue.

2. **Final Scope, Not Last Proposal**
   - The summarizer must extract the agreed scope, not blindly repeat the final proposer output.

3. **Explicit Open Questions**
   - Only genuine, stakeholder-dependent questions are allowed.
   - This cleanly hands off to human governance.

4. **Termination Reason as Input**
   - The summarizer receives the termination reason, making the decision traceable.


## How Termination Works and Alternatives Considered

### Current Termination Strategy

Termination is not time-based alone; it is quality-aware and multi-signal driven.

1. **Max Round Limit (6–8 Rounds)**
   - The system enforces a hard cap on rounds and this was determined experimentally with multiple times and input.
   - A minimum of 2 rounds is enforced to avoid shallow outcomes.

2. **Satisfaction Signal from Critic agent**
   - The critic may signal satisfaction only when genuinely satisfied with proposals from proposal agent (Absolute disagreement delta  with Critic confidence and Proposer confidence).
   - The prompt forbids signaling satisfaction merely to end the conversation.

3. **Repeated / Subset Challenge Detection**
   - The system checks whether new challenges are subsets of previous challenges and the current implementation uses character-level overlap (around 50 characters).


### Why the Current Design Works

- Combines hard limits (max rounds) with soft semantic signals (satisfaction, repetition).
- Ensures convergence without sacrificing rigor.
- Aligns with enterprise governance expectations.

---

## One Thing I Would Do Differently with More Time

If given more time, I would evolve the system in three key ways:

### 1. Replace Character-Level Matching with Semantic / Hybrid Search

- Introduce embedding-based similarity:
  - Store historical challenges in a vector database.
  - Compare new challenges using cosine similarity.
- Use hybrid search (lexical + semantic) for robustness.

**Benefit**

- More accurate loop detection
- Reduced false negatives

---

### 2. Ground Proposals and Critiques with Historical Data 

- Ground both Proposer and Critic using:
  - Past feature decisions
  - Prior critiques
  - Historical success/failure patterns
- Inject this context via retrieval-augmented prompting or RAG Agent (vector DB).

**Benefit**

- More realistic proposals
- Fewer repeated mistakes
- Enterprise memory across deliberations

---

### 3. Introduce Human-in-the-Loop Before Final Termination

- Add an optional human checkpoint:
  - When the critic is satisfied but open questions exist
  - Allow a human reviewer to:
    - Approve termination
    - Extend deliberation
    - Inject constraints

**Benefit**

- Stronger governance
- Higher trust in critical decisions
- Better alignment with regulated environments

---


This assignment demonstrates system-level thinking:

- Governance-aware agent design
- Deterministic orchestration
- Scalable termination logic
- Enterprise-grade extensibility

With more time, I would focus on memory, grounding, and human alignment, but the current design already establishes a strong, production-ready foundation.
'''
