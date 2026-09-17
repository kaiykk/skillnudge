# Architecture

## Status

- `[FROZEN]` V0 is a layered, trace-first Intervention Advisor.
- `[FROZEN]` Local retrieval and conditional live discovery converge into a
  Candidate Pool before evidence hydration and judgement.
- `[WORKING HYPOTHESIS]` These boundaries are sufficient for a lightweight
  first implementation.
- `[FUTURE]` Semantic retrieval, large-scale source adapters, and lifecycle
  automation.

The diagrams describe design boundaries, not implemented services. SkillNudge
does not require a microservice architecture.

## Product-Level Architecture

```mermaid
flowchart TD
    U[User] --> A[SkillNudge Advise]
    A --> C[Capability Understanding]
    C --> I[Intervention Planning]
    I --> AC[Candidate Acquisition]
    AC --> E[Evidence]
    E --> J[Judgement]
    J --> F[Advice]

    AC --> S[Skills]
    AC --> P[Plugins]
    AC --> T[Tools]
    AC --> R[Companion Resources]
```

## V0 Runtime

```mermaid
flowchart TD
    R0[Raw User Request] --> R1[Intake / Context]
    R1 --> R2[Capability Framing]
    R2 --> R3[Intervention Planning]
    R3 --> R4[Query Planning]
    R4 --> R5[Candidate Acquisition]
    R5 --> LR[Local Retrieval]
    R5 --> LD[Conditional Live Discovery]
    LR --> CP[Candidate Pool]
    LD --> CP
    CP --> R6[Evidence Hydration]
    R6 --> R7[Candidate Judgement]
    R7 --> R8[Final Advice]

    TR[Trace] -. crosses .-> R1
    TR -. crosses .-> R2
    TR -. crosses .-> R3
    TR -. crosses .-> R4
    TR -. crosses .-> R5
    TR -. crosses .-> R6
    TR -. crosses .-> R7
    TR -. crosses .-> R8
```

## Candidate Acquisition Decision Tree

```mermaid
flowchart TD
    S[Start] --> L[Local Search]
    L --> Q{Enough evidence?}
    Q -->|YES| H[Evidence Hydration]
    Q -->|NO| W{Which intervention surface?}
    W -->|Skill| SS[Skill registry / search]
    W -->|Plugin| PM[Official marketplace refresh]
    W -->|Tool| TW[Targeted live web discovery]
    W -->|Resource| RR[Targeted resource lookup]
    SS --> N[Normalize]
    PM --> N
    TW --> N
    RR --> N
    N --> D[Deduplicate]
    D --> C[Cache at the appropriate level]
    C --> P[Candidate Pool]
    H --> P
```

## Boundary Notes

- Capability Framing happens before candidate search.
- Candidate Acquisition constructs a pool; it does not give final advice.
- Evidence Hydration turns shallow search results into judgeable evidence.
- Candidate Judgement estimates intervention utility, not just text similarity.
- Final Advice is intentionally small and can be `no_intervention`.
- Trace artifacts are explicit and reviewable; private chain-of-thought is not
  part of the design.
