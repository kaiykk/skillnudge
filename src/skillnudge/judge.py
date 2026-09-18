"""Checkpoint 4 Candidate Judgement and minimal Final Advice runtime."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from .planning_model import PlanningModel


JUDGE_PROMPT_VERSION = "judge.candidate.v0"
FINAL_ADVICE_PROMPT_VERSION = "final_advice.v0"
JUDGE_DISPOSITIONS = frozenset(
    {"viable", "companion", "defer", "reject", "insufficient_evidence"}
)
FINAL_ADVICE_STATUSES = frozenset(
    {
        "recommendation",
        "no_intervention",
        "insufficient_evidence",
        "needs_clarification",
        "source_error",
    }
)
EVIDENCE_REFS = frozenset(
    {
        "candidate.description",
        "candidate.body",
        "retrieval.query_hits",
        "identity.provenance_status",
        "identity.evidence_gaps",
        "identity.repo",
        "identity.source_url",
        "identity.license",
        "identity.updated_at",
        "corpus.identity",
        "corpus.version",
    }
)
UNSUPPORTED_INTEGRATION_UNCERTAINTY = (
    "The planned Integration candidate surface was not evaluated in Week 1."
)


class JudgeValidationError(ValueError):
    """Raised when a Judge or Final Advice response violates its contract."""

    def __init__(self, contract_name: str, errors: list[str]):
        self.contract_name = contract_name
        self.errors = errors
        super().__init__(f"{contract_name} validation failed: {'; '.join(errors)}")


class JudgeStageError(RuntimeError):
    """Raised when a structured Judge or Advice response remains invalid."""


def _is_mapping(value: Any) -> bool:
    return isinstance(value, Mapping)


def _required_string(value: Mapping[str, Any], key: str, errors: list[str]) -> None:
    if key not in value:
        errors.append(f"missing required field: {key}")
    elif not isinstance(value[key], str) or not value[key].strip():
        errors.append(f"{key} must be a non-empty string")


def _string_list(value: Mapping[str, Any], key: str, errors: list[str]) -> None:
    items = value.get(key)
    if not isinstance(items, list):
        errors.append(f"{key} must be a list")
        return
    if any(not isinstance(item, str) or not item.strip() for item in items):
        errors.append(f"{key} must contain only non-empty strings")


def _enum(
    value: Mapping[str, Any],
    key: str,
    allowed: set[str] | frozenset[str],
    errors: list[str],
) -> None:
    if key not in value:
        errors.append(f"missing required field: {key}")
    elif value[key] not in allowed:
        errors.append(f"{key} must be one of {sorted(allowed)}")


def _unexpected(
    value: Mapping[str, Any],
    allowed: set[str] | frozenset[str],
    errors: list[str],
) -> None:
    unexpected = sorted(set(value) - allowed)
    if unexpected:
        errors.append(f"unexpected fields: {unexpected}")


def validate_judge_hard_gates(judgement: Mapping[str, Any]) -> None:
    """Reject disposition values that contradict the frozen hard gates."""

    assessment = judgement["assessment"]
    practical = assessment["practical_fit"]
    evidence_status = judgement["evidence_status"]
    disposition = judgement["disposition"]
    errors: list[str] = []
    if evidence_status == "insufficient" and disposition != "insufficient_evidence":
        errors.append("evidence_status=insufficient requires disposition=insufficient_evidence")
    if assessment["capability_fit"] == "none" and disposition != "reject":
        errors.append("capability_fit=none requires disposition=reject")
    if practical["compatibility"] == "incompatible" and disposition != "reject":
        errors.append("compatibility=incompatible requires disposition=reject")
    if practical["constraint_fit"] == "violates" and disposition != "reject":
        errors.append("constraint_fit=violates requires disposition=reject")
    if assessment["stage_fit"] == "later" and disposition != "defer":
        errors.append("stage_fit=later requires disposition=defer")
    if errors:
        raise JudgeValidationError("CandidateJudgement", errors)


def validate_candidate_judgement(value: Any) -> dict[str, Any]:
    """Validate the frozen CandidateJudgement schema without adding scores."""

    errors: list[str] = []
    if not _is_mapping(value):
        raise JudgeValidationError("CandidateJudgement", ["response must be a JSON object"])
    judgement = dict(value)
    _required_string(judgement, "candidate_id", errors)
    _enum(judgement, "evidence_status", {"sufficient", "partial", "insufficient"}, errors)

    assessment = judgement.get("assessment")
    if not _is_mapping(assessment):
        errors.append("assessment must be an object")
        assessment_data: Mapping[str, Any] = {}
    else:
        assessment_data = assessment
        _enum(assessment_data, "capability_fit", {"strong", "partial", "weak", "none"}, errors)
        _enum(assessment_data, "stage_fit", {"now", "later", "wrong_context", "unclear"}, errors)
        _enum(assessment_data, "mechanism_fit", {"strong", "partial", "weak"}, errors)
        _enum(assessment_data, "expected_gain", {"high", "medium", "low", "unknown"}, errors)
        practical = assessment_data.get("practical_fit")
        if not _is_mapping(practical):
            errors.append("assessment.practical_fit must be an object")
        else:
            _enum(
                practical,
                "compatibility",
                {"compatible", "conditional", "incompatible", "unknown"},
                errors,
            )
            _enum(
                practical,
                "constraint_fit",
                {"satisfies", "partial", "violates", "unknown"},
                errors,
            )
            _enum(practical, "friction", {"low", "medium", "high", "unknown"}, errors)
            _unexpected(practical, {"compatibility", "constraint_fit", "friction"}, errors)
        _enum(assessment_data, "trust", {"strong", "adequate", "weak", "unknown"}, errors)
        _unexpected(
            assessment_data,
            {
                "capability_fit",
                "stage_fit",
                "mechanism_fit",
                "expected_gain",
                "practical_fit",
                "trust",
            },
            errors,
        )

    for key in ("matched_capabilities", "gaps_or_mismatches", "evidence"):
        if key not in judgement:
            errors.append(f"missing required field: {key}")
        elif key == "evidence":
            refs = judgement[key]
            if not isinstance(refs, list) or any(
                not isinstance(ref, str) or not ref.strip() for ref in refs
            ):
                errors.append("evidence must be a list of non-empty strings")
        else:
            _string_list(judgement, key, errors)

    _enum(judgement, "disposition", JUDGE_DISPOSITIONS, errors)
    _required_string(judgement, "reason", errors)
    _unexpected(
        judgement,
        {
            "candidate_id",
            "evidence_status",
            "assessment",
            "matched_capabilities",
            "gaps_or_mismatches",
            "evidence",
            "disposition",
            "reason",
        },
        errors,
    )
    if errors:
        raise JudgeValidationError("CandidateJudgement", errors)
    validate_judge_hard_gates(judgement)
    return judgement


def _normalize_advice_ref(value: Any, field: str, errors: list[str]) -> dict[str, Any] | None:
    if value is None:
        return None
    if not _is_mapping(value):
        errors.append(f"{field} must be an object or null")
        return None
    data = dict(value)
    _required_string(data, "candidate_id", errors)
    _required_string(data, "reason", errors)
    if "name" in data and data["name"] is not None and (
        not isinstance(data["name"], str) or not data["name"].strip()
    ):
        errors.append(f"{field}.name must be a non-empty string or null")
    _unexpected(data, {"candidate_id", "name", "reason"}, errors)
    return data


def validate_final_advice(value: Any) -> dict[str, Any]:
    """Validate the existing minimal FinalAdvice shape."""

    errors: list[str] = []
    if not _is_mapping(value):
        raise JudgeValidationError("FinalAdvice", ["response must be a JSON object"])
    advice = dict(value)
    _enum(advice, "status", FINAL_ADVICE_STATUSES, errors)
    refs: dict[str, dict[str, Any] | None] = {}
    for key in ("primary", "supporting", "companion"):
        refs[key] = _normalize_advice_ref(advice.get(key), key, errors)
    deferred = advice.get("deferred", [])
    if not isinstance(deferred, list):
        errors.append("deferred must be a list")
        deferred = []
    normalized_deferred: list[dict[str, Any]] = []
    for index, item in enumerate(deferred):
        normalized = _normalize_advice_ref(item, f"deferred[{index}]", errors)
        if normalized is not None:
            normalized_deferred.append(normalized)
    uncertainties = advice.get("uncertainties", [])
    if not isinstance(uncertainties, list) or any(
        not isinstance(item, str) or not item.strip() for item in uncertainties
    ):
        errors.append("uncertainties must be a list of non-empty strings")
        uncertainties = []
    _unexpected(
        advice,
        {"status", "primary", "supporting", "companion", "deferred", "uncertainties"},
        errors,
    )
    if errors:
        raise JudgeValidationError("FinalAdvice", errors)
    result = {
        "status": advice["status"],
        "primary": refs["primary"],
        "supporting": refs["supporting"],
        "companion": refs["companion"],
        "deferred": normalized_deferred,
        "uncertainties": list(uncertainties),
    }
    if result["supporting"] is not None and result["primary"] is None:
        raise JudgeValidationError(
            "FinalAdvice",
            ["supporting requires a primary recommendation"],
        )
    if result["status"] == "recommendation" and result["primary"] is None:
        raise JudgeValidationError(
            "FinalAdvice",
            ["status=recommendation requires a primary recommendation"],
        )
    if result["status"] != "recommendation" and any(
        result[key] is not None for key in ("primary", "supporting", "companion")
    ):
        raise JudgeValidationError(
            "FinalAdvice",
            ["non-recommendation status cannot contain main recommendations"],
        )
    return result


def validate_final_advice_against_judgements(
    advice: Mapping[str, Any],
    judgements: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Ensure Advice only selects judged candidates and respects dispositions."""

    normalized = validate_final_advice(advice)
    by_id = {str(item["candidate_id"]): item for item in judgements}
    selected: list[tuple[str, Mapping[str, Any]]] = []
    for field in ("primary", "supporting", "companion"):
        ref = normalized[field]
        if ref is None:
            continue
        candidate_id = ref["candidate_id"]
        if candidate_id not in by_id:
            raise JudgeValidationError(
                "FinalAdvice",
                [f"{field} references unjudged candidate: {candidate_id}"],
            )
        selected.append((field, by_id[candidate_id]))
    for ref in normalized["deferred"]:
        candidate_id = ref["candidate_id"]
        if candidate_id not in by_id:
            raise JudgeValidationError(
                "FinalAdvice",
                [f"deferred references unjudged candidate: {candidate_id}"],
            )

    ids = [ref["candidate_id"] for field, _ in selected for ref in [normalized[field]]]
    if len(ids) != len(set(ids)):
        raise JudgeValidationError("FinalAdvice", ["a candidate cannot occupy multiple advice slots"])
    names: dict[str, str] = {}
    for field, judgement in selected:
        ref = normalized[field]
        assert ref is not None
        disposition = judgement["disposition"]
        expected = "companion" if field == "companion" else "viable"
        if disposition != expected:
            raise JudgeValidationError(
                "FinalAdvice",
                [f"{field} candidate must have disposition={expected}"],
            )
        name = str(ref.get("name") or "").strip().casefold()
        if name and name in names:
            raise JudgeValidationError(
                "FinalAdvice",
                [
                    "same-name candidates cannot be selected together by default: "
                    f"{names[name]} and {ref['candidate_id']}"
                ],
            )
        if name:
            names[name] = ref["candidate_id"]
    for ref in normalized["deferred"]:
        judgement = by_id[ref["candidate_id"]]
        if judgement["disposition"] != "defer":
            raise JudgeValidationError(
                "FinalAdvice",
                ["deferred candidate must have disposition=defer"],
            )
    return normalized


