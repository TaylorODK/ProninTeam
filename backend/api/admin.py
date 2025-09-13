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
