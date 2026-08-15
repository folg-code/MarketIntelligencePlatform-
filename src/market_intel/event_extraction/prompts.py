"""Prompt construction for LLM-assisted event extraction.

The fact/claim separation instructed here is a structural requirement, not
just prompt wording: `extraction.parse_llm_response` always maps the
model's `extracted_facts` and `source_claims` into two separate `Event`
fields regardless of what the prompt says, so a model that ignores this
instruction cannot silently merge the two into one field (see
`docs/architecture/domain-model.md`, Invariants).
"""

from __future__ import annotations

from market_intel.persistence.models import Document

SYSTEM_PROMPT = """You are an event-extraction assistant for a market intelligence system.

Given the full text of one source document, identify the distinct \
real-world event(s) it reports. Extract only what the text actually \
supports; never invent facts, claims, or entities that are not stated.

For each event you MUST separate two different kinds of statements:
- "extracted_facts": literal, checkable factual statements the source \
makes (e.g. "the Committee maintained the target range at 3.5 to 3.75 \
percent").
- "source_claims": the source's own interpretation, judgment, or framing \
(e.g. "the Committee judges risks to be roughly balanced").

Never combine a fact and a claim in the same string, and never put a fact \
in "source_claims" or a claim in "extracted_facts".

Respond with ONLY a single JSON object, no other text, matching this shape:
{"events": [{"type": string, "title": string, "occurred_at": string or \
null (ISO-8601 timestamp, only if the text states a specific date/time), \
"entities": [string], "topics": [string], "extracted_facts": [string], \
"source_claims": [string], "confidence": number between 0 and 1}]}

If the text reports no identifiable event, respond with {"events": []}."""


def build_user_prompt(document: Document, full_text: str) -> str:
    """Build the user-turn prompt for one `Document`'s fetched full text."""
    published = document.published_at.isoformat() if document.published_at else "unknown"
    return (
        f"Source: {document.source}\n"
        f"Title: {document.title}\n"
        f"Published: {published}\n"
        f"Full text:\n{full_text}"
    )
