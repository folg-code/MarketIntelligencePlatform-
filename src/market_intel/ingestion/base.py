"""Interface for source-specific ingestion adapters.

Business logic and calling code must depend on `DocumentSourceAdapter`, not
on a concrete adapter or on any external source's transport/format
directly (see `docs/architecture/overview.md`, Responsibilities And
Boundaries: ingestion adapters isolate external integrations from business
logic).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from market_intel.persistence.models import Document


class DocumentSourceAdapter(ABC):
    """Fetches, parses, and normalizes one external source into `Document`s."""

    @abstractmethod
    async def fetch_documents(self) -> list[Document]:
        """Fetch new/available content from the source as normalized `Document`s.

        Returned `Document` instances are not yet persisted; callers decide
        how and whether to store them (e.g. de-duplicating by `url`).
        """
