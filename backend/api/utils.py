from typing import TypeVar
from typing import Generic, Optional, Union
from collections import OrderedDict
from django.db import models
from rest_framework.validators import ValidationError, UniqueTogetherValidator
from django.conf import settings


ModelType = TypeVar('ModelType', bound=models.Model)


def create_list_obj(cls: Generic[ModelType], items: list[OrderedDict | dict],
                    **kwargs) -> list[Generic[ModelType]]:
    try:
        return [cls(**item, **kwargs) for item in items]
    except Exception as exc:
        raise ValueError(exc)


def empty_validator(value):
    if not value:
        raise ValidationError('Обязательное поле.')
    return value


class DynamicUniqueTogetherValidator(UniqueTogetherValidator):
    """Проверяет на уникальность поля одной модели."""
    def __init__(self, model: Generic[ModelType], fields=None, message=None):
        try:
            _data = settings.UNIQUE_TOGETHER_VALIDATOR_DATA[model.__name__]
            queryset = model.objects.all()
            fields = fields or _data.get('fields')
            message = message or _data.get('message')
            del _data
        except Exception as exc:
            raise ValueError(exc)
        super().__init__(queryset, fields, message)
