from typing import Any

from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from .models import Payment, Like, Comment, Collect
from .tasks import send_collect_created_email, send_payment_created_email


def clear_collect_cache(collect_id):
    cache_key = f"collect_detail_{collect_id}"
    cache.delete(cache_key)


@receiver([post_save, post_delete], sender=Payment)
def payment_changed(sender, instance, **kwargs):
    clear_collect_cache(instance.collect.id)


@receiver([post_save, post_delete], sender=Like)
def like_changed(sender, instance, **kwargs):
    clear_collect_cache(instance.payment.collect.id)


@receiver([post_save, post_delete], sender=Comment)
def comment_changed(sender, instance, **kwargs):
    clear_collect_cache(instance.payment.collect.id)


@receiver(post_save, sender=Collect)
def send_email_to_author(sender, instance, created, **kwargs):

    if created:
        send_collect_created_email.delay(collect_id=instance.id)


@receiver(post_save, sender=Payment)
def send_email_to_payment_author(sender, instance, created, **kwargs):

    if created:
        send_payment_created_email.delay(payment_id=instance.id)


@receiver(post_save, sender=Payment)
def make_inactive_collect(sender, instance, **kwargs):
    collect = instance.collect
    current_sum = collect.payments.aggregate(Sum("amount"))["amount__sum"] or 0
    if current_sum > collect.total_amount:
        collect.is_active = False
        collect.save(update_fields=["is_active"])
