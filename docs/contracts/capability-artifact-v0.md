# Capability Artifact v0

`native.capability-artifact.v0` is the smallest immutable identity envelope
used by the bounded EVOLVE MVP. It supports only one artifact type:
`instruction`.

```yaml
schema_version: native.capability-artifact.v0
capability_id: stable identifier
version: v1
type: instruction
exact_content: exact UTF-8 instruction text
sha256: SHA-256(exact_content UTF-8 bytes)
```

The `capability_id` remains stable across versions. `version` and `sha256`
must change when the artifact changes. SkillNudge validates the bytes and
returns a normalized immutable record; it does not install, mutate, or infer
an ontology from the artifact.

This contract intentionally excludes Skill packages, plugins, tools, memory,
families, registries, taxonomies, and multi-file manifests.
