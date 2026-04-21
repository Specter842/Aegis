from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import CanaryEventModel

class CanaryRepo:
    def __init__(self, session: AsyncSession):
        self._session = session
        
    async def create(self, event: CanaryEventModel) -> CanaryEventModel:
        self._session.add(event)
        await self._session.commit()
        await self._session.refresh(event)
        return event
        
    async def update(self, event: CanaryEventModel) -> CanaryEventModel:
        await self._session.commit()
        await self._session.refresh(event)
        return event
