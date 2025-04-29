from django.shortcuts import render

from .models import NetworkDevice


def home(request):
    devices = NetworkDevice.objects.all()
    return render(request, "netmiko_tools/index.html", {"devices": devices})
