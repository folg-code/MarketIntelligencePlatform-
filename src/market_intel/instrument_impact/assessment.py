"""Pure, deterministic instrument-impact assessment.

Given a set of already-extracted `Event`s belonging to one `Narrative`, decide
a `NarrativeInstrumentImpact` direction/relevance/horizon for one `Instrument`.
Kept free of any database/session/LLM/HTTP dependency, mirroring the
`narrative_engine.assignment` / `evidence.aggregation` pure-function split
(`market_intel.instrument_impact.service` is the thin async orchestrator that
persists the result).

Per `docs/architecture/domain-model.md` (Invariants, Protected Semantics), a
`NarrativeInstrumentImpact` must never be inferred solely from
entity/keyword presence. This module does not classify a fact on a bare
action verb (raised/lowered/held/etc.) alone: a fact is only classified as a
hike/cut/hold if it contains BOTH the action verb AND a rate/target-range
anchor phrase ("target range" or "federal funds rate") that are *related* —
decided by a bounded-proximity test directly on the raw fact string (see
`_is_related`/`_classify_fact`), not by splitting the string into clauses
first. For a given trigger-verb occurrence, its nearest anchor-phrase
occurrence (by word distance, in either order) is related to it only if (1)
at most two words separate them, (2) the span between them contains no
character outside letters/digits/whitespace (an allowlist-by-complement —
see `_DISALLOWED_BETWEEN_SPAN_CHARACTER_PATTERN` — so any current or future
punctuation/symbol used as an informal clause joiner disqualifies by
construction, with nothing to enumerate), and (3) the span between them
contains none of a fixed set of contrast/coordinating conjunctions,
relative pronouns, and subordinators (a closed grammatical vocabulary — see
`_DISQUALIFYING_MARKER_WORD_PATTERN`). All three conditions must hold; if the nearest
anchor fails any one, that verb occurrence contributes no signal and is
never retried against a farther anchor occurrence (e.g. "...target range
unchanged after some members raised objections" — "raised" is both too far
from "target range" and separated from it by "after" — contributes no
signal from that occurrence), and a bare trigger verb with no anchor
anywhere in the fact (e.g. "The Chair raised concerns about inflation
risks") contributes no signal at all. The word-distance bound is the primary
mechanism, not either marker check: it is what closes cases with no lexical
or orthographic delimiter at all (e.g. "The Committee having raised rates
twice this year left the target range unchanged" — a bare participial
phrase neither marker check could ever catch), while the character
allowlist and the connector-word blocklist are both defense-in-depth for
cases that are marked (by punctuation/symbol or by a connector word,
respectively) but still within the word bound. This is a best-effort
heuristic, not a syntactic parse: it can under-match (an anchor and verb
genuinely belonging together but separated by more than two words — e.g. by
a longer appositive or interposed adverbial phrase — will fail the distance
bound and the fact will fall through to no-signal rather than being
classified) or, in principle, over-match on unusual phrasing where an
unrelated verb happens to sit within two words of an anchor with no
disqualifying punctuation or connector word between them; the guarantee
this module makes is narrower than "correctly parses arbitrary English" — it
is that a verb more than two words (or a punctuation-marked or
connector-word-marked clause boundary) away from every anchor occurrence
cannot masquerade as evidence for that anchor. Falling through to no signal
on ambiguous/unbounded phrasing is
intentional: an omitted signal is preferred over a confidently wrong
directional call. This module also gates on `Event.type == "rate_decision"`,
but that upstream Event-level classification is not by itself treated as
sufficient evidence that any given fact under the event literally describes
the rate action; the bounded-proximity anchor+verb check on the fact text is
what determines what the Fed actually did. A single fact whose independent
anchor-verb pairs yield different actions (e.g. one pair says "raised", a
different pair says "lowered") contributes one classified entry per
distinct action, which feeds the same mixed-signal handling used for
conflicting facts across events (see `_classified_rate_decision_facts`).
The resulting `rationale` always quotes the specific fact(s) that drove the
conclusion. Deliberately narrow MVP scope (see
`ImplementationReport.assumptions`): only rate-decision events are
interpreted; any other `Event.type` contributes no signal and the assessor
reports `uncertain`/`unknown` rather than guessing.
"""

