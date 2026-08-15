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


def test_a_relative_pronoun_clause_with_raised_is_not_classified_as_a_hike() -> None:
    """Round-3 validation counter-example (a): a relative pronoun ("who")

    joins an unrelated "raised" clause to the subject, well outside the
    2-word bound, before the genuine anchor+verb pair ("left the target
    range unchanged") appears. Clause-splitting (Fix #2) confidently
    misclassified this as a hike because "who" was not in its delimiter
    list; bounded-proximity must reject "raised" on distance alone (and the
    "who" marker is defense-in-depth on top of that).
    """
    event = _rate_decision_event(
        "Officials who had raised concerns about inflation ultimately left "
        "the target range unchanged."
    )

    assessment = assess_impact([event], instrument=Instrument.NQ)

    assert assessment.direction is ImpactDirection.NEUTRAL
    assert assessment.horizon is ImpactHorizon.MULTI_DAY
    assert "unchanged" in assessment.rationale


def test_a_subordinator_clause_with_raised_is_not_classified_as_a_hike() -> None:
    """Round-3 validation counter-example (b): the subordinator "even as"

    joins an unrelated "raised" clause trailing the genuine anchor+verb
    pair. Same failure mode as the relative-pronoun case, different
    subordinating conjunction and different clause ordering (unrelated
    clause trails here instead of leading).
    """
    event = _rate_decision_event(
        "The Committee left the target range unchanged even as some "
        "policymakers raised concerns about sticky inflation."
    )

    assessment = assess_impact([event], instrument=Instrument.NQ)

    assert assessment.direction is ImpactDirection.NEUTRAL
    assert assessment.horizon is ImpactHorizon.MULTI_DAY
    assert "unchanged" in assessment.rationale


def test_a_zero_marker_participial_raised_clause_is_not_classified_as_a_hike() -> None:
    """Round-3 validation counter-example (c): a bare participial phrase

    ("having raised rates twice this year") with **no lexical delimiter at
    all** between it and the genuine anchor+verb pair. No finite delimiter
    list could ever catch this — it must be rejected by the word-distance
    bound itself, which this test asserts is actually what is being
    exercised (no comma or listed conjunction/subordinator appears anywhere
    in the fact).
    """
    fact = "The Committee having raised rates twice this year left the target range unchanged."
    assert "," not in fact
    for marker_word in ("though", "but", "while", "although", "after", "and", "however"):
        assert marker_word not in fact.lower()

    event = _rate_decision_event(fact)

    assessment = assess_impact([event], instrument=Instrument.NQ)

    assert assessment.direction is ImpactDirection.NEUTRAL
    assert assessment.horizon is ImpactHorizon.MULTI_DAY
    assert "unchanged" in assessment.rationale


def test_a_different_relative_pronoun_clause_with_raised_is_not_classified_as_a_hike() -> None:
    """Broader coverage variant of counter-example (a): a different relative

    pronoun ("that" instead of "who") introducing the unrelated "raised"
    clause, to check the fix generalizes rather than special-casing "who".
    """
    event = _rate_decision_event(
        "The dissent that one member raised did not stop the Committee from "
        "leaving the target range unchanged."
    )

    assessment = assess_impact([event], instrument=Instrument.NQ)

    assert assessment.direction is ImpactDirection.NEUTRAL
    assert assessment.horizon is ImpactHorizon.MULTI_DAY
    assert "unchanged" in assessment.rationale


def test_a_different_subordinator_clause_with_raised_is_not_classified_as_a_hike() -> None:
    """Broader coverage variant of counter-example (b): a different

    subordinator ("since" instead of "even as") leading the unrelated
    "raised" clause, to check the fix generalizes rather than special-
    casing "even as". Deliberately has **no comma** between the two
    clauses (unlike the "though"/"after" round-2 fixtures): the old
    clause-splitting code's fixed delimiter list does not include "since",
    so without a comma to also split on, old code would read this whole
    fact as one clause and confidently misclassify "raised" as a hike;
    with a comma present this fixture would pass even against the old
    code and would not actually exercise the fix.
    """
    fact = (
        "Since one policymaker raised concerns about persistent inflation "
        "the Committee left the target range unchanged."
    )
    assert "," not in fact

    event = _rate_decision_event(fact)

    assessment = assess_impact([event], instrument=Instrument.NQ)

    assert assessment.direction is ImpactDirection.NEUTRAL
    assert assessment.horizon is ImpactHorizon.MULTI_DAY
    assert "unchanged" in assessment.rationale


def test_a_second_zero_marker_participial_raised_clause_is_not_classified_as_a_hike() -> None:
    """Broader coverage variant of counter-example (c): a different

    zero-marker participial construction ("despite having raised...")
    where "despite" is deliberately not in the disqualifying-marker list,
    so this must also be rejected purely on the word-distance bound rather
    than any marker, with the unrelated clause trailing instead of leading.
    """
    fact = (
        "The Committee left the target range unchanged despite having "
        "raised rates at the prior two meetings."
    )
    assert "," not in fact
    for marker_word in (
        "though",
        "but",
        "while",
        "although",
        "after",
        "and",
        "however",
        "who",
        "which",
        "that",
        "whose",
        "whom",
        "even as",
        "as",
        "since",
        "when",
        "where",
        "once",
        "whereas",
        "unless",
        "if",
        "because",
        "before",
        "until",
    ):
        assert f" {marker_word} " not in f" {fact.lower()} "

    event = _rate_decision_event(fact)

    assessment = assess_impact([event], instrument=Instrument.NQ)

    assert assessment.direction is ImpactDirection.NEUTRAL
    assert assessment.horizon is ImpactHorizon.MULTI_DAY
    assert "unchanged" in assessment.rationale


