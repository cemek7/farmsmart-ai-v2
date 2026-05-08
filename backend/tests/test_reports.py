from httpx import AsyncClient
from tests.conftest import register_user, auth

EXPENSE = {
    "crop_type": "maize", "seed_cost": 10000.0, "fertilizer_cost": 6000.0,
    "labor_cost": 20000.0, "irrigation_cost": 4000.0, "transport_cost": 3000.0,
    "other_cost": 0.0, "farm_size": 5.0, "date": "2026-05-01",
}
INCOME = {"crop_type": "maize", "amount": 80000.0, "quantity": 1500.0, "date": "2026-09-01"}


async def test_empty_report(client: AsyncClient):
    token = await register_user(client, "empty_report@test.com")
    resp = await client.get("/reports", headers=auth(token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_expense"] == 0.0
    assert data["total_income"] == 0.0
    assert data["net_profit"] == 0.0


async def test_report_totals(client: AsyncClient):
    token = await register_user(client, "totals_report@test.com")
    await client.post("/expenses", headers=auth(token), json=EXPENSE)
    await client.post("/income", headers=auth(token), json=INCOME)

    resp = await client.get("/reports", headers=auth(token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_expense"] == 43000.0
    assert data["total_income"] == 80000.0
    assert data["net_profit"] == 37000.0


async def test_report_crop_breakdown(client: AsyncClient):
    token = await register_user(client, "breakdown_report@test.com")
    await client.post("/expenses", headers=auth(token), json=EXPENSE)
    await client.post("/expenses", headers=auth(token), json={**EXPENSE, "crop_type": "rice", "seed_cost": 15000.0})
    await client.post("/income", headers=auth(token), json=INCOME)

    data = (await client.get("/reports", headers=auth(token))).json()
    assert "maize" in data["expense_by_crop"]
    assert "rice" in data["expense_by_crop"]
    assert "maize" in data["income_by_crop"]


async def test_report_only_shows_own_data(client: AsyncClient):
    user1 = await register_user(client, "user1_report@test.com")
    user2 = await register_user(client, "user2_report@test.com")
    await client.post("/expenses", headers=auth(user1), json=EXPENSE)

    data = (await client.get("/reports", headers=auth(user2))).json()
    assert data["total_expense"] == 0.0


async def test_unauthenticated_rejected(client: AsyncClient):
    assert (await client.get("/reports")).status_code == 401
