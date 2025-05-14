from django.contrib import admin
from .models import NetworkDevice, DeviceGroup, CommandTemplate


from django.urls import reverse
from django.utils.html import format_html


@admin.register(NetworkDevice)
class NetworkDeviceAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "ip_address",
        "device_type",
        "is_active",
        "nornir_history_link",
    ]
    list_filter = ["device_type", "is_active"]
    search_fields = ["name", "ip_address", "description"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = [
        (
            "Device Information",
            {
                "fields": [
                    "name",
                    "ip_address",
                    "device_type",
                    "description",
                    "is_active",
                ]
            },
        ),
        (
            "Authentication",
            {"fields": ["username", "password", "enable_password", "port"]},
        ),
        ("Metadata", {"fields": ["created_at", "updated_at"]}),
    ]

    def nornir_history_link(self, obj):
        url = reverse("nornir_tools:nornir_device_history", args=[obj.id])
        return format_html('<a href="{}">Nornir History</a>', url)

    nornir_history_link.short_description = "Nornir History"


@admin.register(DeviceGroup)
class DeviceGroupAdmin(admin.ModelAdmin):
    list_display = ["name", "get_device_count", "created_at"]
    search_fields = ["name", "description"]
    filter_horizontal = ["devices"]
    readonly_fields = ["created_at", "updated_at"]

    def get_device_count(self, obj):
        return obj.devices.count()

    get_device_count.short_description = "Device Count"


@admin.register(CommandTemplate)
class CommandTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "command_type", "created_at"]
    list_filter = ["command_type"]
    search_fields = ["name", "description", "template"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = [
        ("Template Information", {"fields": ["name", "description", "command_type"]}),
        ("Template Content", {"fields": ["template"]}),
        ("Metadata", {"fields": ["created_at", "updated_at"]}),
    ]
