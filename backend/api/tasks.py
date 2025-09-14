from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMessage

from api.models import Collect, Payment


@shared_task(
    retry_kwargs={"max_retries": 5, "countdown": 60},
    retry_backoff=True,
    retry_jitter=True,
)
def send_collect_created_email(collect_id):
    """Отправить письмо автору о создании сбора"""

    request = Collect.objects.get(id=collect_id)
    subject = "Ваш сбор успешно создан!"
    message = (
        f"Здравствуйте!\n\n"
        f"Ваш сбор «{request.name}» (ID: {collect_id}) успешно создан.\n"
        f"Теперь вы можете принимать платежи.\n\n"
        f"С уважением, команда {getattr(settings, 'PROJECT_NAME')}"
    )
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[request.author.email],
    )
    email.send()


@shared_task
def send_payment_created_email(payment_id):
    """Отправить письмо автору сбора о новом платеже"""

    request = Payment.objects.get(id=payment_id)
    subject = "Ваш платеж успешно создан!"
    message = (
        f"Здравствуйте!\n\n"
        f"Ваш платеж для сбора «{request.collect.name}»"
        f"на сумму  {request.amount}. Успешно создан\n\n"
        f"С уважением, команда {getattr(settings, 'PROJECT_NAME')}"
    )
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[request.author.email],
    )
    email.send()
