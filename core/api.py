from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import DeviceGroup, NetworkDevice


@api_view(["GET"])
def network_data(request):
    """
    API endpoint that returns network topology data for visualization
    """
    devices = NetworkDevice.objects.all()
    groups = DeviceGroup.objects.all()

    nodes = [
        {"id": device.name, "group": 1 if device.device_type == "router" else 2}
        for device in devices
    ]

    links = []
    for group in groups:
        group_devices = list(group.devices.all())
        if len(group_devices) > 1:
            for i in range(len(group_devices) - 1):
                links.append(
                    {
                        "source": group_devices[i].name,
                        "target": group_devices[i + 1].name,
                    }
                )

    return Response({"nodes": nodes, "links": links})