from __future__ import annotations

import enum
import re
from dataclasses import dataclass
from re import Pattern

from market_intel.persistence.models import Event, ImpactDirection, ImpactHorizon, Instrument

_RATE_DECISION_EVENT_TYPE = "rate_decision"

# Relevance is an unconstrained 0-1 float (see `NarrativeInstrumentImpact.relevance`
# docstring); these named levels keep the mapping from "how clear was the
# signal" to a relevance score explicit and auditable rather than a bare
# magic number scattered through the logic below.
_RELEVANCE_NO_SIGNAL = 0.1
_RELEVANCE_MIXED_SIGNAL = 0.4
_RELEVANCE_CLEAR_SIGNAL_BASE = 0.6
_RELEVANCE_PER_CORROBORATING_FACT = 0.1
_RELEVANCE_MAX = 1.0


class _RateAction(enum.Enum):
    """A rate-decision outcome literally stated by a fact, before instrument mapping."""

    HIKE = "hike"
    CUT = "cut"
    HOLD = "hold"


@dataclass(frozen=True)
class _ClassifiedFact:
    action: _RateAction
    fact: str


@dataclass(frozen=True)
class ImpactAssessment:
    """The deterministic outcome of assessing one `Instrument`'s impact."""

    instrument: Instrument
    direction: ImpactDirection
    relevance: float
    horizon: ImpactHorizon
    rationale: str


# Patterns are matched against the literal `extracted_facts` text (never
# against `entities`/`topics`/titles), so the signal always traces back to
# what the source document actually states the Fed did.
_HIKE_PATTERNS: tuple[Pattern[str], ...] = (
    re.compile(r"\braised\b", re.IGNORECASE),
    re.compile(r"\bincreased\b", re.IGNORECASE),
    re.compile(r"\bhiked\b", re.IGNORECASE),
)
_CUT_PATTERNS: tuple[Pattern[str], ...] = (
    re.compile(r"\blowered\b", re.IGNORECASE),
    re.compile(r"\bcut\b", re.IGNORECASE),
    re.compile(r"\bdecreased\b", re.IGNORECASE),
    re.compile(r"\breduced\b", re.IGNORECASE),
)
_HOLD_PATTERNS: tuple[Pattern[str], ...] = (
    re.compile(r"\bmaintained\b", re.IGNORECASE),
    re.compile(r"\bheld\b", re.IGNORECASE),
    re.compile(r"\bunchanged\b", re.IGNORECASE),
)

# An action verb alone is not sufficient evidence that a fact describes the
# literal rate action (e.g. "raised concerns" is not "raised the target
# range"). A fact is only classifiable if it also names what was
# raised/lowered/held: the target range or the federal funds rate. This is
# the anchor the Protected Semantics section of `domain-model.md` requires
# ("never inferred from keywords alone") — the verb and the anchor must be
# *related* per the bounded-proximity test below (see `_is_related`), not
# merely present anywhere in the same fact string, or an unrelated verb
# could bleed into an anchor's signal to describe a different (or no)
# action.
_RATE_ANCHOR_PATTERN: Pattern[str] = re.compile(
    r"\b(?:target range|federal funds rate)\b", re.IGNORECASE
)

