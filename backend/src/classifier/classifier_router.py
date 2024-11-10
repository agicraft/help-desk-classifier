import logging
from fastapi import APIRouter, Request

from .classifier_service import get_classifier_service


from .classifier_dto import (
    ClassifiedMessageDto,
    ClassifyingMessageDto,
    ClassifierSchemaDto,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/classifier")


@router.get("/schema", response_model=ClassifierSchemaDto)
async def schema(request: Request):
    service = get_classifier_service(request.state)
    return service.get_schema()


@router.post("/classify", response_model=ClassifiedMessageDto)
async def classify(
    body: ClassifyingMessageDto, request: Request
) -> ClassifiedMessageDto:
    service = get_classifier_service(request.state)
    return service.classify(body)
