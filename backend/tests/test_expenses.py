from httpx import AsyncClient
from tests.conftest import register_user, auth

EXPENSE = {
    "crop_type": "Maize",  # intentionally mixed-case — should be normalised
    "seed_cost": 10000.0,
    "fertilizer_cost": 6000.0,
    "labor_cost": 20000.0,
    "irrigation_cost": 4000.0,
    "transport_cost": 3000.0,
    "other_cost": 0.0,
    "farm_size": 5.0,
    "date": "2026-05-01",
}


async def test_list_empty(client: AsyncClient):
    token = await register_user(client, "list_exp@test.com")
    resp = await client.get("/expenses", headers=auth(token))
    assert resp.status_code == 200
    assert resp.json() == []


async def test_create_expense(client: AsyncClient):
    token = await register_user(client, "create_exp@test.com")
    resp = await client.post("/expenses", headers=auth(token), json=EXPENSE)
    assert resp.status_code == 201
    data = resp.json()
    assert data["crop_type"] == "maize"  # normalised to lowercase
    assert data["total"] == 43000.0


async def test_get_expense(client: AsyncClient):
    token = await register_user(client, "get_exp@test.com")
    created = (await client.post("/expenses", headers=auth(token), json=EXPENSE)).json()
    resp = await client.get(f"/expenses/{created['id']}", headers=auth(token))
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


async def test_update_expense(client: AsyncClient):
    token = await register_user(client, "upd_exp@test.com")
    created = (await client.post("/expenses", headers=auth(token), json=EXPENSE)).json()
    resp = await client.put(
        f"/expenses/{created['id']}", headers=auth(token), json={"seed_cost": 20000.0}
    )
    assert resp.status_code == 200
    assert resp.json()["seed_cost"] == 20000.0
    assert resp.json()["total"] == 53000.0


async def test_delete_expense(client: AsyncClient):
    token = await register_user(client, "del_exp@test.com")
    created = (await client.post("/expenses", headers=auth(token), json=EXPENSE)).json()
    resp = await client.delete(f"/expenses/{created['id']}", headers=auth(token))
    assert resp.status_code == 204
    assert (await client.get(f"/expenses/{created['id']}", headers=auth(token))).status_code == 404


async def test_cannot_read_other_users_expense(client: AsyncClient):
    owner = await register_user(client, "owner_exp@test.com")
    other = await register_user(client, "other_exp@test.com")
    created = (await client.post("/expenses", headers=auth(owner), json=EXPENSE)).json()
    assert (await client.get(f"/expenses/{created['id']}", headers=auth(other))).status_code == 404


async def test_cannot_update_other_users_expense(client: AsyncClient):
    owner = await register_user(client, "owner_upd_exp@test.com")
    other = await register_user(client, "other_upd_exp@test.com")
    created = (await client.post("/expenses", headers=auth(owner), json=EXPENSE)).json()
    resp = await client.put(
        f"/expenses/{created['id']}", headers=auth(other), json={"seed_cost": 1.0}
    )
    assert resp.status_code == 404


async def test_cannot_delete_other_users_expense(client: AsyncClient):
    owner = await register_user(client, "owner_del_exp@test.com")
    other = await register_user(client, "other_del_exp@test.com")
    created = (await client.post("/expenses", headers=auth(owner), json=EXPENSE)).json()
    assert (await client.delete(f"/expenses/{created['id']}", headers=auth(other))).status_code == 404


async def test_negative_cost_rejected(client: AsyncClient):
    token = await register_user(client, "neg_exp@test.com")
    resp = await client.post("/expenses", headers=auth(token), json={**EXPENSE, "seed_cost": -1.0})
    assert resp.status_code == 422


async def test_zero_farm_size_rejected(client: AsyncClient):
    token = await register_user(client, "zero_farm@test.com")
    resp = await client.post("/expenses", headers=auth(token), json={**EXPENSE, "farm_size": 0.0})
    assert resp.status_code == 422


async def test_empty_crop_type_rejected(client: AsyncClient):
    token = await register_user(client, "empty_crop_exp@test.com")
    resp = await client.post("/expenses", headers=auth(token), json={**EXPENSE, "crop_type": "  "})
    assert resp.status_code == 422


async def test_unauthenticated_rejected(client: AsyncClient):
    assert (await client.get("/expenses")).status_code == 401
