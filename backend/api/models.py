from django.db import models
from django.contrib.auth import get_user_model
from proninteam.constants import (
    NAME_MAX_LENGTH,
    MAX_DIGITS,
    DECIMAL_PLACES,
    FORMAT,
)


User = get_user_model()
# Create your models here.


class Collect(models.Model):
    """Модель сбора для пользователей."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
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
    reason = models.ForeignKey(
        "Event",
        on_delete=models.CASCADE,
    )
    description = models.TextField(
        verbose_name="Описание сбора",
    )
    min_payment = models.DecimalField(
        default=models.SET_NULL,
        verbose_name="Минимальная сумма платежа",
        max_digits=MAX_DIGITS,
        decimal_places=DECIMAL_PLACES,
    )
    target_amount = models.DecimalField(
        default=models.SET_NULL,
        verbose_name="Целевая сумма сбора",
        max_digits=MAX_DIGITS,
        decimal_places=DECIMAL_PLACES,
    )
    total_amount = models.DecimalField(
        default=models.SET_NULL,
        verbose_name="Общая цель сбора сбора",
        max_digits=MAX_DIGITS,
        decimal_places=DECIMAL_PLACES,
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

    def __str__(self):
        return f"{self.author}: {self.name}"

    class Meta:
        default_related_name = "collects"
        verbose_name = "Сбор"
        verbose_name_plural = "Сборы"


class Payment(models.Model):
    """Модель для оплаты пользователем"""

    user = models.ForeignKey(
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
        verbose_name = "Сбор"
        verbose_name_plural = "Сборы"


class Event(models.Model):
    """Модель события для создания сбора."""

    event_format = models.CharField(
        choices=FORMAT, verbose_name="Формат встречи"
    )
    event_date_field = models.DateField(
        verbose_name="Дата встречи",
    )
    event_place = models.TextField(
        verbose_name="Место проведения встречи",
    )

    class Meta:
        verbose_name = "Событие"
        verbose_name_plural = "События"


class Like(models.Model):
    """Модель лайка платежа."""

    user = models.ForeignKey(
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
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    comment = models.TextField(verbose_name="Текст комментария")

    class Meta:
        default_related_name = "comments"
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
