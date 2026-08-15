"""Validation layer.

Deterministic/rule-based checks and the human confirmation gate that LLM
output must pass before finalizing protected outcomes (see
docs/architecture/decisions/ADR-001-llm-decision-boundaries.md). No other
component may finalize those outcomes directly from raw LLM output.
"""
