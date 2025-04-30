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


def home(request):
    form = CommandForm()
    results = []

    if request.method == "POST":
        form = CommandForm(request.POST)
        if form.is_valid():
            command = form.cleaned_data["command"]
            execution_type = form.cleaned_data["execution_type"]

            if execution_type == "single":
                device = form.cleaned_data["single_device"]
                if device:
                    device, output, status = execute_command_on_device(
                        device, command, request.user.username
                    )
                    results.append(
                        {"device": device, "status": status, "output": output}
                    )
            else:
                devices = form.cleaned_data["multiple_devices"]
                if devices:
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

            # Save command history for all results
            for result in results:
                CommandHistory.objects.create(
                    device=result["device"],
                    command=command,
                    output=result["output"],
                    status=result["status"],
                    executed_by=request.user.username,
                )

                if result["status"] == "success":
                    messages.success(
                        request,
                        f"Command executed successfully on {result['device'].name}",
                    )
                else:
                    messages.error(
                        request,
                        f"Command failed on {result['device'].name}: {result['output']}",
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
