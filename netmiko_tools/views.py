from concurrent.futures import ThreadPoolExecutor, as_completed

import netmiko
from django.contrib import messages
from django.shortcuts import get_object_or_404, render

from .forms import CommandForm
from .models import CommandHistory, NetworkDevice


def execute_command_on_device(device, command, executed_by):
    try:
        with netmiko.ConnectHandler(
            device_type=device.device_type,
            ip=device.ip_address,
            username=device.username,
            password=device.password,
            port=device.port,
            secret=device.enable_password,
        ) as net_connect:
            output = net_connect.send_command(command)
            status = "success"
            return device, output, status
    except Exception as e:
        return device, str(e), "failed"


def execute_config_commands_on_device(device, config_commands, executed_by):
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
    form = CommandForm()
    results = []

    if request.method == "POST":
        form = CommandForm(request.POST)
        if form.is_valid():
            command = form.cleaned_data.get("command")  # Use .get() as it might be None
            config_commands_raw = form.cleaned_data.get("config_commands")  # Use .get()
            execution_type = form.cleaned_data["execution_type"]
            devices = form.cleaned_data[
                "multiple_devices"
            ]  # Always use multiple devices now

            if execution_type == "show_cmd":
                if devices and command:  # Check if command is provided
                    with ThreadPoolExecutor(max_workers=10) as executor:
                        future_to_device = {
                            executor.submit(
                                execute_command_on_device,
                                device,
                                command,
                                request.user.username,
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
                                executed_by=request.user.username,
                            )
                elif not command:
                    messages.error(
                        request, "Please enter a command for Show Commands mode."
                    )
                elif not devices:
                    messages.error(request, "Please select at least one device.")

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
                                request.user.username,
                            ): device
                            for device in devices
                        }

                        for future in as_completed(future_to_device):
                            device, output, status = future.result()
                            results.append(
                                {"device": device, "status": status, "output": output}
                            )
                            # Save history inside the loop for config_cmd
                            # Store the raw commands string for history
                            CommandHistory.objects.create(
                                device=device,
                                command=config_commands_raw,  # Save the multi-line string
                                output=output,
                                status=status,
                                executed_by=request.user.username,
                            )
                elif not config_commands_raw:
                    messages.error(request, "Please enter configuration commands.")
                elif not devices:
                    messages.error(request, "Please select at least one device.")

            # Display messages based on results (moved outside history saving)
            for result in results:
                if result["status"] == "success":
                    messages.success(
                        request,
                        f"Operation successful on {result['device'].name}",
                    )
                else:
                    messages.error(
                        request,
                        f"Operation failed on {result['device'].name}: {result['output']}",
                    )

    return render(
        request,
        "netmiko_tools/index.html",
        {"form": form, "results": results},
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
