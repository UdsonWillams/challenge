import sys

from httpx import ASGITransport, AsyncClient

from app.database.unit_of_work import get_uow

sys.path.append("app/")

import pytest
import pytest_asyncio

# This will automatically include the fixtures from the specified modules
# Need to update this list as you add more fixture files
pytest_plugins = [
    "tests.fixtures.database",
    "tests.fixtures.base",
]


@pytest.fixture(scope="session")
def app(uow):
    from app.main import app

    app.dependency_overrides[get_uow] = lambda: uow
    yield app


@pytest_asyncio.fixture(scope="function")
async def client(async_session, uow):
    from starlette.routing import _DefaultLifespan

    from app.main import app

    app.dependency_overrides[get_uow] = lambda: uow
    app.router.lifespan_context = _DefaultLifespan(app.router)
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://localhost"
    ) as ac:
        yield ac


@pytest_asyncio.fixture(scope="function")
async def admin_headers(client, customer_admin):
    resp = await client.post(
        "/auth/token",
        json={"email": customer_admin.email, "password": customer_admin.plain_password},
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
