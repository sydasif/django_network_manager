from django.urls import path

from . import views

app_name = "nornir_tools"

urlpatterns = [
    path("", views.nornir_home, name="nornir_home"),
    path("devices/", views.devices, name="devices"),  # Add devices list view
    path(
        "device_history/<int:device_id>/",
        views.nornir_device_history,
        name="nornir_device_history",
    ),
]
