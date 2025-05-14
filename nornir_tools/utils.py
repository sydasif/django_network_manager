from typing import Any, Dict, List

from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config

from .models import NornirCommandHistory
from netmiko_tools.models import NetworkDevice


def create_nornir_inventory() -> Dict[str, Any]:
    """Create Nornir inventory from NetworkDevice model."""
    inventory = {
        "hosts": {},
        "groups": {
            "global": {
                "platform": "cisco_ios",  # default platform
                "connection_options": {
                    "netmiko": {
                        "extras": {
                            "session_log": "nornir_session.log",
                        }
                    }
                },
            }
        },
    }

    for device in NetworkDevice.objects.filter(is_active=True):
        inventory["hosts"][device.name] = {
            "hostname": device.ip_address,
            "username": device.username,
            "password": device.password,
            "platform": device.device_type,
            "port": device.port,
            "connection_options": {
                "netmiko": {
                    "extras": {
                        "secret": (
                            device.enable_password if device.enable_password else ""
                        )
                    }
                }
            },
        }

    return inventory


def init_nornir(num_workers: int = 10) -> InitNornir:
    """Initialize Nornir with inventory from database.

    Args:
        num_workers: Number of worker threads for parallel execution
    """
    import tempfile

    import yaml

    # Create temporary directory for inventory files
    tmp_dir = tempfile.mkdtemp()
    inventory = create_nornir_inventory()

    # Write inventory files
    hosts_file = f"{tmp_dir}/hosts.yaml"
    groups_file = f"{tmp_dir}/groups.yaml"
    defaults_file = f"{tmp_dir}/defaults.yaml"

    with open(hosts_file, "w") as f:
        yaml.safe_dump(inventory["hosts"], f)
    with open(groups_file, "w") as f:
        yaml.safe_dump(inventory["groups"], f)
    with open(defaults_file, "w") as f:
        yaml.safe_dump({}, f)

    nr = InitNornir(
        inventory={
            "plugin": "SimpleInventory",
            "options": {
                "host_file": hosts_file,
                "group_file": groups_file,
                "defaults_file": defaults_file,
            },
        },
        logging={
            "enabled": True,
            "level": "DEBUG",
            "to_console": True,
            "log_file": "nornir.log",
        },
        runner={"plugin": "threaded", "options": {"num_workers": num_workers}},
    )
    return nr


def run_commands(
    devices: List[str], commands: List[str], parallel: bool = True
) -> Dict:
    """
    Run show commands on selected devices.

    Args:
        devices: List of device names
        commands: List of commands to run
        parallel: Whether to run commands in parallel
    """
    # Initialize Nornir with appropriate number of workers
    nr = init_nornir(num_workers=10 if parallel else 1)
    nr = nr.filter(filter_func=lambda h: h.name in devices)

    results = {}
    for command in commands:
        try:
            result = nr.run(
                task=netmiko_send_command,
                command_string=command,
                enable=True,
                use_textfsm=False,  # Disable TextFSM to get raw output
                use_timing=True,  # Use timing mode for more reliable output
            )
            # Check if there were any failures
            failed_hosts = [
                host for host, host_data in result.items() if host_data.failed
            ]
            if failed_hosts:
                failures = {host: str(result[host].exception) for host in failed_hosts}
                results[command] = {"status": "failed", "failures": failures}

                # Save failed command history
                for host, error in failures.items():
                    device = NetworkDevice.objects.get(name=host)
                    NornirCommandHistory.objects.create(
                        device=device, command=command, output=error, status="failed"
                    )
            else:
                # Extract the actual command output from successful results
                outputs = {
                    host: host_data[0].result for host, host_data in result.items()
                }
                results[command] = {"status": "success", "outputs": outputs}

                # Save successful command history
                for host, output in outputs.items():
                    device = NetworkDevice.objects.get(name=host)
                    NornirCommandHistory.objects.create(
                        device=device, command=command, output=output, status="success"
                    )
        except Exception as e:
            results[command] = {"status": "error", "error": str(e)}

    return results


def run_config_commands(
    devices: List[str], config_commands: List[str], parallel: bool = True
) -> Dict:
    """
    Run configuration commands on selected devices.

    Args:
        devices: List of device names
        config_commands: List of configuration commands
        parallel: Whether to run commands in parallel
    """
    # Initialize Nornir with appropriate number of workers
    nr = init_nornir(num_workers=10 if parallel else 1)
    nr = nr.filter(filter_func=lambda h: h.name in devices)

    try:
        result = nr.run(
            task=netmiko_send_config, config_commands=config_commands, enable=True
        )

        # Check if there were any failures
        failed_hosts = [host for host, host_data in result.items() if host_data.failed]

        results = {}
        if failed_hosts:
            failures = {host: str(result[host].exception) for host in failed_hosts}
            results = {"status": "failed", "failures": failures}

            # Save failed command history
            for host, error in failures.items():
                device = NetworkDevice.objects.get(name=host)
                NornirCommandHistory.objects.create(
                    device=device,
                    command="\n".join(config_commands),
                    output=error,
                    status="failed",
                )
        else:
            # Extract the actual command output from successful results
            outputs = {host: host_data[0].result for host, host_data in result.items()}
            results = {"status": "success", "outputs": outputs}

            # Save successful command history for each device
            for host, output in outputs.items():
                device = NetworkDevice.objects.get(name=host)
                NornirCommandHistory.objects.create(
                    device=device,
                    command="\n".join(config_commands),
                    output=output or "Configuration applied successfully",
                    status="success",
                )

        return results

    except Exception as e:
        return {"status": "error", "error": str(e)}


def backup_config(devices: List[str], parallel: bool = True) -> Dict:
    """Backup running configuration of selected devices.

    Args:
        devices: List of device names
        parallel: Whether to run commands in parallel
    """
    nr = init_nornir(num_workers=10 if parallel else 1)
    nr = nr.filter(filter_func=lambda h: h.name in devices)

    try:
        result = nr.run(
            task=netmiko_send_command, command_string="show running-config", enable=True
        )

        # Check if there were any failures
        failed_hosts = [host for host, host_data in result.items() if host_data.failed]

        results = {}
        if failed_hosts:
            failures = {host: str(result[host].exception) for host in failed_hosts}
            results = {"status": "failed", "failures": failures}

            # Save failed command history
            for host, error in failures.items():
                device = NetworkDevice.objects.get(name=host)
                NornirCommandHistory.objects.create(
                    device=device,
                    command="show running-config",
                    output=error,
                    status="failed",
                )
        else:
            # Extract the actual command output from successful results
            outputs = {host: host_data[0].result for host, host_data in result.items()}
            results = {"status": "success", "outputs": outputs}

            # Save successful command history for each device
            for host, output in outputs.items():
                device = NetworkDevice.objects.get(name=host)
                NornirCommandHistory.objects.create(
                    device=device,
                    command="show running-config",
                    output=output,
                    status="success",
                )

        return results

    except Exception as e:
        return {"status": "error", "error": str(e)}