def judge_candidate_prompt(
    capability_contract: Mapping[str, Any],
    intervention_plan: Mapping[str, Any],
    evidence_pack: Mapping[str, Any],
) -> str:
    """Build a single-candidate prompt without exposing other candidates."""

    return f"""You are the Candidate Judgement stage of SkillNudge.

Judge exactly one hydrated candidate. Do not search, retrieve another candidate,
regenerate the capability contract, modify the intervention plan, or infer
provenance. Return only one JSON object matching the frozen CandidateJudgement
schema.

The core question is whether this intervention is likely to improve the user's
next trajectory compared with doing nothing, enough to justify friction,
uncertainty, and risk. Retrieval rank is evidence context only. It must not
determine disposition or any judgement dimension.

Keep these dimensions separate:
capability_fit != expected_gain != trust != friction.
Unknown provenance may coexist with strong capability fit and sufficient
evidence when the full body supports assessment. Unknown provenance normally
means trust=unknown unless explicit trust evidence exists. Never invent stars,
authors, maintenance, compatibility, license, adoption, or citations.

Use these hard gates:
- evidence_status=insufficient -> disposition=insufficient_evidence
- capability_fit=none -> disposition=reject
- compatibility=incompatible -> disposition=reject
- constraint_fit=violates -> disposition=reject
- stage_fit=later -> disposition=defer
- auxiliary-only value may be disposition=companion
- otherwise disposition may be viable

Use only these evidence references when citing evidence:
{json.dumps(sorted(EVIDENCE_REFS), ensure_ascii=False)}
Do not copy long body passages into the judgement. Do not add numeric scores,
primary/supporting fields, or extra JSON fields.

CapabilityContract:
{json.dumps(capability_contract, ensure_ascii=False, indent=2)}

InterventionPlan:
{json.dumps(intervention_plan, ensure_ascii=False, indent=2)}

EvidencePack:
{json.dumps(evidence_pack, ensure_ascii=False, indent=2)}

Frozen CandidateJudgement shape:
{{
  "candidate_id": "string",
  "evidence_status": "sufficient | partial | insufficient",
  "assessment": {{
    "capability_fit": "strong | partial | weak | none",
    "stage_fit": "now | later | wrong_context | unclear",
    "mechanism_fit": "strong | partial | weak",
    "expected_gain": "high | medium | low | unknown",
    "practical_fit": {{
      "compatibility": "compatible | conditional | incompatible | unknown",
      "constraint_fit": "satisfies | partial | violates | unknown",
      "friction": "low | medium | high | unknown"
    }},
    "trust": "strong | adequate | weak | unknown"
  }},
  "matched_capabilities": ["string"],
  "gaps_or_mismatches": ["string"],
  "evidence": ["stable EvidencePack reference"],
  "disposition": "viable | companion | defer | reject | insufficient_evidence",
  "reason": "string"
}}
"""