def test_an_unrelated_verb_in_a_second_sentence_is_disqualified_by_the_period() -> None:
    """Round-4 validation counter-example: the disqualifying-marker list had

    no sentence-terminal punctuation, so an unrelated verb in a second short
    sentence could land within the 2-word distance bound of an anchor in a
    first, unrelated short sentence. "stayed" is not a HOLD trigger, so the
    only verb occurrence is "raised"; before the period was added to
    `_DISQUALIFYING_MARKER_PATTERN`, it fell inside the distance bound of
    "target range" with no marker between them and was wrongly classified
    as a hike.
    """
    event = _rate_decision_event("The target range stayed. He raised his hand.")

    assessment = assess_impact([event], instrument=Instrument.NQ)

    assert assessment.direction is ImpactDirection.UNCERTAIN
    assert assessment.horizon is ImpactHorizon.UNKNOWN


def test_an_unrelated_verb_in_a_second_sentence_does_not_turn_a_hold_into_mixed() -> None:
    """Same failure mode as above, but with a genuine HOLD verb ("held") in

    the first sentence: before the period was added to
    `_DISQUALIFYING_MARKER_PATTERN`, the unrelated "raised" in the second
    sentence fell inside the distance bound of "target range" with no
    marker between them, adding a spurious HIKE action alongside the
    correct HOLD action and producing a mixed-signal result instead of a
    clean hold.
    """
    event = _rate_decision_event("The target range held. Someone raised objections.")

    assessment = assess_impact([event], instrument=Instrument.NQ)

    assert assessment.direction is ImpactDirection.NEUTRAL
    assert assessment.horizon is ImpactHorizon.MULTI_DAY
    assert "held" in assessment.rationale


def test_an_em_dash_clause_join_with_raised_does_not_turn_a_hold_into_mixed() -> None:
    """Round-6 validation counter-example: an em dash used as a clause-joiner

    (no comma, semicolon, sentence-terminal punctuation, or listed
    conjunction/subordinator) between a genuine HOLD anchor+verb pair and an
    unrelated "raised" clause. Before dashes were added to
    `_DISQUALIFYING_MARKER_PATTERN`, "raised" fell inside the 2-word distance
    bound of "target range" with no marker between them, adding a spurious
    HIKE action alongside the correct HOLD action.
    """
    event = _rate_decision_event("The target range held — someone raised objections.")

    assessment = assess_impact([event], instrument=Instrument.NQ)

    assert assessment.direction is ImpactDirection.NEUTRAL
    assert assessment.horizon is ImpactHorizon.MULTI_DAY
    assert "held" in assessment.rationale


def test_a_double_hyphen_clause_join_with_raised_does_not_turn_a_hold_into_mixed() -> None:
    """Same failure mode as the em-dash case above, using the common ASCII

    double-hyphen (`--`) substitute for an em dash instead of the literal
    em-dash character.
    """
    event = _rate_decision_event("The target range held -- someone raised objections.")

    assessment = assess_impact([event], instrument=Instrument.NQ)

    assert assessment.direction is ImpactDirection.NEUTRAL
    assert assessment.horizon is ImpactHorizon.MULTI_DAY
    assert "held" in assessment.rationale


def test_a_spaced_single_hyphen_clause_join_with_raised_does_not_turn_a_hold_into_mixed() -> (
    None
):
    """Same failure mode again, using a spaced single hyphen (` - `), the

    plainest ASCII clause-joining dash convention.
    """
    event = _rate_decision_event("The target range held - someone raised objections.")

    assessment = assess_impact([event], instrument=Instrument.NQ)

    assert assessment.direction is ImpactDirection.NEUTRAL
    assert assessment.horizon is ImpactHorizon.MULTI_DAY
    assert "held" in assessment.rationale


def test_a_hyphenated_compound_word_between_anchor_and_verb_is_not_a_new_false_negative() -> (
    None
):
    """Checks whether adding a bare hyphen to the disqualifying-marker

    pattern creates a *new* false negative for a genuine same-clause
    anchor+verb pair that happens to contain a hyphenated compound word
    between them. It does not, in this domain: idiomatic Fed-statement
    phrasing always has "the" immediately before the anchor phrase
    ("raised the target range"), and `_BETWEEN_SPAN_WORD_PATTERN` already
    splits any hyphenated word into two word-distance-bound tokens (e.g.
    "short-term" -> "short", "term"); "the" plus any hyphenated modifier is
    therefore always at least 3 tokens, already exceeding
    `_MAX_WORDS_BETWEEN_ANCHOR_AND_VERB` (2) on the pre-existing,
    unmodified distance bound alone. This fact is uncertain both before
    and after this patch, for a reason unrelated to the new dash marker. A
    hyphenated modifier could only fit inside the 2-word bound by omitting
    "the" entirely (e.g. "raised short-term target range"), which is not
    realistic Fed-statement phrasing and does not occur in any of this
    module's existing fixtures.
    """
    event = _rate_decision_event(
        "The Committee raised the short-term target range for the federal funds rate."
    )

    assessment = assess_impact([event], instrument=Instrument.NQ)

    assert assessment.direction is ImpactDirection.UNCERTAIN
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
