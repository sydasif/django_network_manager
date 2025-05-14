import io
from concurrent.futures import ThreadPoolExecutor, as_completed
from pprint import pprint

import netmiko
from django.contrib import messages
from django.shortcuts import get_object_or_404, render

from .forms import NetmikoCommandForm  # Corrected import
from .models import CommandHistory, NetworkDevice


def execute_command_on_device(device, command, use_textfsm=True):
    try:
        with netmiko.ConnectHandler(
            device_type=device.device_type,
            ip=device.ip_address,
            username=device.username,
            password=device.password,
            port=device.port,
            secret=device.enable_password,
        ) as net_connect:
            output = net_connect.send_command(command, use_textfsm=use_textfsm)
            if use_textfsm:
                with io.StringIO() as buf:
                    pprint(output, buf)
                    output = buf.getvalue()
            status = "success"
            return device, output, status
    except Exception as e:
        return device, str(e), "failed"


def execute_config_commands_on_device(device, config_commands):
    try:
        with netmiko.ConnectHandler(
            device_type=device.device_type,
            ip=device.ip_address,
            username=device.username,
            password=device.password,
            port=device.port,
            secret=device.enable_password,
        ) as net_connect:
            net_connect.enable()
            output = net_connect.send_config_set(config_commands)
            output += net_connect.save_config()
            status = "success"
            return device, output, status
    except Exception as e:
        return device, str(e), "failed"


def home(request):
    results = []

    if request.method == "POST":
        form = NetmikoCommandForm(request.POST)
        if form.is_valid():
            # Get form data
            command = form.cleaned_data.get("command", "")
            preset_command = form.cleaned_data.get("preset_command", "")
            config_commands_raw = form.cleaned_data.get("config_commands", "")
            execution_type = form.cleaned_data["execution_type"]
            use_textfsm = form.cleaned_data.get("use_textfsm", True)

            # Filter devices based on selected device groups
            devices = form.cleaned_data.get("multiple_devices", [])

            if execution_type == "show_cmd":
                if not command:
                    messages.error(
                        request, "Please enter a command for Show Commands mode."
                    )
                elif not devices:
                    messages.error(request, "Please select at least one device.")
                else:
                    with ThreadPoolExecutor(max_workers=10) as executor:
                        future_to_device = {
                            executor.submit(
                                execute_command_on_device,
                                device,
                                command,
                                use_textfsm,
                            ): device
                            for device in devices
                        }

                        for future in as_completed(future_to_device):
                            device, output, status = future.result()
                            results.append(
                                {"device": device, "status": status, "output": output}
                            )
                            # Save history inside the loop for show_cmd
                            CommandHistory.objects.create(
                                device=device,
                                command=command,
                                output=output,
                                status=status,
                            )

            elif execution_type == "config_cmd":
                if (
                    devices and config_commands_raw
                ):  # Check if config commands are provided
                    config_commands = config_commands_raw.splitlines()
                    with ThreadPoolExecutor(max_workers=10) as executor:
                        future_to_device = {
                            executor.submit(
                                execute_config_commands_on_device,
                                device,
                                config_commands,
                            ): device
                            for device in devices
                        }

                        for future in as_completed(future_to_device):
                            device, output, status = future.result()
                            results.append(
                                {"device": device, "status": status, "output": output}
                            )
                            # Save history inside the loop for config_cmd
                            CommandHistory.objects.create(
                                device=device,
                                command=config_commands_raw,  # Save the multi-line string
                                output=output,
                                status=status,
                            )
                elif not config_commands_raw:
                    messages.error(request, "Please enter configuration commands.")
                elif not devices:
                    messages.error(request, "Please select at least one device.")

            # Display messages based on results
            for result in results:
                if result["status"] == "success":
                    messages.success(
                        request, f"Operation successful on {result['device'].name}"
                    )
                else:
                    messages.error(
                        request,
                        f"Operation failed on {result['device'].name}: {result['output']}",
                    )
    else:
        form = NetmikoCommandForm()

    return render(
        request, "netmiko_tools/index.html", {"form": form, "results": results}
    )


def devices(request):
    devices = NetworkDevice.objects.all()
    return render(
        request,
        "netmiko_tools/devices.html",
        {"devices": devices},
    )


def device_history(request, device_id):
    device = get_object_or_404(NetworkDevice, pk=device_id)
    command_history = CommandHistory.objects.filter(device=device).order_by(
        "-executed_at"
    )
    return render(
        request,
        "netmiko_tools/device_history.html",
        {"device": device, "command_history": command_history},
    )
