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
anchor phrase ("target range" or "federal funds rate") within the same
*clause* of the fact string (see `_split_into_clauses`/`_classify_clause`).
Clause-scoping means the anchor and verb must appear on the same side of any
comma, semicolon, or contrast/coordinating conjunction ("though", "but",
"while", "although", "after", "and", "however"); a trigger verb in a different clause
from the anchor (e.g. "...target range unchanged after some members raised
objections") contributes no signal from that unrelated clause, and a bare
trigger verb with no anchor anywhere in the fact (e.g. "The Chair raised
concerns about inflation risks") contributes no signal at all. This is a
best-effort heuristic split, not a syntactic parse: it can under-split (an
anchor and verb genuinely belonging together but separated by, e.g., an
appositive comma will fail to co-occur in one clause and the fact will
fall through to no-signal rather than being classified) or, in principle,
mis-split unusual phrasing; the guarantee this module makes is narrower than
"correctly parses arbitrary English" — it is that a verb from one
plainly-distinct clause cannot masquerade as evidence for an anchor in
another. Falling through to no signal on ambiguous/under-split phrasing is
intentional: an omitted signal is preferred over a confidently wrong
directional call. This module also gates on `Event.type == "rate_decision"`,
but that upstream Event-level classification is not by itself treated as
sufficient evidence that any given fact under the event literally describes
the rate action; the clause-scoped anchor+verb check on the fact text is
what determines what the Fed actually did. A single fact whose clauses
independently yield different actions (e.g. one clause says "raised", a
different clause says "lowered") contributes one classified entry per
distinct clause-level action, which feeds the same mixed-signal handling
used for conflicting facts across events (see `_classified_rate_decision_facts`).
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
# ("never inferred from keywords alone") — the verb and the anchor must both
# be literally present in the same *clause* (see `_split_into_clauses`), not
# merely the same fact string, or an unrelated clause's verb could bleed
# into an anchor clause that describes a different (or no) action.
_RATE_ANCHOR_PATTERN: Pattern[str] = re.compile(
    r"\b(?:target range|federal funds rate)\b", re.IGNORECASE
)

# Clause boundary: a comma/semicolon, or one of the common contrast/
# coordinating conjunctions that typically introduce a new subject-verb
# clause in this kind of statement. This is a heuristic textual split, not a
# grammatical parse — see the module docstring for what it does and does not
# guarantee. "and" is deliberately included despite being a coordinator
# rather than a contrast word: without it, a single clause like "...target
# range unchanged and one member raised objections" would let "raised"
# (HIKE) win over "unchanged" (HOLD) purely because of `_classify_clause`'s
# internal HIKE-before-HOLD priority, reproducing the exact cross-clause
# bleed this fix exists to prevent.
_CLAUSE_DELIMITER_PATTERN: Pattern[str] = re.compile(
    r"[,;]|\b(?:though|but|while|although|after|and|however)\b",
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


def _split_into_clauses(fact: str) -> list[str]:
    """Split `fact` into clause-sized chunks on `_CLAUSE_DELIMITER_PATTERN`.

    Purely textual heuristic (no grammar/parse tree): good enough to keep an
    anchor and verb from a genuinely unrelated clause from being read as
    co-occurring, not good enough to guarantee every real clause boundary in
    arbitrary English is found. Empty/whitespace-only segments (e.g. from a
    delimiter at the very start or two adjacent delimiters) are dropped.
    """
    return [clause for clause in _CLAUSE_DELIMITER_PATTERN.split(fact) if clause.strip()]


def _classify_clause(clause: str) -> _RateAction | None:
    """Return the rate action one clause literally describes, or `None`.

    A bare action verb is never sufficient: `clause` must also contain a
    rate/target-range anchor ("target range" or "federal funds rate") in
    this same clause, or the verb is assumed to describe something else
    entirely (e.g. "raised concerns", "cut short", "held a briefing") and no
    signal is produced. If a clause somehow contains verbs for more than one
    action (unusual — this generally indicates two actions got merged into
    one clause by an under-split), HIKE is preferred over CUT over HOLD,
    mirroring the priority the original whole-fact check used.
    """
    if not _RATE_ANCHOR_PATTERN.search(clause):
        return None
    if any(pattern.search(clause) for pattern in _HIKE_PATTERNS):
        return _RateAction.HIKE
    if any(pattern.search(clause) for pattern in _CUT_PATTERNS):
        return _RateAction.CUT
    if any(pattern.search(clause) for pattern in _HOLD_PATTERNS):
        return _RateAction.HOLD
    return None


def _classify_fact(fact: str) -> list[_RateAction]:
    """Return every distinct rate action `fact` literally describes, clause-scoped.

    `fact` is split into clauses (`_split_into_clauses`) and each clause is
    classified independently (`_classify_clause`); an anchor in one clause
    can never combine with a verb from a different clause. The distinct
    actions found (in first-seen order, deduplicated) are returned: usually
    zero (no signal) or one (a clear action), but a fact whose clauses
    genuinely disagree (e.g. one clause says "raised", another says
    "lowered") returns more than one action rather than silently picking a
    winner — callers turn multiple actions into the same mixed-signal
    handling used for conflicting facts across events.
    """
    actions: list[_RateAction] = []
    for clause in _split_into_clauses(fact):
        action = _classify_clause(clause)
        if action is not None and action not in actions:
            actions.append(action)
    return actions


def _classified_rate_decision_facts(events: list[Event]) -> list[_ClassifiedFact]:
    """Collect every classifiable fact from this narrative's rate-decision events.

    A fact whose clauses yield more than one distinct action (see
    `_classify_fact`) contributes one `_ClassifiedFact` per distinct action,
    all citing the same fact text; this is a deliberate choice so an
    internally self-contradictory fact is treated the same as conflicting
    facts across events, reusing `assess_impact`'s existing mixed-signal
    resolution rather than duplicating it.
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
