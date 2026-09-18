# Checkpoint 1.1: D001 Candidate Identity Diagnostic

## Scope and Evidence Boundary

This diagnostic answers one question: what do the two same-name Top-50 records
represent relative to the pinned D001 canonical identity?

- Query: `ui ux prototyping guidance`
- Configured raw acquisition window: Top-50
- `web_10306` rank: 29
- `web_20486` rank: 33
- Canonical full-rank probe: ranks 60, 1048, and 128 for the three recorded
  queries; it was outside the configured Top-50 window for every query and was
  not in the fused Top-30.
- Corpus: 26,262 records from `https://github.com/oneal2000/SR-Agents` at
  commit `277fd8d2bbd7d3b81a5cf4ffa6e87e18c7906e4f`, SHA-256
  `16ee509ae5bea8c2e17167dffecd89100a7d8dfa31256c3742426758c7169b5e`.
- Existing body normalization was used exactly as implemented in
  `src/skillnudge/retrieval.py`: remove trailing newline characters, then
  SHA-256 the UTF-8 body.

Raw bodies were inspected from the corpus but are intentionally not copied into
this report. The JSON artifact contains compact structural summaries and hashes.

## 1. Pinned Canonical Identity

The canonical D001 mapping is:

| Field | Value |
| --- | --- |
| Raw corpus ID | `web_00010` |
| SQLite candidate ID | `nextlevelbuilder/ui-ux-pro-max-skill::ui-ux-pro-max` |
| Name | `ui-ux-pro-max` |
| Repository | `nextlevelbuilder/ui-ux-pro-max-skill` |
| Official path | `.claude/skills/ui-ux-pro-max/SKILL.md` |
| Official commit | `5fe9624cb844266aeae50d8a3f24c403bd456c16` |
| Source URL | `https://github.com/nextlevelbuilder/ui-ux-pro-max-skill` |
| License | `MIT` |
| Body length | 13,520 characters |
| Raw body SHA-256 | `b6627ae64792f475731d3fb0643d4521370c26dbc447fd91675e4f446aa0f3c3` |
| Normalized body SHA-256 | `b6627ae64792f475731d3fb0643d4521370c26dbc447fd91675e4f446aa0f3c3` |

The raw corpus record itself contained only the keys `content`, `description`,
`name`, and `skill_id`; its repo, source URL, source, license, and updated
timestamp were unavailable. The repo, URL, source label, and MIT license shown
above are the explicit SQLite identity override based on the pinned official
body hash. They are not raw corpus provenance. `updated_at` remains unavailable.

The record has no YAML frontmatter. Its first meaningful heading is
`# UI/UX Pro Max - Design Intelligence`. Its body covers prioritized UX rules,
the design-system and search workflow, technology stacks, output formats, and a
pre-delivery checklist.

## 2. Candidate `web_10306`

### Identity and provenance

| Field | Value |
| --- | --- |
| Candidate ID | `web_10306` |
| Name | `ui-ux-pro-max` |
| Retrieval rank | 29 in `ui ux prototyping guidance` |
| Raw BM25 score | `-11.444003597868301` |
| Body length | 1,439 characters |
| Raw body SHA-256 | `4b694efef95d109f9a0ad8bd5861cc07e619787322f580075581c69a2c396fbb` |
| Normalized body SHA-256 | `4b694efef95d109f9a0ad8bd5861cc07e619787322f580075581c69a2c396fbb` |
| Repo / source URL / source / license / updated_at | `SOURCE_PROVENANCE_UNAVAILABLE` |

Description:

> Advanced design intelligence for professional UI/UX. Use for implementing
> modern design patterns (Glassmorphism, Bento Grid), ensuring accessibility,
> and generating tailored design systems for web and mobile.

The raw corpus metadata keys are `content`, `description`, `name`, and
`skill_id`. No YAML frontmatter is present, so no frontmatter/header name or
description fields are available. The first meaningful heading is
`# UI/UX Pro Max`.

### Structural comparison with canonical

- Exact body equality: `false`.
- Normalized body equality: `false`.
- SequenceMatcher ratio after the same trailing-newline normalization:
  `0.006818637609465873`.
- Shared Markdown headings: none.
- Candidate-only headings: `Capabilities`, `1. Design System Generation`,
  `2. Design Patterns`, `3. Review & Refactor`, `Rules of Thumb`, and
  `When to Use`, in addition to its different top-level heading.
- Canonical-only structure: prioritized rule categories for accessibility,
  touch and interaction, performance, responsive layout, typography and color,
  animation, style selection, and charts; prerequisites; the stepwise design
  system/search workflow; stacks; output formats; examples; tips; and the
  pre-delivery checklist.
- Length difference: 12,081 fewer characters than canonical.

This is a compact topical UI/UX guide with a materially different structure. It
has no source evidence tying it to the canonical repository.

## 3. Candidate `web_20486`

### Identity and provenance

