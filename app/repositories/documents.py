from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Document


class DocumentRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, file_name: str) -> Document:
        document = Document(file_name=file_name)
        self._session.add(document)
        await self._session.flush()
        return document
