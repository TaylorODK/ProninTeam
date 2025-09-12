from django.db import models
from django.contrib.auth import get_user_model

from proninteam.constants import (
    NAME_MAX_LENGTH,
    MAX_DIGITS,
    DECIMAL_PLACES,
    FORMAT,
    REASON,
)


User = get_user_model()
# Create your models here.


class Collect(models.Model):
    """
    Модель сбора для пользователей.
    Для полей target_amount и total_amount по умолчанию установлены значения 0.
    При данном значении сбор считает бесконечным и будет завершен только после
    достижения даты окончания сбора или если автор сбора
    самостоятельно деактивирует сбор.
    Возможна повторная активация сбора автором.
    """

    # --- Описание сбора
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=False, verbose_name="Автор сбора"
    )
    name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        unique=True,
        verbose_name="Наименование сбора",
    )
    slug = models.SlugField(
        max_length=NAME_MAX_LENGTH,
        unique=True,
        verbose_name="Слаг",
    )
    description = models.TextField(
        verbose_name="Описание сбора",
    )
    logo = models.ImageField(
        upload_to="collect/",
        verbose_name="Обложка сбора",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата и время создания сбора",
    )
    stop_date = models.DateTimeField(
        verbose_name="Дата и время завершения сбора",
    )
    is_active = models.BooleanField(
        editable=False,
        default=True,
        verbose_name="Активность сбора",
    )

    # --- Описание события
    event_format = models.CharField(
        choices=FORMAT, verbose_name="Формат встречи"
    )
    event_reason = models.CharField(
        choices=REASON,
        verbose_name="Вид события",
    )
    event_date = models.DateField(
        verbose_name="Дата встречи",
    )
    event_time = models.TimeField(
        verbose_name="Время встречи",
    )
    event_place = models.TextField(
        verbose_name="Место проведения встречи",
    )

    # --- Данные по объемам сбора
    min_payment = models.DecimalField(
        default=0,
        verbose_name="Минимальная сумма платежа",
        max_digits=MAX_DIGITS,
        decimal_places=DECIMAL_PLACES,
    )
    target_amount = models.DecimalField(
        default=0,
        verbose_name="Целевая сумма сбора",
        max_digits=MAX_DIGITS,
        decimal_places=DECIMAL_PLACES,
    )
    total_amount = models.DecimalField(
        default=0,
        verbose_name="Общая цель сбора сбора",
        max_digits=MAX_DIGITS,
        decimal_places=DECIMAL_PLACES,
    )

    def __str__(self):
        return f"{self.author}: {self.name}"

    class Meta:
        default_related_name = "collects"
        verbose_name = "Сбор"
        verbose_name_plural = "Сборы"


class Payment(models.Model):
    """
    Модель для оплаты пользователем
    Модель предусматривает возможность пользователей скрыть общую сумму
    платежа, по умолчанию сумма не скрывается.
    Дополнительно предусмотрена возможность пользователю
    оставить комментарий при платеже.
    """

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    collect = models.ForeignKey(
        Collect,
        on_delete=models.CASCADE,
    )
    amount = models.DecimalField(
        max_digits=MAX_DIGITS,
        decimal_places=DECIMAL_PLACES,
        verbose_name="Сумма платежа",
    )
    hide_amount = models.BooleanField(
        default=False,
        verbose_name="Скрыть сумма платежа",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата и время платежа"
    )

    def __str__(self):
        return f"{self.user.username}"

    class Meta:
        default_related_name="payments"
        verbose_name = "Сбор"
        verbose_name_plural = "Сборы"


class Like(models.Model):
    """
    Модель лайка платежа.
    Предусматривает возможность для сторонних авторизованных
    пользователей поставить лайк платежам.
    """

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
    )

    class Meta:
        default_related_name = "likes"
        verbose_name = "Лайк"
        verbose_name_plural = "Лайки"


class Comment(models.Model):
    """
    Модель комментария платежа.
    Пользователи могут прокомментировать данные об определенных платежах.
    """

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    comment = models.TextField(verbose_name="Текст комментария")
    payment = models.ForeignKey(Payment, verbose_name="Платеж", on_delete=models.CASCADE)
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата и время комментария",
    )

    class Meta:
        default_related_name = "comments"
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
