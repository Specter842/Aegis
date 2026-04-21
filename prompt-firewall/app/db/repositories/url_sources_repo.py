from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.models import UrlSourceModel

class UrlSourcesRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_url_source(self, src: UrlSourceModel) -> UrlSourceModel:
        self.session.add(src)
        await self.session.flush()
        return src
        
    async def get_url_source_by_id(self, url_id: str) -> UrlSourceModel | None:
        stmt = select(UrlSourceModel).where(UrlSourceModel.url_id == url_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_url_source_by_pk(self, pk: int) -> UrlSourceModel | None:
        return await self.session.get(UrlSourceModel, pk)

    async def list_url_sources(self, tenant_id: str, limit: int = 50, offset: int = 0) -> list[UrlSourceModel]:
        stmt = select(UrlSourceModel).where(UrlSourceModel.tenant_id == tenant_id).order_by(desc(UrlSourceModel.created_at)).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
