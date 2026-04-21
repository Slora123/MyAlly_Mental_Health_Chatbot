"""
src/rag/safety.py
──────────────────
Section 11 of the Implementation Guide: Safety Layer.

Two functions:
  check_pre_generation(message)  → (is_safe, reason)
  check_post_generation(reply)   → (is_safe, list_of_issues)

Pre-generation is a fast gate before any retrieval or generation.
Post-generation reviews the model's reply before it reaches the user.
"""

from __future__ import annotations

from src.rag.router import is_high_risk

# ── Post-generation red-flag patterns ─────────────────────────────────────────
# Each entry is (description, list_of_trigger_phrases).
# Phrase matching is case-insensitive on normalised text.

_DIAGNOSIS_PATTERNS: list[str] = [
    "you have depression",
    "you have anxiety",
    "you are depressed",
    "you are anxious",
    "you definitely have",
    "you clearly have",
    "you suffer from",
    "you are diagnosed",
    "i diagnose",
    "this is a diagnosis",
    "based on your symptoms you have",
]

_MEDICATION_PATTERNS: list[str] = [
    "stop taking your medication",
    "stop taking your medicine",
    "stop your medication",
    "don't take your medication",
    "do not take your medication",
    "take more",
    "increase your dose",
    "decrease your dose",
    "change your prescription",
    "you should stop your antidepressant",
    "you should stop your pills",
]

_DISMISSIVE_PATTERNS: list[str] = [
    "just get over it",
    "stop being dramatic",
    "you're overreacting",
    "you are overreacting",
    "it's not a big deal",
    "it is not a big deal",
    "everyone feels that way",
    "just be positive",
    "just think happy thoughts",
    "you should be grateful",
    "others have it worse",
    "stop being weak",
    "man up",
    "grow up",
]

_CERTAINTY_PATTERNS: list[str] = [
    "i am certain that",
    "100 percent sure",
    "guaranteed to",
    "this will definitely cure",
    "this will definitely fix",
    "scientifically proven that you",
    "there is no doubt",
    "you will definitely feel better if you",
]

_UNSAFE_ADVICE_PATTERNS: list[str] = [
    "ignore those thoughts",
    "just ignore the urge",
    "ignore thoughts of suicide",
    "you don't need a therapist",
    "you do not need a therapist",
    "therapy is not for you",
    "you don't need help",
    "you do not need help",
]


def _normalise(text: str) -> str:
    return " ".join(text.lower().split())


def _find_matches(norm_text: str, patterns: list[str]) -> list[str]:
    return [p for p in patterns if p in norm_text]


# ── Public API ────────────────────────────────────────────────────────────────


def check_pre_generation(message: str) -> tuple[bool, str]:
    """
    Pre-generation safety gate (Section 11 – Pre-generation checks).

    Returns
    -------
    (True, "")            – message is safe to proceed with normal RAG flow
    (False, reason_str)   – message requires special handling (crisis path)
    """
    if is_high_risk(message):
        return False, "high_risk_signal_detected"
    return True, ""


def check_post_generation(reply: str) -> tuple[bool, list[str]]:
    """
    Post-generation safety review (Section 11 – Post-generation checks).

    Checks the model's reply for:
      - Diagnosis claims
      - Unsafe medication advice
      - Dismissive or blaming language
      - Unsafe advice (e.g. "ignore those thoughts")
      - Excessive certainty overclaiming

    Returns
    -------
    (True, [])            – reply passed all checks
    (False, [issue_list]) – reply failed one or more checks; caller should
                            log the issues and either warn or regenerate.
    """
    norm = _normalise(reply)
    issues: list[str] = []

    if _find_matches(norm, _DIAGNOSIS_PATTERNS):
        issues.append("diagnosis_claim_detected")

    if _find_matches(norm, _MEDICATION_PATTERNS):
        issues.append("unsafe_medication_advice_detected")

    if _find_matches(norm, _DISMISSIVE_PATTERNS):
        issues.append("dismissive_or_blaming_language_detected")

    if _find_matches(norm, _UNSAFE_ADVICE_PATTERNS):
        issues.append("unsafe_advice_detected")

    if _find_matches(norm, _CERTAINTY_PATTERNS):
        issues.append("certainty_overclaiming_detected")

    return (len(issues) == 0), issues
