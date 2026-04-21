from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.models import DocumentChunkModel

class DocumentChunksRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_chunks(self, chunks: list[DocumentChunkModel]):
        self.session.add_all(chunks)
        await self.session.flush()

    async def get_chunks_for_document(self, doc_pk: int) -> list[DocumentChunkModel]:
        stmt = select(DocumentChunkModel).where(DocumentChunkModel.document_fk == doc_pk).order_by(DocumentChunkModel.chunk_index)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
