from django.contrib import admin

from .models import CommandHistory, NetworkDevice


@admin.register(NetworkDevice)
class NetworkDeviceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "ip_address",
        "device_type",
        "port",
        "is_active",
        "created_at",
    )
    list_filter = ("device_type", "is_active")
    search_fields = ("name", "ip_address", "description")
    ordering = ("name",)


@admin.register(CommandHistory)
class CommandHistoryAdmin(admin.ModelAdmin):
    list_display = ("device", "command", "status", "executed_at", "executed_by")
    list_filter = ("status", "device", "executed_at")
    search_fields = ("command", "output", "device__name")
    ordering = ("-executed_at",)
