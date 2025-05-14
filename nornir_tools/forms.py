from django import forms

from netmiko_tools.models import NetworkDevice


class NornirCommandForm(forms.Form):
    devices = forms.ModelMultipleChoiceField(
        queryset=NetworkDevice.objects.filter(is_active=True),
        label="Select Devices",
        widget=forms.SelectMultiple(attrs={"class": "form-select"}),
    )

    command_type = forms.ChoiceField(
        choices=[
            ("show", "Show Commands"),
            ("config", "Configuration Commands"),
            ("backup", "Backup Configuration"),
            ("validate", "Validate Configuration"),
        ],
        widget=forms.RadioSelect,
        initial="show",
    )

    command = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "rows": 5,
                "class": "form-control",
                "placeholder": "Enter commands (one per line)",
            }
        ),
        required=False,
    )

    parallel_execution = forms.BooleanField(
        required=False,
        initial=True,
        help_text="Execute commands on multiple devices in parallel",
    )
