"""Small provider boundary for structured planning responses."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Protocol


class ModelProviderError(RuntimeError):
    """A live provider failed without exposing provider response contents."""


class LiveModelProviderUnavailable(ModelProviderError):
    """No configured live model credential/provider is available."""

    def __init__(self) -> None:
        super().__init__("LIVE_MODEL_PROVIDER_UNAVAILABLE")


class PlanningModel(Protocol):
    provider_name: str
    model_name: str

    def generate_structured(self, *, stage: str, prompt: str, prompt_version: str) -> Any:
        """Return a JSON object or JSON text for one planning stage."""


LOCAL_PROVIDER_ENV_PATH = Path(__file__).resolve().parents[2] / "config" / "provider.local.env"
_LOCAL_PROVIDER_KEYS = {
    "SKILLNUDGE_MODEL",
    "SKILLNUDGE_MODEL_API_KEY",
    "SKILLNUDGE_MODEL_BASE_URL",
    "SKILLNUDGE_MODEL_TIMEOUT_SECONDS",
}


def _read_local_provider_env(path: Path | None = None) -> dict[str, str]:
    """Read the ignored local provider file without adding a dotenv dependency."""

    path = path or LOCAL_PROVIDER_ENV_PATH
    if not path.is_file():
        return {}
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        if "=" not in line:
            continue
        key, value = (part.strip() for part in line.split("=", 1))
        if key not in _LOCAL_PROVIDER_KEYS:
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        values[key] = value
    return values


@dataclass(frozen=True)
class OpenAICompatibleModel:
    """A minimal Chat Completions adapter using only the Python standard library."""

    api_key: str | None = None
    base_url: str = "https://api.openai.com/v1"
    model_name: str = ""
    timeout_seconds: float = 60.0
    provider_name: str = "openai-compatible"

    @classmethod
    def from_environment(cls) -> "OpenAICompatibleModel":
        local_env = _read_local_provider_env()

        def setting(name: str, default: str = "") -> str:
            return os.environ.get(name) or local_env.get(name, default)

        return cls(
            api_key=setting("SKILLNUDGE_MODEL_API_KEY"),
            base_url=setting("SKILLNUDGE_MODEL_BASE_URL", "https://api.openai.com/v1"),
            model_name=setting("SKILLNUDGE_MODEL"),
            timeout_seconds=float(setting("SKILLNUDGE_MODEL_TIMEOUT_SECONDS", "60")),
        )

    def generate_structured(self, *, stage: str, prompt: str, prompt_version: str) -> Any:
        if not self.api_key or not self.model_name:
            raise LiveModelProviderUnavailable()
        request_body = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": "Return only a valid JSON object matching the requested contract.",
                },
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
        }
        request = urllib.request.Request(
            url=self.base_url.rstrip("/") + "/chat/completions",
            data=json.dumps(request_body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            raise ModelProviderError(f"MODEL_PROVIDER_HTTP_{error.code}") from error
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, UnicodeDecodeError) as error:
            raise ModelProviderError("MODEL_PROVIDER_REQUEST_FAILED") from error

        try:
            content = payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as error:
            raise ModelProviderError("MODEL_PROVIDER_INVALID_RESPONSE") from error
        if isinstance(content, list):
            content = "".join(
                item.get("text", "") for item in content if isinstance(item, Mapping)
            )
        if not isinstance(content, (str, Mapping)):
            raise ModelProviderError("MODEL_PROVIDER_INVALID_CONTENT")
        return content


@dataclass
class DeterministicFakeModel:
    """Injected test adapter; it is never selected by the live CLI."""

    responses: list[Any]
    provider_name: str = "deterministic-fake"
    model_name: str = "fixture-model"
    calls: list[dict[str, str]] = field(default_factory=list)

    def generate_structured(self, *, stage: str, prompt: str, prompt_version: str) -> Any:
        self.calls.append({"stage": stage, "prompt_version": prompt_version})
        if not self.responses:
            raise ModelProviderError("DETERMINISTIC_FAKE_RESPONSE_EXHAUSTED")
        return self.responses.pop(0)
