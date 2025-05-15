from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.exceptions import ValidationError

DEVICE_TYPES = [
    ("arista_eos", "arista_eos"),
    ("cisco_ios", "cisco_ios"),
    ("cisco_nxos", "cisco_nxos"),
    ("generic", "generic"),
    ("juniper", "juniper"),
    ("juniper_junos", "juniper_junos"),
    ("mikrotik_routeros", "mikrotik_routeros"),
    ("mikrotik_switchos", "mikrotik_switchos"),
    ("vyatta_vyos", "vyatta_vyos"),
    ("vyos", "vyos"),
]

USER_ROLES = [
    ('admin', 'Administrator'),
    ('operator', 'Operator'),
    ('viewer', 'Viewer'),
]

class User(AbstractUser):
    """Custom user model with role-based access control"""
    role = models.CharField(max_length=20, choices=USER_ROLES, default='viewer')
    devices = models.ManyToManyField('NetworkDevice', through='DevicePermission', related_name='authorized_users')
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='core_user_set',
        related_query_name='core_user'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='core_user_set',
        related_query_name='core_user'
    )

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self._assign_default_permissions()

    def _assign_default_permissions(self):
        if self.role == 'admin':
            admin_group = Group.objects.get_or_create(name='Administrators')[0]
            self.groups.add(admin_group)
        elif self.role == 'operator':
            operator_group = Group.objects.get_or_create(name='Operators')[0]
            self.groups.add(operator_group)
        elif self.role == 'viewer':
            viewer_group = Group.objects.get_or_create(name='Viewers')[0]
            self.groups.add(viewer_group)

class DevicePermission(models.Model):
    """Model for managing user permissions on devices"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device = models.ForeignKey('NetworkDevice', on_delete=models.CASCADE)
    can_view = models.BooleanField(default=True)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'device']
        verbose_name = "Device Permission"
        verbose_name_plural = "Device Permissions"

class AuditLog(models.Model):
    """Model for tracking all user actions"""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50)
    device = models.ForeignKey('NetworkDevice', on_delete=models.SET_NULL, null=True)
    details = models.JSONField()
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"

class NetworkDevice(models.Model):
    """Central model for network device management"""
    name = models.CharField(max_length=100, unique=True)
    ip_address = models.GenericIPAddressField(unique=True)
    device_type = models.CharField(
        max_length=100, choices=DEVICE_TYPES, default="cisco_ios"
    )
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    enable_password = models.CharField(max_length=100, blank=True, null=True)
    port = models.IntegerField(default=22)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.ip_address})"

    class Meta:
        ordering = ["name"]
        verbose_name = "Network Device"
        verbose_name_plural = "Network Devices"


class DeviceGroup(models.Model):
    """Model for organizing devices into groups"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    devices = models.ManyToManyField(NetworkDevice, related_name='groups')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "Device Group"
        verbose_name_plural = "Device Groups"


class CommandTemplate(models.Model):
    """Model for reusable command templates"""
    COMMAND_TYPES = [
        ("show", "Show Command"),
        ("config", "Configuration Command"),
        ("validate", "Validation Command"),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    command_type = models.CharField(max_length=20, choices=COMMAND_TYPES)
    template = models.TextField(help_text="Use {{ variable }} syntax for variables")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_command_type_display()})"

    class Meta:
        ordering = ["name"]
        verbose_name = "Command Template"
        verbose_name_plural = "Command Templates"
