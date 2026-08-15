"""Unit tests for the pure, deterministic instrument-impact assessment.

No database session involved: `Event`s are constructed directly, mirroring
`tests/narrative_engine/test_assignment.py`.
"""

from __future__ import annotations

from market_intel.instrument_impact.assessment import assess_impact
from market_intel.persistence.models import Event, ImpactDirection, ImpactHorizon, Instrument


def _rate_decision_event(*facts: str, **overrides: object) -> Event:
    defaults: dict[str, object] = {
        "title": "FOMC statement",
        "type": "rate_decision",
        "extracted_facts": list(facts),
    }
    defaults.update(overrides)
    return Event(document_id=1, **defaults)


def test_a_rate_hike_fact_is_assessed_as_bearish_for_nq_with_a_multi_day_horizon() -> None:
    event = _rate_decision_event(
        "The Committee raised the target range for the federal funds rate to 4 to 4-1/4 percent."
    )

    assessment = assess_impact([event], instrument=Instrument.NQ)

    assert assessment.instrument is Instrument.NQ
    assert assessment.direction is ImpactDirection.BEARISH
    assert assessment.horizon is ImpactHorizon.MULTI_DAY
    assert "raised the target range" in assessment.rationale


def test_a_rate_cut_fact_is_assessed_as_bullish_for_nq_with_a_multi_day_horizon() -> None:
    event = _rate_decision_event(
        "The Committee lowered the target range for the federal funds rate to 3 to 3-1/4 percent."
    )

    assessment = assess_impact([event], instrument=Instrument.NQ)

    assert assessment.direction is ImpactDirection.BULLISH
    assert assessment.horizon is ImpactHorizon.MULTI_DAY
    assert "lowered the target range" in assessment.rationale


def test_a_rate_hold_fact_is_assessed_as_neutral_for_nq() -> None:
    event = _rate_decision_event(
        "The Committee maintained the target range at 3-1/2 to 3-3/4 percent."
    )

    assessment = assess_impact([event], instrument=Instrument.NQ)

    assert assessment.direction is ImpactDirection.NEUTRAL
    assert assessment.horizon is ImpactHorizon.MULTI_DAY
    assert "maintained the target range" in assessment.rationale


def test_conflicting_rate_decision_facts_are_assessed_as_mixed_with_unknown_horizon() -> None:
    event = _rate_decision_event(
        "The Committee raised the target range for the federal funds rate.",
        "A separate release reported the Committee lowered the target range last quarter.",
    )

    assessment = assess_impact([event], instrument=Instrument.NQ)

    assert assessment.direction is ImpactDirection.MIXED
    assert assessment.horizon is ImpactHorizon.UNKNOWN
    assert "raised the target range" in assessment.rationale
    assert "lowered the target range" in assessment.rationale


def test_no_rate_decision_event_is_assessed_as_uncertain_with_unknown_horizon() -> None:
    non_rate_event = Event(
        document_id=1,
        title="Quarterly earnings report",
        type="earnings_report",
        extracted_facts=["Revenue grew 12% year over year."],
    )

    assessment = assess_impact([non_rate_event], instrument=Instrument.NQ)

    assert assessment.direction is ImpactDirection.UNCERTAIN
    assert assessment.horizon is ImpactHorizon.UNKNOWN
    assert "1 event" in assessment.rationale


def test_a_rate_decision_event_with_no_classifiable_fact_is_assessed_as_uncertain() -> None:
    event = _rate_decision_event("The Committee will announce its decision at 2pm.")

    assessment = assess_impact([event], instrument=Instrument.NQ)

    assert assessment.direction is ImpactDirection.UNCERTAIN
    assert assessment.horizon is ImpactHorizon.UNKNOWN


def test_a_trigger_verb_used_outside_a_rate_target_range_context_is_not_classified() -> None:
    """A `rate_decision` event does not guarantee every fact under it literally

    describes the rate action: a fact merely containing a trigger verb (e.g.
    "raised") without a rate/target-range anchor must fall through to the
    same no-signal path as if no trigger verb were present at all, never a
    confident hike/cut/hold. Reproduces the false positive found in
    validation, where "The Chair raised concerns about persistent inflation
    risks going forward." was previously misclassified as a hike.
    """
    event = _rate_decision_event(
        "The Chair raised concerns about persistent inflation risks going forward."
    )

    assessment = assess_impact([event], instrument=Instrument.NQ)

    assert assessment.direction is ImpactDirection.UNCERTAIN
    assert assessment.horizon is ImpactHorizon.UNKNOWN