def final_advice_prompt(
    capability_contract: Mapping[str, Any],
    intervention_plan: Mapping[str, Any],
    acquisition: Mapping[str, Any] | None,
    judgements: Sequence[Mapping[str, Any]],
) -> str:
    """Build Final Advice from judgements, never from retrieval rank directly."""

    return f"""You are the Final Advice stage of SkillNudge.

Choose the smallest useful intervention set from the CandidateJudgements below.
Do not search, retrieve, re-judge, or inspect hidden candidate text. Do not
sort by RRF rank, BM25 score, body length, or candidate name. Candidate
judgement disposition is the source of truth.

Rules:
- remove reject and insufficient_evidence from recommendation choices;
- choose at most one primary and at most one supporting recommendation;
- include at most one companion when it adds distinct support value;
- mention deferred candidates only when the timing distinction is useful;
- zero recommendations is valid;
- do not recommend two same-name or materially redundant candidates by default;
- if the acquisition artifact contains an unsupported family warning, preserve
  that gap in uncertainties and do not imply that the acquired family beat the
  unevaluated family.

Return only this JSON shape:
{{
  "status": "recommendation | no_intervention | insufficient_evidence | needs_clarification | source_error",
  "primary": {{"candidate_id": "string", "name": "string", "reason": "string"}} or null,
  "supporting": {{"candidate_id": "string", "name": "string", "reason": "string"}} or null,
  "companion": {{"candidate_id": "string", "name": "string", "reason": "string"}} or null,
  "deferred": [{{"candidate_id": "string", "name": "string", "reason": "string"}}],
  "uncertainties": ["string"]
}}

CapabilityContract:
{json.dumps(capability_contract, ensure_ascii=False, indent=2)}

InterventionPlan:
{json.dumps(intervention_plan, ensure_ascii=False, indent=2)}

Acquisition summary:
{json.dumps(acquisition or {}, ensure_ascii=False, indent=2)}

CandidateJudgements:
{json.dumps(list(judgements), ensure_ascii=False, indent=2)}
"""


