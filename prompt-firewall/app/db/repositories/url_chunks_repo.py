from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.models import UrlChunkModel

class UrlChunksRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_chunks(self, chunks: list[UrlChunkModel]):
        self.session.add_all(chunks)
        await self.session.flush()

    async def get_chunks_for_url_source(self, url_src_pk: int) -> list[UrlChunkModel]:
        stmt = select(UrlChunkModel).where(UrlChunkModel.url_source_fk == url_src_pk).order_by(UrlChunkModel.chunk_index)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
