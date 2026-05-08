from httpx import AsyncClient
from tests.conftest import register_user, auth

EXPENSE = {
    "crop_type": "maize", "seed_cost": 10000.0, "fertilizer_cost": 6000.0,
    "labor_cost": 20000.0, "irrigation_cost": 4000.0, "transport_cost": 3000.0,
    "other_cost": 0.0, "farm_size": 5.0, "date": "2026-05-01",
}
INCOME = {"crop_type": "maize", "amount": 80000.0, "quantity": 1500.0, "date": "2026-09-01"}


async def test_list_empty(client: AsyncClient):
    token = await register_user(client, "list_inc@test.com")
    resp = await client.get("/income", headers=auth(token))
    assert resp.status_code == 200
    assert resp.json() == []


async def test_create_without_link(client: AsyncClient):
    token = await register_user(client, "create_inc@test.com")
    resp = await client.post("/income", headers=auth(token), json=INCOME)
    assert resp.status_code == 201
    data = resp.json()
    assert data["amount"] == 80000.0
    assert data["is_paired"] is False
    assert data["expense_id"] is None


async def test_create_with_valid_expense_link(client: AsyncClient):
    token = await register_user(client, "linked_inc@test.com")
    expense_id = (await client.post("/expenses", headers=auth(token), json=EXPENSE)).json()["id"]
    resp = await client.post("/income", headers=auth(token), json={**INCOME, "expense_id": expense_id})
    assert resp.status_code == 201
    data = resp.json()
    assert data["expense_id"] == expense_id
    assert data["is_paired"] is True


async def test_cross_user_expense_link_silently_dropped(client: AsyncClient):
    owner = await register_user(client, "owner_inc@test.com")
    attacker = await register_user(client, "attacker_inc@test.com")
    expense_id = (await client.post("/expenses", headers=auth(owner), json=EXPENSE)).json()["id"]
    # Attacker tries to link their income to owner's expense
    resp = await client.post("/income", headers=auth(attacker), json={**INCOME, "expense_id": expense_id})
    assert resp.status_code == 201
    assert resp.json()["expense_id"] is None  # silently dropped
    assert resp.json()["is_paired"] is False


async def test_update_income(client: AsyncClient):
    token = await register_user(client, "upd_inc@test.com")
    created = (await client.post("/income", headers=auth(token), json=INCOME)).json()
    resp = await client.put(
        f"/income/{created['id']}", headers=auth(token), json={"amount": 90000.0}
    )
    assert resp.status_code == 200
    assert resp.json()["amount"] == 90000.0


async def test_delete_income(client: AsyncClient):
    token = await register_user(client, "del_inc@test.com")
    created = (await client.post("/income", headers=auth(token), json=INCOME)).json()
    resp = await client.delete(f"/income/{created['id']}", headers=auth(token))
    assert resp.status_code == 204
    assert (await client.get(f"/income/{created['id']}", headers=auth(token))).status_code == 404


async def test_cannot_access_other_users_income(client: AsyncClient):
    owner = await register_user(client, "owner_get_inc@test.com")
    other = await register_user(client, "other_get_inc@test.com")
    created = (await client.post("/income", headers=auth(owner), json=INCOME)).json()
    assert (await client.get(f"/income/{created['id']}", headers=auth(other))).status_code == 404


async def test_zero_amount_rejected(client: AsyncClient):
    token = await register_user(client, "zero_amt@test.com")
    resp = await client.post("/income", headers=auth(token), json={**INCOME, "amount": 0.0})
    assert resp.status_code == 422


async def test_empty_crop_type_rejected(client: AsyncClient):
    token = await register_user(client, "empty_crop_inc@test.com")
    resp = await client.post("/income", headers=auth(token), json={**INCOME, "crop_type": ""})
    assert resp.status_code == 422


async def test_unauthenticated_rejected(client: AsyncClient):
    assert (await client.get("/income")).status_code == 401
