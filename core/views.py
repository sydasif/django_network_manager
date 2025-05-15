from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

# Create serializers for the API
from rest_framework import permissions, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from netmiko_tools.models import CommandHistory
from nornir_tools.models import NornirCommandHistory

from .models import CommandTemplate, DeviceGroup, NetworkDevice


class NetworkDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NetworkDevice
        fields = [
            "id",
            "name",
            "ip_address",
            "device_type",
            "username",
            "port",
            "is_active",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
        extra_kwargs = {
            "password": {"write_only": True},
            "enable_password": {"write_only": True},
        }


class DeviceGroupSerializer(serializers.ModelSerializer):
    devices_count = serializers.SerializerMethodField()

    class Meta:
        model = DeviceGroup
        fields = [
            "id",
            "name",
            "description",
            "devices",
            "devices_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_devices_count(self, obj):
        return obj.devices.count()


class CommandTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommandTemplate
        fields = [
            "id",
            "name",
            "description",
            "command_type",
            "template",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


# Authentication views
@login_required
def index(request):
    devices = NetworkDevice.objects.all()
    groups = DeviceGroup.objects.all()
    templates = CommandTemplate.objects.all()

    # Get recent command history
    netmiko_history = CommandHistory.objects.all().order_by("-executed_at")[:5]
    nornir_history = NornirCommandHistory.objects.all().order_by("-executed_at")[:5]

    # Combine and sort the history
    command_history = sorted(
        list(netmiko_history) + list(nornir_history),
        key=lambda x: x.executed_at,
        reverse=True,
    )[:10]

    context = {
        "device_count": devices.count(),
        "online_count": devices.filter(is_active=True).count(),
        "group_count": groups.count(),
        "template_count": templates.count(),
        "command_history": command_history,
    }
    return render(request, "core/dashboard.html", context)


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get("next", "core:index")
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "core/login.html")


def logout_view(request):
    logout(request)
    return redirect("core:login")


# Create viewsets for the API
class NetworkDeviceViewSet(viewsets.ModelViewSet):
    queryset = NetworkDevice.objects.all()
    serializer_class = NetworkDeviceSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=["get"])
    def status(self, request, pk=None):
        device = self.get_object()
        # In a real implementation, this would check device connectivity
        return Response({"status": "online" if device.is_active else "offline"})

    @action(detail=True, methods=["get"])
    def groups(self, request, pk=None):
        device = self.get_object()
        groups = device.groups.all()
        serializer = DeviceGroupSerializer(groups, many=True)
        return Response(serializer.data)


class DeviceGroupViewSet(viewsets.ModelViewSet):
    queryset = DeviceGroup.objects.all()
    serializer_class = DeviceGroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=["get"])
    def devices(self, request, pk=None):
        group = self.get_object()
        devices = group.devices.all()
        serializer = NetworkDeviceSerializer(devices, many=True)
        return Response(serializer.data)


class CommandTemplateViewSet(viewsets.ModelViewSet):
    queryset = CommandTemplate.objects.all()
    serializer_class = CommandTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["command_type"]
    search_fields = ["name", "description"]


# Create views for the web interface


@login_required
def device_list(request):
    # Filter devices based on status parameter
    status = request.GET.get("status")
    devices = NetworkDevice.objects.all()

    if status == "active":
        devices = devices.filter(is_active=True)

    return render(
        request,
        "core/device_list.html",
        {"devices": devices, "is_active_filter": status == "active"},
    )


@login_required
def group_list(request):
    groups = DeviceGroup.objects.all()
    return render(request, "core/group_list.html", {"groups": groups})


@login_required
def template_list(request):
    templates = CommandTemplate.objects.all()
    return render(request, "core/template_list.html", {"templates": templates})


@login_required
def device_detail(request, device_id):
    device = get_object_or_404(NetworkDevice, pk=device_id)

    # Get command history for this device
    netmiko_history = CommandHistory.objects.filter(device=device).order_by(
        "-executed_at"
    )[:5]
    nornir_history = NornirCommandHistory.objects.filter(device=device).order_by(
        "-executed_at"
    )[:5]

    # Combine and sort the history
    command_history = sorted(
        list(netmiko_history) + list(nornir_history),
        key=lambda x: x.executed_at,
        reverse=True,
    )[:10]

    return render(
        request,
        "core/device_detail.html",
        {
            "device": device,
            "command_history": command_history,
        },
    )
