from django.urls import path

from . import views

app_name = "netmiko_tools"

urlpatterns = [
    path("", views.home, name="home"),
    path("devices/", views.devices, name="devices"),
    path(
        "devices/<int:device_id>/history/", views.device_history, name="device_history"
    ),
]
