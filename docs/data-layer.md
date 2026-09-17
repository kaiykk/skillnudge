# Data Layer

## Status

- `[FROZEN]` Candidate provenance and cache level must remain visible.
- `[FROZEN]` A live result must not automatically become trusted corpus data.
- `[WORKING HYPOTHESIS]` Three lifecycle levels are enough for V0 design and
  can later be collapsed if their operational cost is not justified.
- `[FUTURE]` Stable snapshot publishing and automated freshness management.

## Candidate Lifecycle

The local corpus is a default source, not the whole world. A Candidate Pool may
combine stable local data, authoritative catalogs, live discovery, a user
provided URL or repository, and locally installed Skills or Plugins.

```text
Live candidate
      ↓
L2 Current Run / Ephemeral
      ↓ validation
L1 Validated Cache
      ↓ repeated provenance and freshness checks
L0 Stable Catalog
```

The reverse direction is not automatic. A candidate may remain ephemeral when
its source, license, body, compatibility, or identity cannot be verified.

## L0 Stable Catalog

An intentionally selected snapshot with a known source, version or commit,
license, retrieval time, and normalized identity. It is suitable for repeatable
local retrieval.

## L1 Validated Cache

A previously inspected candidate whose evidence is useful but whose freshness
or source stability still requires management. It can reduce repeated fetches
without pretending to be a permanent catalog.

## L2 Current Run / Ephemeral

A candidate discovered for one run. It is available to the current Judge and
trace, but must not silently alter the trusted corpus.

## Normalized Candidate Concept

All sources should eventually map to a common conceptual record:

```text
candidate_id
type
name
description
source
source_url
repo
body_or_readme
compatibility
license
updated_at
trust_signals
provenance
content_hash
cache_level
```

This is deliberately not a frozen implementation schema. It defines the
information needed to compare candidates and explain evidence boundaries.

## Retrieval and Storage Boundary

Large bodies should remain on disk or in a durable indexed store. The V0
direction is:

```text
Disk corpus
→ lightweight SQLite index
→ per-query retrieval
→ small candidate pool
→ hydrate full bodies only for the pool
```

The design must not require loading a 10k, 50k, or 100k-plus corpus fully into
Python memory.

## Provenance Rules

Every candidate entering a pool should retain:

- canonical identity;
- source URL or local path;
- version, commit, or retrieved time;
- evidence location;
- license state;
- compatibility uncertainty;
- cache level;
- content hash where available.

Source claims, README claims, model inferences, and directly observed behavior
must remain distinguishable.
