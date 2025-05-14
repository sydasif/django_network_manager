from django.db import models
from django.utils import timezone

from core.models import NetworkDevice  # Import NetworkDevice from core app


class NornirCommandHistory(models.Model):
    device = models.ForeignKey(
        NetworkDevice, on_delete=models.CASCADE, related_name="nornir_command_history"
    )
    command = models.TextField()
    output = models.TextField(blank=True)
    status = models.CharField(max_length=20, default="success")
    executed_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.device.name} - {self.command[:50]}"

    class Meta:
        ordering = ["-executed_at"]
        verbose_name_plural = "Nornir command histories"
