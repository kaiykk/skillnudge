# Local Provider Configuration

Checkpoint 2 live smoke tests use one OpenAI-compatible structured-output
provider. Configure it in the local-only file:

```text
config/provider.local.env
```

The file is intentionally ignored by Git. Fill these values locally:

```dotenv
SKILLNUDGE_MODEL=your-model-name
SKILLNUDGE_MODEL_API_KEY=your-api-key
SKILLNUDGE_MODEL_BASE_URL=https://api.openai.com/v1
SKILLNUDGE_MODEL_TIMEOUT_SECONDS=60
```

`SKILLNUDGE_MODEL_BASE_URL` is optional when using the default OpenAI endpoint.
Environment variables take precedence over the local file. The provider
adapter reads this file with the standard library; no dotenv package is
required. The adapter uses only `SKILLNUDGE_MODEL_API_KEY` for authentication;
it never falls back to `OPENAI_API_KEY`, including when the configured base URL
is a third-party OpenAI-compatible endpoint.

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
