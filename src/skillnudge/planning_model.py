"""Small provider boundary for structured planning responses."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field
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
        return cls(
            api_key=os.environ.get("SKILLNUDGE_MODEL_API_KEY") or os.environ.get("OPENAI_API_KEY"),
            base_url=os.environ.get("SKILLNUDGE_MODEL_BASE_URL", "https://api.openai.com/v1"),
            model_name=os.environ.get("SKILLNUDGE_MODEL", ""),
            timeout_seconds=float(os.environ.get("SKILLNUDGE_MODEL_TIMEOUT_SECONDS", "60")),
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
