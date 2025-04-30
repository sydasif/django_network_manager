from django import forms

from .models import NetworkDevice


class CommandForm(forms.Form):
    EXECUTION_TYPE = (
        ("show_cmd", "Show Commands"),
        ("config_cmd", "Configuration Commands"),
    )

    execution_type = forms.ChoiceField(
        choices=EXECUTION_TYPE,
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        initial="show_cmd",  # Updated initial value
    )

    # Removed single_device field

    multiple_devices = forms.ModelMultipleChoiceField(
        queryset=NetworkDevice.objects.filter(is_active=True),
        label="Select Devices",
        required=False,  # Requirement handled by JS based on mode
        widget=forms.SelectMultiple(attrs={"class": "form-control"}),
    )

    command = forms.CharField(
        label="Command",
        max_length=200,
        required=False,  # Requirement handled by JS based on mode
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    config_commands = forms.CharField(
        label="Configuration Commands",
        required=False,  # Requirement handled by JS based on mode
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 5}),
    )
