from django.shortcuts import render


def home(request):
    return render(request, "netmiko_tools/index.html")
