from django.urls import path

from . import views

app_name = "nornir_tools"

urlpatterns = [
    path("", views.nornir_home, name="nornir_home"),
]
