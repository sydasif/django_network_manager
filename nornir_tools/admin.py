from django.contrib import admin
from .models import NornirCommandHistory


@admin.register(NornirCommandHistory)
class NornirCommandHistoryAdmin(admin.ModelAdmin):
    list_display = ("device", "command", "status", "executed_at")
    list_filter = ("status", "device", "executed_at")
    search_fields = ("command", "output", "device__name")
    ordering = ("-executed_at",)
