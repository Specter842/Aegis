import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.session import engine
from app.db.models import Base
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

test_session_maker = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
async def db_schema():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session():
    async with test_session_maker() as session:
        yield session

@pytest.fixture
async def app_client():
    from app.main import lifespan
    async with lifespan(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            yield client
