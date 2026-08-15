"""Unit tests for deterministic `canonical_key` derivation.

Pure/network-free per `docs/architecture/ai-and-evidence.md` (Testing
Expectations): narrative assignment must be tested deterministically.
"""

from __future__ import annotations

from market_intel.narrative_engine.canonical_key import compute_canonical_key
from market_intel.persistence.models import Event


def _event(**overrides: object) -> Event:
    defaults: dict[str, object] = {
        "type": "rate_decision",
        "entities": ["Federal Reserve", "FOMC"],
        "topics": ["monetary_policy"],
    }
    defaults.update(overrides)
    return Event(title="unused for key derivation", **defaults)


def test_same_semantic_identity_produces_the_same_key_regardless_of_order_and_case() -> None:
    event_a = _event(
        entities=["Federal Reserve", "FOMC"], topics=["Monetary Policy", "Interest Rates"]
    )
    event_b = _event(
        entities=["fomc", "  federal reserve  "], topics=["interest rates", "monetary policy"]
    )

    assert compute_canonical_key(event_a) == compute_canonical_key(event_b)


def test_distinct_type_produces_a_distinct_key() -> None:
    event_a = _event(type="rate_decision")
    event_b = _event(type="earnings_report")

    assert compute_canonical_key(event_a) != compute_canonical_key(event_b)


def test_distinct_entities_produce_a_distinct_key() -> None:
    event_a = _event(entities=["Federal Reserve"])
    event_b = _event(entities=["European Central Bank"])

    assert compute_canonical_key(event_a) != compute_canonical_key(event_b)


def test_missing_type_and_empty_entities_still_produce_a_stable_key() -> None:
    event_a = _event(type=None, entities=[], topics=[])
    event_b = _event(type=None, entities=[], topics=[])

    assert compute_canonical_key(event_a) == compute_canonical_key(event_b)


def test_key_is_a_fixed_length_hex_digest() -> None:
    key = compute_canonical_key(_event())

    assert len(key) == 64
    assert all(character in "0123456789abcdef" for character in key)