# Bounded-proximity relatedness test, replacing an earlier clause-splitting
# design. Clause-splitting decided "same clause" via a finite delimiter word
# list, which is structurally unable to bound English's open-ended set of
# relative pronouns/subordinators/zero-marker constructs (a bare participial
# phrase with no lexical delimiter at all defeats any such list by
# construction). Relatedness between an anchor-phrase occurrence and a
# trigger-verb occurrence is instead decided directly on the raw fact
# string by three independent, all-must-pass conditions (see `_is_related`):
# (1) at most this many words separate them, (2) no character outside
# letters/digits/whitespace appears in the span between them
# (`_DISALLOWED_BETWEEN_SPAN_CHARACTER_PATTERN`), and (3) no disqualifying
# connector word (`_DISQUALIFYING_MARKER_WORD_PATTERN`) appears in that span.
# Condition (1) is the primary mechanism — it is what closes the zero-marker
# case that neither marker check alone ever could; conditions (2) and (3)
# are both defense-in-depth for cases that are marked (by punctuation/symbol
# or by a connector word, respectively) but still happen to be within the
# word bound. Do not loosen this bound without re-checking it stays below
# the shortest observed cross-clause "bleed" distance (~4 words in the
# counter-examples that motivated this design); see
# `tests/instrument_impact/test_assessment.py` for the fixtures this was
# calibrated against.
_MAX_WORDS_BETWEEN_ANCHOR_AND_VERB = 2

# Word tokenizer used only to count words strictly *between* an anchor match
# and a verb match (never to re-tokenize/re-split the fact as a whole):
# whitespace-delimited runs of letters/digits, with punctuation stripped, so
# a token like "unchanged," counts as one word rather than being skipped or
# double-counted.
_BETWEEN_SPAN_WORD_PATTERN: Pattern[str] = re.compile(r"[A-Za-z0-9]+")

# Punctuation/symbol check, expressed as an allowlist-by-complement rather
# than an enumerated blocklist. Earlier rounds enumerated specific
# disqualifying punctuation characters (comma/semicolon, then
# sentence-terminal punctuation, then dashes) one closed category at a
# time — but real-world text also uses ellipses, bullets, slashes,
# ampersands, pipes, and any number of other symbols as informal clause
# joiners, and a single validation round found five previously-unenumerated
# examples at once. Enumeration of "bad" characters cannot converge against
# that open-ended set. This pattern inverts the check: rather than listing
# disqualifying characters, it matches anything that is *not* in the
# always-permitted set, so any current or future punctuation/symbol
# character disqualifies a pairing by construction, with nothing left to
# enumerate. The permitted character class deliberately mirrors
# `_BETWEEN_SPAN_WORD_PATTERN`'s `[A-Za-z0-9]` plus whitespace (the word
# separator) — it reuses an already-established character class rather than
# inventing a new one. No punctuation exceptions (e.g. an apostrophe for
# contractions, a decimal point for percentages) are carved out of this
# allowlist: all 25 existing fixtures were checked by hand and none needs
# one (decimals such as "4 to 4-1/4 percent" always trail after the anchor
# phrase, never sit between an anchor and a trigger verb, and Fed-statement
# register does not use contractions in this position); if a concrete case
# is ever found needing one, that is a narrow, single-character-class
# addition to this permitted set, not a repeat of the old blocklist's
# unbounded growth pattern.
#
# A bare hyphen-minus (now disqualifying like any other non-alphanumeric,
# non-whitespace character) is heavily overloaded in real text (hyphenated
# compound words, negative numbers, mid-word), but this does not create a
# new false negative in this module's domain: `_BETWEEN_SPAN_WORD_PATTERN`
# already splits any hyphenated word into two separate word-distance-bound
# tokens, and idiomatic Fed-statement phrasing always has "the" immediately
# before the anchor phrase ("raised the target range"), so a hyphenated
# modifier between a genuine anchor and verb already exceeds
# `_MAX_WORDS_BETWEEN_ANCHOR_AND_VERB` on the pre-existing distance bound
# alone, before this character check is ever reached — see
# `test_a_hyphenated_compound_word_between_anchor_and_verb_is_not_a_new_false_negative`.
_DISALLOWED_BETWEEN_SPAN_CHARACTER_PATTERN: Pattern[str] = re.compile(r"[^A-Za-z0-9\s]")

