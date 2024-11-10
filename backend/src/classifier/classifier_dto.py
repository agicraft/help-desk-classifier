from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BaseDtoModel(BaseModel):
    model_config = ConfigDict(
        strict=True,
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel,
    )


class ClassifierSchemaDto(BaseDtoModel):
    attribute_labels: Dict[str, str]


class ClassifyingMessageDto(BaseDtoModel):
    name: Optional[str] = None
    topic: Optional[str] = None
    text: str
    generate_answer: bool = False


class ClassifierAttributeDto(BaseDtoModel):
    name: str
    value: Any


class ClassifiedMessageDto(BaseDtoModel):
    valid: bool
    attributes: List[ClassifierAttributeDto]
    missing_attributes: List[str]
    keywords: List[str]
    answer: Optional[str]
