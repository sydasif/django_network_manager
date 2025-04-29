import netmiko
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommandForm
from .models import CommandHistory, NetworkDevice


def home(request):
    devices = NetworkDevice.objects.all()
    form = CommandForm()
    command_history = CommandHistory.objects.all().order_by("-executed_at")[:5]

    if request.method == "POST":
        form = CommandForm(request.POST)
        if form.is_valid():
            command = form.cleaned_data["command"]
            device_id = request.POST.get("device_id")
            try:
                device = NetworkDevice.objects.get(pk=device_id)
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
                    messages.success(
                        request,
                        f"Command '{command}' executed successfully on {device.name}",
                    )

                CommandHistory.objects.create(
                    device=device,
                    command=command,
                    output=output,
                    status=status,
                    executed_by="admin",  # Replace with actual user if auth is implemented
                )
            except NetworkDevice.DoesNotExist:
                messages.error(request, "Device not found.")
            except Exception as e:
                messages.error(request, f"Error executing command: {e}")
                output = str(e)
                status = "failed"

            return redirect("home")

    return render(
        request,
        "netmiko_tools/index.html",
        {"devices": devices, "form": form},
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
