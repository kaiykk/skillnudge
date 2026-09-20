# Local Provider Configuration

Phase 1 dogfood uses the official DeepSeek structured-output API. Configure it
in the local-only file:

```text
config/provider.local.env
```

The file is intentionally ignored by Git. Fill these values locally:

```dotenv
DEEPSEEK_API_KEY=your-deepseek-api-key
SKILLNUDGE_MODEL=deepseek-flash
SKILLNUDGE_MODEL_BASE_URL=https://api.deepseek.com
SKILLNUDGE_MODEL_TIMEOUT_SECONDS=60
SKILLNUDGE_MODEL_TEMPERATURE=0
SKILLNUDGE_MODEL_TOP_P=1
SKILLNUDGE_MODEL_SEED=
SKILLNUDGE_MODEL_MAX_OUTPUT_TOKENS=1200
SKILLNUDGE_MODEL_REASONING_EFFORT=
```

`SKILLNUDGE_MODEL_BASE_URL` defaults to the official DeepSeek endpoint and
should not include `/v1` for this project. Environment variables take
precedence over the local file. The adapter reads this file with the standard
library; no dotenv package is required. `DEEPSEEK_API_KEY` is the supported
authentication variable. The legacy `SKILLNUDGE_MODEL_API_KEY` variable remains
accepted only as a compatibility override and is not documented as the
supported dogfood path.

Every planning request uses JSON Output with `response_format.type=json_object`
and explicitly sends `thinking.type=disabled`. The adapter persists only safe
provider metadata such as provider identity, endpoint identity, requested and
observed model names, and token usage. It never persists `reasoning_content`.

Never put a real key in `provider.local.env.example`, source files, tests,
review packets, chat messages, or committed files. Do not upload
`config/provider.local.env`.

## Mandatory Publish Gate

Before every commit intended for GitHub push, run:

```bash
./scripts/check_publish_gate.sh
```

The gate fails if a protected `.env`, local provider, secret, or credential
configuration path is tracked or staged. It also verifies that every existing
`config/*.local.env` file is ignored. A passing gate is required before every
push; it does not replace normal tests or review.

This clone is configured with `core.hooksPath=.githooks`, so Git also runs the
same gate automatically from `.githooks/pre-push` before each `git push`. After
cloning the repository elsewhere, enable the versioned hook once:

```bash
git config core.hooksPath .githooks
```

After the gate passes, run the relevant validation command and inspect:

```bash
git status --short
git diff --cached --name-only
```

Only then push to GitHub.
