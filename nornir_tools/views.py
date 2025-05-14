from django.contrib import messages
from django.shortcuts import render

from .forms import NornirCommandForm
from .utils import backup_config, run_commands, run_config_commands


def nornir_home(request):
    form = NornirCommandForm()
    results = None

    if request.method == "POST":
        form = NornirCommandForm(request.POST)
        if form.is_valid():
            devices = [device.name for device in form.cleaned_data["devices"]]
            command_type = form.cleaned_data["command_type"]
            commands = [
                cmd.strip()
                for cmd in form.cleaned_data["command"].split("\n")
                if cmd.strip()
            ]
            parallel = form.cleaned_data["parallel_execution"]

            try:
                if command_type == "show":
                    results = run_commands(devices, commands, parallel)
                elif command_type == "config":
                    results = run_config_commands(devices, commands, parallel)
                elif command_type == "backup":
                    results = backup_config(devices)
                elif command_type == "validate":
                    # Add validation logic here
                    pass

                if results:
                    messages.success(request, "Commands executed successfully")
                else:
                    messages.warning(request, "No results returned")

            except Exception as e:
                messages.error(request, f"Error executing commands: {str(e)}")

    return render(
        request, "nornir_tools/index.html", {"form": form, "results": results}
    )
