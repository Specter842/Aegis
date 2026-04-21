from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.models import DocumentModel

class DocumentsRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_document(self, doc: DocumentModel) -> DocumentModel:
        self.session.add(doc)
        await self.session.flush()
        return doc
        
    async def get_document_by_id(self, document_id: str) -> DocumentModel | None:
        stmt = select(DocumentModel).where(DocumentModel.document_id == document_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_document_by_pk(self, pk: int) -> DocumentModel | None:
        return await self.session.get(DocumentModel, pk)

    async def list_documents(self, tenant_id: str, limit: int = 50, offset: int = 0) -> list[DocumentModel]:
        stmt = select(DocumentModel).where(DocumentModel.tenant_id == tenant_id).order_by(desc(DocumentModel.created_at)).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
