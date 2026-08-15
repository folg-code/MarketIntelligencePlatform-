"""Smoke tests proving the project skeleton and test setup work."""

import market_intel
from market_intel.main import app, health


def test_package_imports() -> None:
    assert market_intel.__doc__ is not None


def test_fastapi_app_is_importable() -> None:
    assert app.title == "Market Intelligence Platform"


async def test_health_endpoint_smoke() -> None:
    """Calls the health route handler directly, proving async test wiring works."""
    result = await health()

    assert result == {"status": "ok"}
