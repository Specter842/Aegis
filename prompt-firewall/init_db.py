import asyncio
from app.db.session import engine
from app.db.models import Base

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database initialized.")

if __name__ == "__main__":
    asyncio.run(init_db())
