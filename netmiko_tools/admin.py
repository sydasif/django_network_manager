from django.contrib import admin

from .models import CommandHistory


@admin.register(CommandHistory)
class CommandHistoryAdmin(admin.ModelAdmin):
    """
    Admin class for CommandHistory model.
    """

    list_display = ("device", "command", "status", "executed_at")
    list_filter = ("status", "device", "executed_at")
    search_fields = ("command", "output", "device__name")
    ordering = ("-executed_at",)
