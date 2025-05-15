from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, NetworkDevice, DeviceGroup, CommandTemplate, DevicePermission, AuditLog

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'date_joined', 'last_login')
    list_filter = ('role', 'is_active', 'groups')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined', 'last_login_ip')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)


@admin.register(NetworkDevice)
class NetworkDeviceAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "ip_address",
        "device_type",
        "is_active",
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

@admin.register(DevicePermission)
class DevicePermissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'device', 'can_view', 'can_edit', 'can_delete']
    list_filter = ['can_view', 'can_edit', 'can_delete']
    search_fields = ['user__username', 'device__name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'user', 'action', 'device', 'ip_address']
    list_filter = ['action', 'timestamp']
    search_fields = ['user__username', 'device__name', 'action', 'ip_address']
    readonly_fields = ['timestamp', 'user', 'action', 'device', 'details', 'ip_address']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
