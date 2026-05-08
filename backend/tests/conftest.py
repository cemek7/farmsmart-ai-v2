import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


async def register_user(client: AsyncClient, email: str, password: str = "Password1!", name: str = "Test Farmer") -> str:
    """Register a user and return their JWT access token."""
    resp = await client.post("/auth/register", json={"name": name, "email": email, "password": password})
    assert resp.status_code == 201, resp.text
    return resp.json()["access_token"]


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="session", autouse=True)
def ensure_baseline_model():
    """Train baseline model once per test session if it doesn't exist yet."""
    from app.ml.train_models import MODELS_DIR, train_baseline
    if not os.path.exists(os.path.join(MODELS_DIR, "baseline.joblib")):
        train_baseline()


@pytest_asyncio.fixture
async def client():
    """Fresh in-memory SQLite DB per test — full isolation, no cleanup needed."""
    from app.main import app as fastapi_app
    from app.database import Base, get_db
    import app.models  # noqa — registers all models with Base

    engine = create_async_engine(TEST_DATABASE_URL)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def _override():
        async with session_factory() as session:
            try:
                yield session
            finally:
                await session.close()

    fastapi_app.dependency_overrides[get_db] = _override

    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as ac:
        yield ac

    fastapi_app.dependency_overrides.pop(get_db, None)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
