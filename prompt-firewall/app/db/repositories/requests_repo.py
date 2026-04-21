from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import ScanRequestModel

class RequestsRepo:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    def add(self, request_data: dict) -> ScanRequestModel:
        model = ScanRequestModel(**request_data)
        self.session.add(model)
        return model

    async def get_by_trace_id(self, trace_id: str) -> ScanRequestModel:
        from sqlalchemy.future import select
        stmt = select(ScanRequestModel).where(ScanRequestModel.trace_id == trace_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()