def test_a_hold_fact_with_an_unrelated_trailing_dissent_clause_is_not_classified_as_a_hike() -> (
    None
):
    """Reproduces the second-round validation counter-example: a genuine

    HOLD clause ("the target range unchanged") followed by an unrelated
    "after ... raised ..." clause about member dissent must not let the
    unrelated clause's "raised" outrank the real "unchanged" signal. Before
    clause-scoping, whole-string anchor+verb co-occurrence (with no clause
    binding) wrongly classified this as a hike because `_HIKE_PATTERNS` was
    checked first and "raised" appeared somewhere in the string.
    """
    event = _rate_decision_event(
        "The Committee left the target range unchanged after some members "
        "raised objections."
    )

    assessment = assess_impact([event], instrument=Instrument.NQ)

    assert assessment.direction is ImpactDirection.NEUTRAL
    assert assessment.horizon is ImpactHorizon.MULTI_DAY
    assert "unchanged" in assessment.rationale


def test_a_hold_fact_with_a_though_clause_dissent_is_not_classified_as_a_hike() -> None:
    """Same failure mode as above, different conjunction/phrasing: the

    tester's second counter-example uses ", though ... raised ..." instead
    of "after ... raised ...".
    """
    event = _rate_decision_event(
        "The Committee kept the target range unchanged, though one member "
        "raised a dissent."
    )

    assessment = assess_impact([event], instrument=Instrument.NQ)

    assert assessment.direction is ImpactDirection.NEUTRAL
    assert assessment.horizon is ImpactHorizon.MULTI_DAY
    assert "unchanged" in assessment.rationale


def test_a_hike_verb_before_an_unrelated_hold_clause_is_not_classified_as_a_hold() -> None:
    """Adversarial test devised independently of the tester's examples: puts

    the unrelated trigger-verb clause *before* the real anchor+verb clause
    (tester's examples both had the unrelated clause trailing), to check
    that clause-scoping is order-agnostic rather than only correct for a
    "real clause first, bogus clause after" layout. Also exercises the
    "although" splitter rather than "after"/"though". If clause-scoping
    only worked in one direction, this would wrongly classify as HOLD when
    the real, and only, actionable clause is the CUT-free "raised
    objections" (no anchor, contributes nothing) followed by a HOLD clause
    that *does* have an anchor+verb pair — so the expected outcome here is
    still a correct NEUTRAL/HOLD, but arrived at from the opposite layout.
    """
    event = _rate_decision_event(
        "Although one member raised objections, the Committee maintained "
        "the target range unchanged."
    )

    assessment = assess_impact([event], instrument=Instrument.NQ)

    assert assessment.direction is ImpactDirection.NEUTRAL
    assert assessment.horizon is ImpactHorizon.MULTI_DAY
    assert "maintained the target range" in assessment.rationale


def test_a_fact_with_two_independently_valid_but_conflicting_clauses_is_mixed() -> None:
    """A single fact can itself be internally self-contradictory (e.g. a

    single sentence conflating an earlier and a later decision); each of
    its clauses independently has its own valid anchor+verb pair, but with
    different actions. This should resolve via the existing mixed-signal
    path rather than silently picking a winner between the two clauses.
    """
    event = _rate_decision_event(
        "The Committee raised the target range in the September meeting, "
        "although the June statement had lowered the target range."
    )

    assessment = assess_impact([event], instrument=Instrument.NQ)

    assert assessment.direction is ImpactDirection.MIXED
    assert assessment.horizon is ImpactHorizon.UNKNOWN


def test_an_instrument_with_no_documented_mapping_is_assessed_as_uncertain_not_reusing_nq() -> None:
    event = _rate_decision_event(
        "The Committee raised the target range for the federal funds rate."
    )

    assessment = assess_impact([event], instrument=Instrument.BTC)

    assert assessment.instrument is Instrument.BTC
    assert assessment.direction is ImpactDirection.UNCERTAIN
    assert assessment.horizon is ImpactHorizon.UNKNOWN
    assert "raised the target range" in assessment.rationale
    assert "BTC" in assessment.rationale


def test_non_string_facts_are_skipped_without_raising() -> None:
    event = Event(
        document_id=1,
        title="FOMC statement",
        type="rate_decision",
        extracted_facts=[
            "The Committee raised the target range for the federal funds rate.",
            {"unexpected": "structured fact"},
        ],
    )

    assessment = assess_impact([event], instrument=Instrument.NQ)

    assert assessment.direction is ImpactDirection.BEARISH
