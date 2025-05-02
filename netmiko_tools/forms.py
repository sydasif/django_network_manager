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
    command = forms.CharField(
        label="Command", max_length=200, required=False
    )  # Make command not required
    preset_command = forms.ChoiceField(
        label="Preset Command",
        choices=[
            ("", "--- Select a command ---"),
            ("show arp", "show arp"),
            ("show cdp neighbors detail", "show cdp neighbors detail"),
            ("show interfaces", "show interfaces"),
            ("show interfaces switchport", "show interfaces switchport"),
            ("show interfaces trunk", "show interfaces trunk"),
            ("show inventory", "show inventory"),
            ("show ip interface", "show ip interface"),
            ("show ip interface brief", "show ip interface brief"),
            ("show ip route", "show ip route"),
            ("show mac-address table", "show mac-address table"),
            ("show running-config", "show running-config"),
            ("show spanning-tree", "show spanning-tree"),
            ("show startup-config", "show startup-config"),
            ("show users", "show users"),
            ("show version", "show version"),
            ("show vlan", "show vlan"),
        ],
        required=False,
    )
    use_textfsm = forms.BooleanField(label="Use TextFSM", required=False, initial=True)
