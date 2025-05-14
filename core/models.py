from django.db import models
from django.utils import timezone

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
