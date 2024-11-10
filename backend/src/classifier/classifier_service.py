from dataclasses import dataclass
import logging
from typing import Any, Dict, Optional, List

from pydantic import BaseModel
import os
import re
from ..utils.collections import flatten_list
from ..utils.llm import llm_chat_request

from .classifier_dto import (
    ClassifiedMessageDto,
    ClassifierAttributeDto,
    ClassifierSchemaDto,
    ClassifyingMessageDto,
)

logger = logging.getLogger(__name__)

DS_ATTR_SERIAL_EMPTY = "Уточнить"
CLASSIFIER_SERVICE_NAME = "classifier_service"
MAX_TEXT_LEN = 2048
MAX_TOPIC_LEN = 512
MAX_NAME_LEN = 64
SPACES_REGEX = re.compile(r"[  \t]{2,}")
DASHES_REGEX = re.compile(r"-{2,}")


@dataclass
class SchemaAttribute:
    name: str
    title: str
    examples: List[str]
    enum: bool = False
    convert_latin: bool = False
    upper_case: bool = False
    hint: Optional[str] = None
    empty_placeholder: Optional[str] = None


@dataclass
class ValidationResult:
    valid: bool
    missing_attributes: List[str]
    valid_attributes: Dict[str, Any]


API_ATTR_SERIAL = "serial_number"
API_ATTR_FAILURE_POINT = "failure_point"
API_ATTR_EQUIPMENT_TYPE = "equipment_type"


schema_attributes = [
    SchemaAttribute(
        API_ATTR_EQUIPMENT_TYPE,
        "Тип оборудования",
        ["Ноутбук", "Сервер", "Коммутатор", "Точка доступа", "Контролллер"],
        enum=True,
    ),
    SchemaAttribute(
        API_ATTR_FAILURE_POINT,
        "Точка отказа",
        [
            "Jack",
            "SFP модуль",
            "Wi-fi антенна",
            "Wi-fi модуль",
            "Аккумулятор",
            "Блок питания",
            "Вентилятор",
            "Динамики",
            "Диск",
            "Камера",
            "Клавиатура",
            "Консультация",
            "Корпус",
            "Материнская плата",
            "Матрица",
            "Оперативная память",
            "Программное обеспечение",
            "Сервер",
        ],
        hint="Try to understand and logically infer one of suggested values. This attribute generally means what part or module was broken in equipment.",
        enum=True,
    ),
    SchemaAttribute(
        API_ATTR_SERIAL,
        "Серийный номер",
        ["C253140360", "CKM01230505747", "D119990456", "E2440311114"],
        hint="It must be some kind of serial number of equipment.",
        empty_placeholder=DS_ATTR_SERIAL_EMPTY,
        convert_latin=True,
    ),
]


class LlmClassificationResponse(BaseModel):
    attributes: Dict[str, Optional[str]]


system_prompt = "You are an assistant in the help desk of a company that manufactures micro electronics devices"

prompt_classification_response_json = """
{
  "attributes": {
    "attribute_name_1": "attribute_1_value",
    "attribute_name_2": "attribute_2_value"
    ...
  }
}
"""


def normalize_classification_result(
    data: LlmClassificationResponse,
) -> LlmClassificationResponse:
    data.attributes = {key: value for (key, value) in data.attributes.items() if value}
    return data


def validate_classification_result(data: LlmClassificationResponse) -> ValidationResult:
    attrs = data.attributes
    missing_attributes = []
    valid_attributes = {}
    valid = True
    for attr in schema_attributes:
        value: Optional[str]
        if attr.name not in attrs:
            missing_attributes.append(attr.name)
            valid = False
            value = None
        else:
            value = attrs[attr.name]

        if value:
            if attr.upper_case:
                value = value.upper()
            if attr.convert_latin:
                value = translit(value)

        if value == None and attr.empty_placeholder:
            value = attr.empty_placeholder

        valid_attributes[attr.name] = value

    return ValidationResult(
        valid=valid,
        missing_attributes=missing_attributes,
        valid_attributes=valid_attributes,
    )


