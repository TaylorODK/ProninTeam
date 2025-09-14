from django.contrib import admin
from api.models import Collect, Payment, Like, Comment

# Register your models here.


@admin.register(Collect)
class CollectAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "author",
        "is_active",
        "stop_date",
    )
    search_fields = ("name", "author")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "author",
        "collect",
        "amount",
        "hide_amount",
    )
    search_fields = ("collect", "author")


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = (
        "author",
        "payment",
    )
    search_fields = ("payment", "author")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "author",
        "payment",
    )
    search_fields = ("payment", "author")
