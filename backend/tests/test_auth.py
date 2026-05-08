from httpx import AsyncClient

BASE_PAYLOAD = {
    "name": "Test Farmer",
    "password": "securepass123",
}


async def test_register_returns_token(client: AsyncClient):
    payload = {**BASE_PAYLOAD, "email": "register_ok@test.com"}
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_register_duplicate_email(client: AsyncClient):
    payload = {**BASE_PAYLOAD, "email": "duplicate@test.com"}
    await client.post("/auth/register", json=payload)
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 409


async def test_login_valid_credentials(client: AsyncClient):
    await client.post("/auth/register", json={**BASE_PAYLOAD, "email": "login@test.com"})
    response = await client.post(
        "/auth/login",
        json={"email": "login@test.com", "password": "securepass123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


async def test_login_wrong_password(client: AsyncClient):
    await client.post("/auth/register", json={**BASE_PAYLOAD, "email": "wrong@test.com"})
    response = await client.post(
        "/auth/login",
        json={"email": "wrong@test.com", "password": "badpassword"},
    )
    assert response.status_code == 401


async def test_get_me(client: AsyncClient):
    reg = await client.post(
        "/auth/register", json={**BASE_PAYLOAD, "email": "me@test.com"}
    )
    token = reg.json()["access_token"]
    response = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@test.com"
    assert data["name"] == "Test Farmer"


async def test_get_me_no_token(client: AsyncClient):
    response = await client.get("/auth/me")
    assert response.status_code == 401
