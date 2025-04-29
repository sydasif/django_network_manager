from django.db import models
from django.utils import timezone


class NetworkDevice(models.Model):

    name = models.CharField(max_length=100, unique=True)
    ip_address = models.GenericIPAddressField(unique=True)
    device_type = models.CharField(max_length=20)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    enable_password = models.CharField(max_length=100, blank=True, null=True)
    port = models.IntegerField(default=22)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.ip_address})"

    class Meta:
        ordering = ["name"]


class CommandHistory(models.Model):
    device = models.ForeignKey(
        NetworkDevice, on_delete=models.CASCADE, related_name="command_history"
    )
    command = models.TextField()
    output = models.TextField(blank=True)
    status = models.CharField(max_length=20, default="success")
    executed_at = models.DateTimeField(default=timezone.now)
    executed_by = models.CharField(
        max_length=100
    )  # Can be linked to User model later if needed

    def __str__(self):
        return f"{self.device.name} - {self.command[:50]}"

    class Meta:
        ordering = ["-executed_at"]
        verbose_name_plural = "Command histories"
