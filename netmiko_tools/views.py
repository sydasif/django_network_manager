import io
from concurrent.futures import ThreadPoolExecutor, as_completed
from pprint import pprint

import netmiko
from django.contrib import messages
from django.shortcuts import get_object_or_404, render
from netmiko.exceptions import NetmikoAuthenticationException, NetmikoTimeoutException

from .forms import NetmikoCommandForm  # Corrected import
from .models import CommandHistory, NetworkDevice


def process_command_form(request):
    """
    Processes the Netmiko command form and returns the cleaned data.
    """
    form = NetmikoCommandForm(request.POST)
    if form.is_valid():
        return form.cleaned_data, None  # Return cleaned data, no error
    else:
        return None, form  # Return None for cleaned data, and the form with errors


def get_unique_devices(selected_devices, selected_groups):
    """
    Combines devices from selected groups and individual devices, and removes duplicates.
    """
    devices = []
    if selected_groups:
        for group in selected_groups:
            devices.extend(group.devices.all())
    if selected_devices:
        devices.extend(selected_devices)

    # Remove duplicates
    return list(set(devices))


def prepare_execution_details(cleaned_data):
    """
    Prepares the command or config commands to be executed based on the form data.
    """
    command = cleaned_data.get("command", "")
    preset_command = cleaned_data.get("preset_command", "")
    config_commands_raw = cleaned_data.get("config_commands", "")
    execution_type = cleaned_data["execution_type"]
    use_textfsm = cleaned_data.get("use_textfsm", True)

    if execution_type == "show_cmd":
        command_to_execute = command or preset_command
        return command_to_execute, execution_type, use_textfsm, config_commands_raw
    elif execution_type == "config_cmd":
        return config_commands_raw, execution_type, use_textfsm, command
    else:
        return None, None, None, None


def execute_command_on_device(device, command, use_textfsm=True):
    """
    Executes a single command on a network device using Netmiko.
    """
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
    except NetmikoTimeoutException:
        return device, "Timeout occurred. Check device connectivity.", "failed"
    except NetmikoAuthenticationException:
        return device, "Authentication failure. Check username and password.", "failed"
    except Exception as e:
        # Log the exception if logging is configured
        # logger.error(f"Error executing command on {device.name}: {e}")
        return device, str(e), "failed"


def execute_config_commands_on_device(device, config_commands):
    """
    Executes configuration commands on a network device using Netmiko.
    """
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
        # Log the exception if logging is configured
        # logger.error(f"Error executing config commands on {device.name}: {e}")
        return device, str(e), "failed"
    except NetmikoTimeoutException:
        return device, "Timeout occurred. Check device connectivity.", "failed"
    except NetmikoAuthenticationException:
        return device, "Authentication failure. Check username and password.", "failed"
    except Exception as e:
        # Log the exception if logging is configured
        # logger.error(f"Error executing config commands on {device.name}: {e}")
        return device, str(e), "failed"


def home(request):
    """
    Handles the main view for executing commands on network devices.
    """
    """
    Handles the main view for executing commands on network devices.
    """
    results = []
    form = NetmikoCommandForm()  # Initialize form for GET requests

    if request.method == "POST":
        form = NetmikoCommandForm(request.POST)  # Bind form with POST data
        if form.is_valid():
            try:
                cleaned_data = form.cleaned_data

                # Get selected devices and device groups
                selected_devices = cleaned_data.get("multiple_devices", [])
                selected_groups = cleaned_data.get("device_groups", [])

                devices = get_unique_devices(selected_devices, selected_groups)

                if not devices:
                    messages.error(
                        request, "Please select at least one device or device group."
                    )
                else:
                    (
                        command_to_execute,
                        execution_type,
                        use_textfsm,
                        config_commands_raw,
                    ) = prepare_execution_details(cleaned_data)

                    if execution_type == "show_cmd":
                        if not command_to_execute:
                            messages.error(
                                request,
                                "Please enter a command or select a preset command for Show Commands mode.",
                            )
                        else:
                            with ThreadPoolExecutor(max_workers=10) as executor:
                                future_to_device = {
                                    executor.submit(
                                        execute_command_on_device,
                                        device,
                                        command_to_execute,
                                        use_textfsm,
                                    ): device
                                    for device in devices
                                }

                                for future in as_completed(future_to_device):
                                    device, output, status = future.result()
                                    results.append(
                                        {
                                            "device": device,
                                            "status": status,
                                            "output": output,
                                        }
                                    )
                                    # Save history inside the loop for show_cmd
                                    CommandHistory.objects.create(
                                        device=device,
                                        command=command_to_execute,
                                        output=output,
                                        status=status,
                                    )

                    elif execution_type == "config_cmd":
                        if config_commands_raw:  # Check if config commands are provided
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
                                        {
                                            "device": device,
                                            "status": status,
                                            "output": output,
                                        }
                                    )
                                    # Save history inside the loop for config_cmd
                                    CommandHistory.objects.create(
                                        device=device,
                                        command=config_commands_raw,  # Save the multi-line string
                                        output=output,
                                        status=status,
                                    )
                        else:
                            messages.error(
                                request, "Please enter configuration commands."
                            )

                    # Display messages based on results
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
            except Exception as e:
                messages.error(request, f"An unexpected error occurred: {e}")
                # Log the exception if logging is configured
                # logger.error(f"An unexpected error occurred: {e}")
                # Ensure results is empty and form is the bound form with errors
                results = []
        # If form is not valid, the form variable already holds the form with errors

    # For GET requests, form is already initialized at the beginning

    return render(
        request, "netmiko_tools/index.html", {"form": form, "results": results}
    )


def devices(request):
    """
    Displays a list of network devices.
    """
    devices = NetworkDevice.objects.all()
    return render(
        request,
        "netmiko_tools/devices.html",
        {"devices": devices},
    )


def device_history(request, device_id):
    """
    Displays the command history for a specific network device.
    """
    device = get_object_or_404(NetworkDevice, pk=device_id)
    command_history = CommandHistory.objects.filter(device=device).order_by(
        "-executed_at"
    )
    return render(
        request,
        "netmiko_tools/device_history.html",
        {"device": device, "command_history": command_history},
    )
