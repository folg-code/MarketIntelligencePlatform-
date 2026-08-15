"""Ingestion adapters.

Source-specific fetch/parse/normalize of raw source content into
`Document` records. External sources (Fed/FOMC, BLS, SEC, news/RSS) are
reached only through adapters in this package; business logic elsewhere
must not call external APIs directly.
"""
