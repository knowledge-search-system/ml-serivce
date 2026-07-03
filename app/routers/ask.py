from typing import Annotated

from fastapi import APIRouter, Depends

from app.deps import get_ask_service
from app.schemas import AskIn, AskOut, SourceOut
from app.services.ask import AskService

router = APIRouter(prefix="/api/v1/ask")


@router.post("")
async def ask(service: Annotated[AskService, Depends(get_ask_service)], payload: AskIn) -> AskOut:
    result = await service.ask(payload.question)
    return AskOut(
        answer=result.answer,
        sources=[SourceOut(file_name=file_name, page=page) for file_name, page in result.sources],
    )
