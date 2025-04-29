from django import forms

from .models import NetworkDevice


class CommandForm(forms.Form):
    device = forms.ModelChoiceField(
        queryset=NetworkDevice.objects.all(),
        label="Device",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    command = forms.CharField(
        label="Command",
        max_length=200,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