| Field | Value |
| --- | --- |
| Candidate ID | `web_20486` |
| Name | `ui-ux-pro-max` |
| Retrieval rank | 33 in `ui ux prototyping guidance` |
| Raw BM25 score | `-11.241779002996813` |
| Body length | 2,350 characters |
| Raw body SHA-256 | `0f5064639c8fae6d327c2c98c7952839da98f47739d290dd8f103d9a142d043d` |
| Normalized body SHA-256 | `0f5064639c8fae6d327c2c98c7952839da98f47739d290dd8f103d9a142d043d` |
| Repo / source URL / source / license / updated_at | `SOURCE_PROVENANCE_UNAVAILABLE` |

Description:

> UI/UX design intelligence. 50 styles, 21 palettes, 50 font pairings, 20
> charts, 9 stacks (React, Next.js, Vue, Svelte, SwiftUI, React Native,
> Flutter, Tailwind, shadcn/ui). Actions: plan, build, create, design,
> implement, review, fix, improve, optimize, enhance, refactor, check UI/UX
> code. Projects: website, landing page, dashboard, admin panel, e-commerce,
> SaaS, portfolio, blog, mobile app, .html, .tsx, .vue, .svelte. Elements:
> button, modal, navbar, sidebar, card, table, form, chart. Styles:
> glassmorphism, claymorphism, minimalism, brutalism, neumorphism, bento grid,
> dark mode, responsive, skeuomorphism, flat design. Topics: color palette,
> accessibility, animation, layout, typography, font pairing, spacing, hover,
> shadow, gradient. Integrations: shadcn/ui MCP for component search and
> examples.

The raw corpus metadata keys are `content`, `description`, `name`, and
`skill_id`. No YAML frontmatter is present, so no frontmatter/header name or
description fields are available. The first meaningful heading is
`# UI/UX Pro Max Skill`.

### Structural comparison with canonical

- Exact body equality: `false`.
- Normalized body equality: `false`.
- SequenceMatcher ratio after the same trailing-newline normalization:
  `0.012980466288594833`.
- Shared Markdown headings: none.
- Candidate-only structure: `Overview`, `Available Tools`, five named
  recommendation tools (`getStyleRecommendations`,
  `getTypographyRecommendations`, `getChartRecommendations`,
  `getProductRecommendations`, and `getUXGuidelines`), `Usage Rules`, and
  `Data Sources`.
- Canonical-only structure: the detailed prioritized rule categories,
  prerequisites, design-system and search workflow, stacks, output formats,
  examples, tips, and pre-delivery checklist.
- Length difference: 11,170 fewer characters than canonical.

This is a short, tool-centric document and is materially different from the
canonical body. It is topically related, but its body and source identity do not
establish that it is the pinned repository's skill or a traceable source variant.

## 4. Full-Corpus Hash Groups

The scan covered all 26,262 records using the existing normalization function.
There were 25,964 distinct normalized body hashes.

| Raw ID | Normalized hash | Hash-group members | Result |
| --- | --- | --- | --- |
| `web_00010` (canonical source record) | `b6627ae64792f475731d3fb0643d4521370c26dbc447fd91675e4f446aa0f3c3` | `web_00010` (`ui-ux-pro-max`) | Singleton |
| `web_10306` | `4b694efef95d109f9a0ad8bd5861cc07e619787322f580075581c69a2c396fbb` | `web_10306` (`ui-ux-pro-max`) | Singleton |
| `web_20486` | `0f5064639c8fae6d327c2c98c7952839da98f47739d290dd8f103d9a142d043d` | `web_20486` (`ui-ux-pro-max`) | Singleton |

There are 24 raw corpus records named `ui-ux-pro-max`, but the exact normalized
body group for each of the three inspected records is a singleton. Therefore,
same-name frequency does not provide identity evidence here.

## 5. Classification

canonical_identity: `not_retrieved`

capability_family: `retrieved`

source_lineage: `unresolved`

Preferred summary:

`CANONICAL_IDENTITY_NOT_RETRIEVED; CAPABILITY_FAMILY_RETRIEVED; PROVENANCE_UNRESOLVED`

The canonical body is present in the corpus and identity-verified by the pinned
official hash, but its canonical identity was not retrieved into the configured
Top-50 window or the fused Top-30. The capability family was retrieved: in
particular, `web_20486` has exactly the same description as canonical and
materially overlapping UI/UX recommendation capabilities. That evidence
supports capability-family similarity, not canonical source identity.

The body hash and structure of `web_20486` diverge from canonical, and its raw
source provenance is unavailable. These facts leave source lineage unresolved.
This diagnostic does not claim that `web_20486` is a verified fork or mirror.

## 6. Checkpoint 2 Interpretation

Checkpoint 2 should preserve identity, provenance, and capability similarity as
separate signals. Future Evidence Hydration or Judge work may need to preserve
this distinction, but this amendment designs no new architecture and does not
justify query changes, embeddings, rerankers, deduplication rules, or runtime
changes.
