"""Deterministic `canonical_key` derivation for narrative identity.

Per `docs/architecture/domain-model.md` (Invariants, Protected Semantics), a
`Narrative`'s identity is always semantic (`canonical_key`-based), never a
transient cluster-hash of whichever events happened to be grouped together
in one processing run. This module hashes only fields that already live on
the `Event` being assigned (`type`, `entities`, `topics`), never anything
derived from a specific batch/cluster of events — so two `Event`s with the
same normalized semantic identity always produce the same key, regardless of
when or in what batch they were extracted.

Provisional MVP convention (see `ImplementationReport.assumptions`): this is
a single-source assumption — it treats each entity/topic string as already
canonical (e.g. "Federal Reserve" vs. "Fed" are *not* currently reconciled to
the same key) because Milestone 1 ingests from one source family at a time.
This is expected to be revisited once Milestone 2 broadens ingestion to
multiple sources with potentially inconsistent entity naming (i.e. entity
resolution/aliasing becomes necessary).
"""

from __future__ import annotations

import hashlib

from market_intel.persistence.models import Event


def compute_canonical_key(event: Event) -> str:
    """Derive `event`'s narrative-identity key from its normalized type/entities/topics.

    Normalization (case/whitespace folding, dedup, sort) makes the key
    independent of input ordering and superficial casing/spacing
    differences, so the same underlying semantic identity always maps to
    the same key. The result is a fixed-length sha256 hex digest so it fits
    a compact, indexed column regardless of how many entities/topics an
    `Event` carries.
    """
    normalized_type = _normalize_term(event.type) or "unspecified"
    normalized_entities = _normalize_terms(event.entities)
    normalized_topics = _normalize_terms(event.topics)

    key_material = "&".join(
        [
            f"type={normalized_type}",
            "entities=" + ",".join(normalized_entities),
            "topics=" + ",".join(normalized_topics),
        ]
    )
    return hashlib.sha256(key_material.encode("utf-8")).hexdigest()


def _normalize_term(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(value.strip().lower().split())


def _normalize_terms(values: list) -> list[str]:
    normalized = {
        _normalize_term(value)
        for value in values
        if isinstance(value, str) and _normalize_term(value)
    }
    return sorted(normalized)
