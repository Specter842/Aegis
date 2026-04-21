from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import OutputScanModel

class OutputRepo:
    def __init__(self, session: AsyncSession):
        self._session = session
        
    async def create(self, scan: OutputScanModel) -> OutputScanModel:
        self._session.add(scan)
        await self._session.commit()
        await self._session.refresh(scan)
        return scan
