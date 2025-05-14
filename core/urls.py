from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"devices", views.NetworkDeviceViewSet)
router.register(r"groups", views.DeviceGroupViewSet)
router.register(r"templates", views.CommandTemplateViewSet)

app_name = "core"

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("api/", include(router.urls)),
    path(
        "api-auth/", include("rest_framework.urls")
    ),  # DRF browsable API authentication
]
