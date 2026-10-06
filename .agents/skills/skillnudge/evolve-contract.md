# Native EVOLVE Contract

EVOLVE Mode is candidate-only. The Host must provide one `TEST` Review result
whose primary attribution is `capability_candidate`, observable Review
evidence, a source `native.capability-artifact.v0`, and a host-proposed
instruction candidate. A linked `INTERVENTION_ABLATION` Validate result may be
provided as optional evidence strengthening; it is not universally required
and does not need to be `HELPS` merely to admit a candidate.

The command checks Review evidence, optional Validate linkage, and the
source/candidate/hash lineage. It emits a non-active
`lifecycle_status: CANDIDATE` with `decision_state.authority: HUMAN_REQUIRED`.
It never installs, mutates, or promotes the candidate. `CAPABILITY_REVISION`
must compare the source and candidate artifacts before the Human Principal
makes a lifecycle decision.
