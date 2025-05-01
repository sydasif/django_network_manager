from django import forms
from django.forms import RadioSelect, Textarea

from .models import NetworkDevice


class NetmikoCommandForm(forms.Form):
    execution_type = forms.ChoiceField(
        label="Execution Type",
        choices=[
            ("show_cmd", "Show Commands"),
            ("config_cmd", "Configuration Commands"),
        ],
        widget=RadioSelect,
        initial="show_cmd",
    )
    multiple_devices = forms.ModelMultipleChoiceField(
        queryset=NetworkDevice.objects.all(),
        label="Devices",
        required=False,
    )
    config_commands = forms.CharField(
        label="Config Commands",
        widget=Textarea(attrs={"rows": 5, "cols": 40}),
        required=False,
    )
    command = forms.CharField(label="Command", max_length=200)
    preset_command = forms.ChoiceField(
        label="Preset Command",
        choices=[
            ("", "--- Select a command ---"),
            ("show ip interface brief", "show ip interface brief"),
            ("show running-config", "show running-config"),
            ("show version", "show version"),
            ("show inventory", "show inventory"),
            ("show cdp neighbors detail", "show cdp neighbors detail"),
        ],
        required=False,
    )
