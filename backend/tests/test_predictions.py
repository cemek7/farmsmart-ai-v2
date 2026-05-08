from httpx import AsyncClient
from tests.conftest import register_user, auth

PREDICT = {
    "crop_type": "maize",
    "seed_cost": 10000.0,
    "fertilizer_cost": 6000.0,
    "labor_cost": 20000.0,
    "irrigation_cost": 4000.0,
    "transport_cost": 3000.0,
    "farm_size": 5.0,
}


async def test_predict_returns_result(client: AsyncClient):
    token = await register_user(client, "pred_ok@test.com")
    resp = await client.post("/predict", headers=auth(token), json=PREDICT)
    assert resp.status_code == 201
    data = resp.json()
    assert data["predicted_revenue"] > 0
    assert data["model_used"] in ("personal", "community", "baseline")
    assert data["crop_type"] == "maize"


async def test_predict_stores_all_inputs(client: AsyncClient):
    token = await register_user(client, "pred_store@test.com")
    data = (await client.post("/predict", headers=auth(token), json=PREDICT)).json()
    assert data["seed_cost"] == 10000.0
    assert data["farm_size"] == 5.0


async def test_predict_invalid_crop(client: AsyncClient):
    token = await register_user(client, "pred_bad_crop@test.com")
    resp = await client.post("/predict", headers=auth(token), json={**PREDICT, "crop_type": "mango"})
    assert resp.status_code == 422


async def test_predict_empty_crop_rejected(client: AsyncClient):
    token = await register_user(client, "pred_empty@test.com")
    resp = await client.post("/predict", headers=auth(token), json={**PREDICT, "crop_type": "  "})
    assert resp.status_code == 422


async def test_predict_zero_farm_size_rejected(client: AsyncClient):
    token = await register_user(client, "pred_zero_farm@test.com")
    resp = await client.post("/predict", headers=auth(token), json={**PREDICT, "farm_size": 0.0})
    assert resp.status_code == 422


async def test_predict_history(client: AsyncClient):
    token = await register_user(client, "pred_history@test.com")
    await client.post("/predict", headers=auth(token), json=PREDICT)
    await client.post("/predict", headers=auth(token), json={**PREDICT, "crop_type": "rice"})

    resp = await client.get("/predict/history", headers=auth(token))
    assert resp.status_code == 200
    assert len(resp.json()) == 2


async def test_history_only_shows_own_predictions(client: AsyncClient):
    user1 = await register_user(client, "pred_own1@test.com")
    user2 = await register_user(client, "pred_own2@test.com")
    await client.post("/predict", headers=auth(user1), json=PREDICT)

    resp = await client.get("/predict/history", headers=auth(user2))
    assert resp.json() == []


async def test_unauthenticated_rejected(client: AsyncClient):
    assert (await client.post("/predict", json=PREDICT)).status_code == 401
