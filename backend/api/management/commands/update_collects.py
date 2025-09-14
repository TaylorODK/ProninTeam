from django.core.management.base import BaseCommand
from django.db.models import Sum
from api.models import Collect


class Command(BaseCommand):
    """Обновление поля is_active для всех сборов после заполнения БД."""

    help = "Обновляет is_active для всех Collect"

    def handle(self, *args, **options):
        collects = Collect.objects.all()
        for collect in collects:
            total_payments = (
                collect.payments.aggregate(total=Sum("amount"))["total"] or 0
            )
            collect.is_active = total_payments < collect.total_amount
            collect.save(update_fields=["is_active"])
        self.stdout.write(
            self.style.SUCCESS("All collects updated successfully.")
        )
