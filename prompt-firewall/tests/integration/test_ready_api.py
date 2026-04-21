import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_health_api(app_client: AsyncClient):
    resp = await app_client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "alive"

@pytest.mark.asyncio
async def test_ready_api(app_client: AsyncClient):
    # During tests, LLM Guard may not load models instantly, or YARA might be missing
    # We just want to check that the structure is correct.
    resp = await app_client.get("/ready")
    
    data = resp.json()
    assert "components" in data
    assert "database" in data["components"]
    
    # DB Should be ready in test
    assert data["components"]["database"]["is_ready"] is True
    
    # Verify critical failure logic works (if any component failed, HTTP is 503)
    has_critical_failure = any(
        c["is_critical"] and not c["is_ready"] 
        for c in data["components"].values()
    )
    
    if has_critical_failure:
        assert resp.status_code == 503
        assert data["status"] == "not_ready"
    else:
        assert resp.status_code == 200
        assert data["status"] == "ready"