def _parse_json_response(response: Any) -> dict[str, Any]:
    if isinstance(response, Mapping):
        return dict(response)
    if not isinstance(response, str):
        raise ValueError("model response must be a JSON object or JSON text")
    parsed = json.loads(response)
    if not isinstance(parsed, Mapping):
        raise ValueError("model JSON must be an object")
    return dict(parsed)


def _repair_prompt(
    stage: str,
    original_prompt: str,
    invalid_response: Any,
    errors: list[str],
) -> str:
    return f"""The {stage} response was invalid for its frozen contract.
Return only one corrected JSON object. Do not change the task, add fields,
invent evidence, or include explanations outside the JSON object.

Validation errors:
{json.dumps(errors, ensure_ascii=False)}

Previous response:
{invalid_response}

Original instructions:
{original_prompt}
"""


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _append_trace(
    path: Path,
    run_id: str,
    event: str,
    stage: str,
    details: Mapping[str, Any] | None = None,
) -> None:
    record = {
        "schema_version": "trace.event.checkpoint4.v0",
        "run_id": run_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "stage": stage,
        "details": dict(details or {}),
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return value


def _empty_advice(status: str, uncertainties: Sequence[str] = ()) -> dict[str, Any]:
    return {
        "status": status,
        "primary": None,
        "supporting": None,
        "companion": None,
        "deferred": [],
        "uncertainties": list(uncertainties),
    }


@dataclass(frozen=True)
class JudgeRunResult:
    run_id: str
    run_dir: str
    judgements: list[dict[str, Any]]
    final_advice: dict[str, Any]
    judge_call_count: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "run_dir": self.run_dir,
            "judged_candidate_count": len(self.judgements),
            "judge_call_count": self.judge_call_count,
            "disposition_counts": {
                disposition: sum(
                    judgement["disposition"] == disposition
                    for judgement in self.judgements
                )
                for disposition in sorted(JUDGE_DISPOSITIONS)
            },
            "final_advice": self.final_advice,
        }