class ClassifierService:

    def get_schema(self) -> ClassifierSchemaDto:
        return ClassifierSchemaDto(
            attribute_labels={attr.name: attr.title for attr in schema_attributes}
        )

    def generate_answer(self, name: str, validation_result: ValidationResult):
        if name:
            ret = f"Здравствуйте, {name}!"
        else:
            ret = "Здравствуйте!"

        attributes_prompt_schema: List[str] = []
        for attr in schema_attributes:
            if not attr.name in validation_result.missing_attributes:
                continue
            attributes_prompt_schema.append(f"- {attr.title}")

        ret += f"""
Спасибо, что обратились в нашу службу поддержки! Чтобы мы могли максимально эффективно и оперативно помочь вам с вашей проблемой, нам потребуется дополнительная информация.

Пожалуйста, укажите следующие данные:
{"\n".join(attributes_prompt_schema)}

Как только мы получим эти данные, наши специалисты смогут более точно диагностировать проблему и предложить возможные решения.

Спасибо за сотрудничество!
"""

        return ret

    def classify(self, body: ClassifyingMessageDto) -> ClassifiedMessageDto:
        topic = normalize_user_str(body.topic, max_len=MAX_TOPIC_LEN, title="Topic")
        text = normalize_user_str(body.text, max_len=MAX_TEXT_LEN, title="Text")
        customer_name = normalize_user_str(
            body.name, max_len=MAX_NAME_LEN, title="Name"
        )

        attributes_prompt_schema: List[str] = []
        for attr in schema_attributes:
            attr_schema = f"Attribute with name '{attr.name}'."
            if attr.hint:
                attr_schema += f" {attr.hint}"
            if attr.enum:
                attr_schema += " Exact list of possible attribute values:"
            else:
                attr_schema += " Example list of some of attribute values:"
            attr_schema += f"{", ".join(attr.examples)}."
            attributes_prompt_schema.append(attr_schema)

        user_prompt = f"""
Below there is a text in Russian between tag BEGIN:MESSAGE and END:MESSAGE.
Also below there is topic of that text between tag BEGIN:TOPIC and END:TOPIC.
You have to try to extract from that text as much as possible attributes by the following schema:

{"\n\n".join(attributes_prompt_schema)}

Use the following JSON format to output found attributes:

{prompt_classification_response_json}

Attribute must have first value if there are many suitable values. Set null for attributes with no value.

BEGIN:TOPIC
{topic}
END:TOPIC

BEGIN:MESSAGE
{text}
END:MESSAGE
"""

        result = llm_chat_request(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            model=os.environ["LLM_MODEL_BASE"],
            output_class=LlmClassificationResponse,
        )

        result = normalize_classification_result(result)

        validation_result = validate_classification_result(result)
        answer: Optional[str] = None
        if not validation_result.valid and body.generate_answer:
            answer = self.generate_answer(
                name=customer_name, validation_result=validation_result
            )

        return ClassifiedMessageDto(
            valid=validation_result.valid,
            missing_attributes=validation_result.missing_attributes,
            attributes=[
                ClassifierAttributeDto(name=name, value=normalize_attr_value(value))
                for (name, value) in validation_result.valid_attributes.items()
                if name not in validation_result.missing_attributes
            ],
            keywords=[val for val in result.attributes.values() if val],
            answer=answer,
        )


def normalize_user_str(raw_value: Optional[str], max_len: int, title: str):
    if raw_value == None:
        return ""
    raw_value = re.sub(SPACES_REGEX, " ", raw_value)
    raw_value = re.sub(DASHES_REGEX, "-", raw_value)

    if len(raw_value) > max_len:
        logger.warning(f"{title=} is longer then {max_len=}")
        raw_value = raw_value[:max_len]

    return raw_value.strip()


def translit(s: str):
    return (
        s.replace("С", "C")
        .replace("Е", "E")
        .replace("В", "B")
        .replace("А", "A")
        .replace("Н", "H")
        .replace("К", "K")
        .replace("М", "M")
        .replace("О", "O")
        .replace("Р", "P")
        .replace("Т", "T")
        .replace("Х", "X")
    )


def normalize_attr_value(raw_attr_value: Optional[str]):
    return raw_attr_value.strip() if raw_attr_value else ""


def get_classifier_service(state: Any) -> ClassifierService:
    return getattr(state, CLASSIFIER_SERVICE_NAME)
