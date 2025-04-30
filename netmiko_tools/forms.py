from django import forms

from .models import NetworkDevice


class CommandForm(forms.Form):
    EXECUTION_TYPE = (("single", "Single Device"), ("bulk", "Multiple Devices"))

    execution_type = forms.ChoiceField(
        choices=EXECUTION_TYPE,
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        initial="single",
    )

    single_device = forms.ModelChoiceField(
        queryset=NetworkDevice.objects.filter(is_active=True),
        label="Device",
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    multiple_devices = forms.ModelMultipleChoiceField(
        queryset=NetworkDevice.objects.filter(is_active=True),
        label="Select Devices",
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-control"}),
    )

    command = forms.CharField(
        label="Command",
        max_length=200,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