class JudgeRuntime:
    """Judge existing Evidence Packs and produce bounded Final Advice."""

    def __init__(self, model: PlanningModel):
        self.model = model

    def run(self, run_dir: str | Path) -> JudgeRunResult:
        output_dir = Path(run_dir)
        run_id = output_dir.name
        trace_path = output_dir / "trace.jsonl"
        capability_artifact = _read_json(output_dir / "01_capability_contract.json")
        intervention_plan = _read_json(output_dir / "02_intervention_plan.json")
        query_plan = _read_json(output_dir / "03_query_plan.json")
        capability_contract = capability_artifact.get("contract", capability_artifact)
        decision = intervention_plan.get("decision")

        if decision == "no_intervention":
            return self._finish_without_judge(
                output_dir,
                trace_path,
                run_id,
                status="no_intervention",
                uncertainties=(),
                reason="planning selected no_intervention",
            )
        if decision == "clarify" or query_plan.get("status") == "clarify":
            question = capability_artifact.get("clarification_question")
            uncertainties = [question] if isinstance(question, str) and question.strip() else []
            return self._finish_without_judge(
                output_dir,
                trace_path,
                run_id,
                status="needs_clarification",
                uncertainties=uncertainties,
                reason="planning requires clarification",
            )

        acquisition = (
            _read_json(output_dir / "04_candidate_acquisition.json")
            if (output_dir / "04_candidate_acquisition.json").exists()
            else None
        )
        evidence = (
            _read_json(output_dir / "05_evidence_packs.json")
            if (output_dir / "05_evidence_packs.json").exists()
            else None
        )
        packs = evidence.get("packs", []) if evidence else []
        if not isinstance(packs, list) or not packs:
            status = "source_error" if acquisition and acquisition.get("status") in {
                "unsupported_family_surface",
                "partial_unsupported_family_surface",
            } else "insufficient_evidence"
            warning_text = [
                str(item.get("message"))
                for item in (acquisition or {}).get("warnings", [])
                if isinstance(item, Mapping) and item.get("message")
            ]
            return self._finish_without_judge(
                output_dir,
                trace_path,
                run_id,
                status=status,
                uncertainties=warning_text,
                reason="no judgeable EvidencePack is available",
            )

        _append_trace(
            trace_path,
            run_id,
            "stage_start",
            "Candidate Judgement",
            {"prompt_version": JUDGE_PROMPT_VERSION, "candidate_count": len(packs)},
        )
        judgements: list[dict[str, Any]] = []
        for pack in packs:
            if not isinstance(pack, Mapping):
                raise JudgeStageError("EvidencePack must be an object")
            candidate_id = str(pack.get("candidate_id") or "")
            if not candidate_id:
                raise JudgeStageError("EvidencePack is missing candidate_id")
            _append_trace(
                trace_path,
                run_id,
                "candidate_judgement_start",
                "Candidate Judgement",
                {
                    "candidate_id": candidate_id,
                    "fused_rank": pack.get("retrieval", {}).get("fused_rank"),
                },
            )
            judgement = self._model_call(
                trace_path=trace_path,
                run_id=run_id,
                stage="Candidate Judgement",
                prompt_version=JUDGE_PROMPT_VERSION,
                prompt=judge_candidate_prompt(
                    capability_contract,
                    intervention_plan,
                    pack,
                ),
                validator=validate_candidate_judgement,
                context={"candidate_id": candidate_id},
            )
            if judgement["candidate_id"] != candidate_id:
                raise JudgeStageError(
                    f"Judge returned candidate_id={judgement['candidate_id']!r} "
                    f"for pack={candidate_id!r}"
                )
            invalid_refs = set(judgement["evidence"]) - EVIDENCE_REFS
            if invalid_refs:
                raise JudgeStageError(
                    f"Judge returned evidence references outside EvidencePack: {sorted(invalid_refs)}"
                )
            judgements.append(judgement)
            _append_trace(
                trace_path,
                run_id,
                "candidate_judgement_complete",
                "Candidate Judgement",
                {
                    "candidate_id": candidate_id,
                    "disposition": judgement["disposition"],
                },
            )

        judgement_artifact = {
            "schema_version": "checkpoint4.judgements.v0",
            "run_id": run_id,
            "stage": "Candidate Judgement",
            "judged_candidate_count": len(judgements),
            "judgements": judgements,
        }
        _write_json(output_dir / "06_judgements.json", judgement_artifact)
        _append_trace(
            trace_path,
            run_id,
            "stage_complete",
            "Candidate Judgement",
            {"judged_candidate_count": len(judgements)},
        )

        _append_trace(
            trace_path,
            run_id,
            "stage_start",
            "Final Advice",
            {"prompt_version": FINAL_ADVICE_PROMPT_VERSION},
        )
        advice = self._model_call(
            trace_path=trace_path,
            run_id=run_id,
            stage="Final Advice",
            prompt_version=FINAL_ADVICE_PROMPT_VERSION,
            prompt=final_advice_prompt(
                capability_contract,
                intervention_plan,
                acquisition,
                judgements,
            ),
            validator=lambda value: validate_final_advice_against_judgements(
                value,
                judgements,
            ),
            context={},
        )
        if acquisition and acquisition.get("warnings"):
            uncertainties = list(advice["uncertainties"])
            if UNSUPPORTED_INTEGRATION_UNCERTAINTY not in uncertainties:
                uncertainties.append(UNSUPPORTED_INTEGRATION_UNCERTAINTY)
            advice["uncertainties"] = uncertainties
            advice = validate_final_advice_against_judgements(advice, judgements)
        _write_json(
            output_dir / "07_final_advice.json",
            {
                "schema_version": "checkpoint4.final_advice.v0",
                "run_id": run_id,
                "stage": "Final Advice",
                **advice,
            },
        )
        _append_trace(
            trace_path,
            run_id,
            "stage_complete",
            "Final Advice",
            {"status": advice["status"]},
        )
        return JudgeRunResult(
            run_id,
            str(output_dir),
            judgements,
            advice,
            len(judgements),
        )

    def _finish_without_judge(
        self,
        output_dir: Path,
        trace_path: Path,
        run_id: str,
        *,
        status: str,
        uncertainties: Sequence[str],
        reason: str,
    ) -> JudgeRunResult:
        _append_trace(
            trace_path,
            run_id,
            "stage_start",
            "Candidate Judgement",
            {"status": "skipped", "reason": reason},
        )
        _append_trace(
            trace_path,
            run_id,
            "stage_complete",
            "Candidate Judgement",
            {"status": "skipped", "reason": reason},
        )
        advice = validate_final_advice(
            _empty_advice(status, uncertainties),
        )
        _write_json(
            output_dir / "07_final_advice.json",
            {
                "schema_version": "checkpoint4.final_advice.v0",
                "run_id": run_id,
                "stage": "Final Advice",
                **advice,
            },
        )
        _append_trace(
            trace_path,
            run_id,
            "stage_start",
            "Final Advice",
            {"source": "early_stop", "status": status},
        )
        _append_trace(
            trace_path,
            run_id,
            "stage_complete",
            "Final Advice",
            {"status": status, "judge_call_count": 0},
        )
        return JudgeRunResult(run_id, str(output_dir), [], advice, 0)

    def _model_call(
        self,
        *,
        trace_path: Path,
        run_id: str,
        stage: str,
        prompt_version: str,
        prompt: str,
        validator: Callable[[Any], dict[str, Any]],
        context: Mapping[str, Any],
    ) -> dict[str, Any]:
        current_prompt = prompt
        invalid_response: Any = None
        errors: list[str] = []
        for repair_attempt in range(2):
            started = time.perf_counter()
            try:
                response = self.model.generate_structured(
                    stage=stage,
                    prompt=current_prompt,
                    prompt_version=prompt_version,
                )
            except Exception as error:
                _append_trace(
                    trace_path,
                    run_id,
                    "model_call",
                    stage,
                    {
                        **context,
                        "provider": getattr(self.model, "provider_name", "unknown"),
                        "model": getattr(self.model, "model_name", "unknown"),
                        "prompt_version": prompt_version,
                        "repair_attempt": repair_attempt,
                        "success": False,
                        "latency_ms": round((time.perf_counter() - started) * 1000, 2),
                    },
                )
                _append_trace(
                    trace_path,
                    run_id,
                    "error",
                    stage,
                    {"error_type": type(error).__name__, "error": str(error), **context},
                )
                raise
            _append_trace(
                trace_path,
                run_id,
                "model_call",
                stage,
                {
                    **context,
                    "provider": getattr(self.model, "provider_name", "unknown"),
                    "model": getattr(self.model, "model_name", "unknown"),
                    "prompt_version": prompt_version,
                    "repair_attempt": repair_attempt,
                    "success": True,
                    "latency_ms": round((time.perf_counter() - started) * 1000, 2),
                },
            )
            invalid_response = response
            try:
                parsed = _parse_json_response(response)
                return validator(parsed)
            except (JudgeValidationError, ValueError) as error:
                errors = error.errors if isinstance(error, JudgeValidationError) else [str(error)]
                _append_trace(
                    trace_path,
                    run_id,
                    "validation_result",
                    stage,
                    {"valid": False, "repair_attempt": repair_attempt, "errors": errors, **context},
                )
                if repair_attempt == 0:
                    current_prompt = _repair_prompt(
                        stage,
                        prompt,
                        invalid_response,
                        errors,
                    )
                    continue
                final_error = JudgeStageError(
                    f"{stage} remained invalid after one repair attempt: {'; '.join(errors)}"
                )
                _append_trace(
                    trace_path,
                    run_id,
                    "error",
                    stage,
                    {
                        "error_type": type(final_error).__name__,
                        "error": str(final_error),
                        **context,
                    },
                )
                raise final_error from error
        raise AssertionError("unreachable")