# Connector-word check, deliberately kept as a blocklist: contrast/
# coordinating conjunctions, relative pronouns, and subordinators typically
# introduce a new subject/clause. Unlike the punctuation category above,
# this is a closed, finite English-grammar vocabulary — zero new gaps have
# been found in this exact list since it was introduced, across several
# validation rounds that *did* find gaps in the (now-removed) punctuation
# enumeration. Words pass through the character allowlist above as ordinary
# letters, so there is no conflict between the two checks: the allowlist's
# job is narrowly "reject unrecognized symbols," while whether a specific
# word (though/who/since/etc.) disqualifies a pairing is decided here,
# independently. This is defense-in-depth, not the primary mechanism (see
# `_MAX_WORDS_BETWEEN_ANCHOR_AND_VERB`) — it is deliberately not relied upon
# to close future counter-examples by growing this list further; a case
# this list misses but the distance bound still catches is the intended,
# expected outcome, not a gap.
#
# One residual risk remains, unaffected by either check above: an anchor
# and verb belonging to two *independent* statements with no punctuation or
# symbol at all between them (e.g. upstream LLM extraction dropping
# ordinary sentence punctuation from a run-on `fact` string) is not caught
# by either mechanism and can still fall inside the word-distance bound —
# the same "no lexical/orthographic delimiter at all" limitation class as
# the zero-marker participial case the distance bound itself was introduced
# to close, just narrower in practice since it additionally requires
# punctuation to have been lost upstream. This is accepted MVP risk here,
# not a defect to fix in this module.
_DISQUALIFYING_MARKER_WORD_PATTERN: Pattern[str] = re.compile(
    r"\b(?:though|but|while|although|after|and|however"
    r"|who|which|that|whose|whom"
    r"|even as|as|since|when|where|once|whereas|unless|if|because|before|until)\b",
    re.IGNORECASE,
)

# Only NQ has a mapping today: the MVP's only ingested source family is
# Fed/FOMC (`docs/architecture/overview.md`, External Integrations), so a
# rate-decision fact only has a documented, defensible interpretation for the
# NQ equity-index future. BTC/GOLD are intentionally left unmapped here
# rather than reusing the NQ mapping speculatively (see
# `ImplementationReport.assumptions`); callers requesting BTC/GOLD receive
# `uncertain`/`unknown` with a rationale explaining why.
_NQ_RATE_ACTION_TO_DIRECTION: dict[_RateAction, ImpactDirection] = {
    _RateAction.HIKE: ImpactDirection.BEARISH,
    _RateAction.CUT: ImpactDirection.BULLISH,
    _RateAction.HOLD: ImpactDirection.NEUTRAL,
}


def _rate_action_verb_matches(fact: str) -> list[tuple[_RateAction, re.Match[str]]]:
    """Return every (action, match) pair for each trigger-verb occurrence in `fact`.

    Every occurrence is returned independently, in pattern-group order
    (HIKE patterns, then CUT, then HOLD) and match order within each
    pattern — `_classify_fact` is responsible for deciding, per occurrence,
    whether it is actually related to a nearby anchor before contributing
    that action; this function does no filtering itself.
    """
    matches: list[tuple[_RateAction, re.Match[str]]] = []
    for action, patterns in (
        (_RateAction.HIKE, _HIKE_PATTERNS),
        (_RateAction.CUT, _CUT_PATTERNS),
        (_RateAction.HOLD, _HOLD_PATTERNS),
    ):
        for pattern in patterns:
            matches.extend((action, match) for match in pattern.finditer(fact))
    return matches


def _span_between(match_a: re.Match[str], match_b: re.Match[str]) -> tuple[int, int]:
    """Return the (start, end) character span strictly between two matches.

    Order-agnostic: works whether `match_a` or `match_b` occurs first in the
    string (verb-before-anchor and anchor-before-verb both work). If the two
    matches overlap or are adjacent, the returned span is empty (`end <=
    start`).
    """
    first, second = sorted((match_a, match_b), key=lambda match: match.start())
    return first.end(), second.start()


