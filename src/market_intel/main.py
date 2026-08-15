"""FastAPI application entry point.

Minimal skeleton exposing a health-check endpoint. Pipeline routes,
dashboard content, and scheduler wiring are added by later tickets.
"""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(title="Market Intelligence Platform")


@app.get("/health")
async def health() -> dict[str, str]:
    """Liveness check; does not touch the database or the scheduler."""
    return {"status": "ok"}
