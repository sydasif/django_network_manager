from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("devices/", views.devices, name="devices"),
    path(
        "device/<int:device_id>/history/",
        views.device_history,
        name="device_history",
    ),
]