def _words_between(fact: str, match_a: re.Match[str], match_b: re.Match[str]) -> int:
    """Count whitespace-delimited, punctuation-stripped words strictly between two matches."""
    start, end = _span_between(match_a, match_b)
    if end <= start:
        return 0
    return len(_BETWEEN_SPAN_WORD_PATTERN.findall(fact[start:end]))


def _is_related(fact: str, anchor_match: re.Match[str], verb_match: re.Match[str]) -> bool:
    """Return whether `anchor_match` and `verb_match` are close enough to co-occur.

    All three conditions must hold: at most `_MAX_WORDS_BETWEEN_ANCHOR_AND_VERB`
    words separate the two matches, the span between them contains no
    character outside letters/digits/whitespace
    (`_DISALLOWED_BETWEEN_SPAN_CHARACTER_PATTERN` — an allowlist-by-complement
    that disqualifies any punctuation/symbol used as an informal clause
    joiner), and that same span contains no disqualifying connector word
    (`_DISQUALIFYING_MARKER_WORD_PATTERN`). Any one failing means the verb
    occurrence contributes no signal for this anchor; the caller does not
    fall back to a farther anchor occurrence (see `_classify_fact`).
    """
    if _words_between(fact, anchor_match, verb_match) > _MAX_WORDS_BETWEEN_ANCHOR_AND_VERB:
        return False
    start, end = _span_between(anchor_match, verb_match)
    between_span = fact[start:end]
    if _DISALLOWED_BETWEEN_SPAN_CHARACTER_PATTERN.search(between_span):
        return False
    return not _DISQUALIFYING_MARKER_WORD_PATTERN.search(between_span)


def _classify_fact(fact: str) -> list[_RateAction]:
    """Return every distinct rate action `fact` literally describes.

    Each trigger-verb occurrence in `fact` (`_rate_action_verb_matches`) is
    paired with its *nearest* anchor-phrase occurrence by word distance
    (`_words_between`), in either order; the pair contributes that action
    only if `_is_related` passes for that nearest anchor. If the nearest
    anchor fails, that verb occurrence contributes no signal — it is never
    retried against a farther anchor occurrence, preserving this module's
    "an omitted signal is preferred over a confidently wrong directional
    call" guarantee. A fact with no anchor occurrence at all short-circuits
    to no signal without examining any verb. The distinct actions found (in
    first-seen order, deduplicated) are returned: usually zero (no signal)
    or one (a clear action), but a fact whose independent anchor-verb pairs
    genuinely disagree (e.g. one pair says "raised", a different pair says
    "lowered") returns more than one action rather than silently picking a
    winner — callers turn multiple actions into the same mixed-signal
    handling used for conflicting facts across events.
    """
    anchor_matches = list(_RATE_ANCHOR_PATTERN.finditer(fact))
    if not anchor_matches:
        return []
    actions: list[_RateAction] = []
    for action, verb_match in _rate_action_verb_matches(fact):
        if action in actions:
            continue
        nearest_anchor = min(
            anchor_matches, key=lambda anchor: _words_between(fact, anchor, verb_match)
        )
        if _is_related(fact, nearest_anchor, verb_match):
            actions.append(action)
    return actions


def _classified_rate_decision_facts(events: list[Event]) -> list[_ClassifiedFact]:
    """Collect every classifiable fact from this narrative's rate-decision events.

    A fact whose independent anchor-verb pairs yield more than one distinct
    action (see `_classify_fact`) contributes one `_ClassifiedFact` per
    distinct action, all citing the same fact text; this is a deliberate
    choice so an internally self-contradictory fact is treated the same as
    conflicting facts across events, reusing `assess_impact`'s existing
    mixed-signal resolution rather than duplicating it.
    """
    classified: list[_ClassifiedFact] = []
    for event in events:
        if event.type != _RATE_DECISION_EVENT_TYPE:
            continue
        for fact in event.extracted_facts:
            if not isinstance(fact, str):
                continue
            for action in _classify_fact(fact):
                classified.append(_ClassifiedFact(action=action, fact=fact))
    return classified


