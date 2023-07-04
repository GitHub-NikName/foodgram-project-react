from django.core.validators import MinValueValidator
from django.conf import settings


validate_cooking_time_min = MinValueValidator(
    settings.COOKING_TIME_MIN,
    f'Убедитесь, что это значение больше '
    f'либо равно {settings.COOKING_TIME_MIN} минут'
    )

validate_ingredient_amount_min = MinValueValidator(
    settings.INGREDIENT_AMOUNT_MIN,
    f'Убедитесь, что это значение больше '
    f'либо равно {settings.INGREDIENT_AMOUNT_MIN}'
    )
