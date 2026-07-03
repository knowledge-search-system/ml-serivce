from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile

from app.deps import get_upload_service
from app.schemas import UploadOut
from app.services.upload import UploadService

router = APIRouter(prefix="/api/v1/documents")


@router.post("")
async def upload_document(
    service: Annotated[UploadService, Depends(get_upload_service)], file: UploadFile
) -> UploadOut:
    content = await file.read()
    result = await service.upload(file.filename or "unnamed", content)
    return UploadOut(id=result.id, file_name=result.file_name, chunks=result.chunks)