def _no_signal_assessment(instrument: Instrument, *, event_count: int) -> ImpactAssessment:
    return ImpactAssessment(
        instrument=instrument,
        direction=ImpactDirection.UNCERTAIN,
        relevance=_RELEVANCE_NO_SIGNAL,
        horizon=ImpactHorizon.UNKNOWN,
        rationale=(
            f"No rate-decision event with a determinable hike/cut/hold outcome was found "
            f"among the narrative's {event_count} event(s); direction is uncertain and "
            "horizon unknown pending a clearer signal."
        ),
    )


def _unmapped_instrument_assessment(
    instrument: Instrument, classified: list[_ClassifiedFact]
) -> ImpactAssessment:
    cited_facts = "; ".join(f'"{item.fact}"' for item in classified)
    return ImpactAssessment(
        instrument=instrument,
        direction=ImpactDirection.UNCERTAIN,
        relevance=_RELEVANCE_NO_SIGNAL,
        horizon=ImpactHorizon.UNKNOWN,
        rationale=(
            f"Rate-decision fact(s) were found ({cited_facts}), but this assessor has no "
            f"documented rate-decision -> direction mapping for {instrument.value.upper()} "
            "yet; direction is uncertain and horizon unknown rather than reusing another "
            "instrument's mapping."
        ),
    )


def _mixed_signal_assessment(
    instrument: Instrument, classified: list[_ClassifiedFact]
) -> ImpactAssessment:
    cited_facts = "; ".join(f'"{item.fact}"' for item in classified)
    return ImpactAssessment(
        instrument=instrument,
        direction=ImpactDirection.MIXED,
        relevance=_RELEVANCE_MIXED_SIGNAL,
        horizon=ImpactHorizon.UNKNOWN,
        rationale=(
            f"Rate-decision facts point to conflicting outcomes ({cited_facts}); "
            f"{instrument.value.upper()} impact direction is mixed and horizon unknown "
            "until the conflict resolves."
        ),
    )


def _clear_signal_assessment(
    instrument: Instrument, action: _RateAction, classified: list[_ClassifiedFact]
) -> ImpactAssessment:
    direction = _NQ_RATE_ACTION_TO_DIRECTION[action]
    cited_facts = "; ".join(f'"{item.fact}"' for item in classified)
    relevance = min(
        _RELEVANCE_MAX,
        _RELEVANCE_CLEAR_SIGNAL_BASE
        + _RELEVANCE_PER_CORROBORATING_FACT * (len(classified) - 1),
    )
    rationale = (
        f"Rate-decision fact(s) indicate a {action.value} ({cited_facts}); assessed as "
        f"{direction.value} for {instrument.value.upper()} because a Fed rate {action.value} "
        "typically shifts risk-asset index futures in that direction, with effects "
        "expected to persist over multiple sessions rather than resolving intraday."
    )
    return ImpactAssessment(
        instrument=instrument,
        direction=direction,
        relevance=relevance,
        horizon=ImpactHorizon.MULTI_DAY,
        rationale=rationale,
    )


def assess_impact(events: list[Event], *, instrument: Instrument) -> ImpactAssessment:
    """Deterministically assess `instrument`'s impact from `events`' rate-decision content.

    `events` should be the `Event`s already assigned to one `Narrative` (its
    `NarrativeEvent`s' events); this function performs no database lookup and
    has no LLM/HTTP dependency.
    """
    classified = _classified_rate_decision_facts(events)
    if not classified:
        return _no_signal_assessment(instrument, event_count=len(events))

    if instrument is not Instrument.NQ:
        return _unmapped_instrument_assessment(instrument, classified)

    distinct_actions = {item.action for item in classified}
    if len(distinct_actions) > 1:
        return _mixed_signal_assessment(instrument, classified)

    (action,) = distinct_actions
    return _clear_signal_assessment(instrument, action, classified)
