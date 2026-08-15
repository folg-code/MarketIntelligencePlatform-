"""Narrative engine.

Assigns extracted events to `NarrativeEvent`s and manages narrative
lifecycle/dynamics state, using semantic (`canonical_key`) identity. Consumes
already-extracted facts/claims; does not call external APIs or the LLM
directly.
"""
