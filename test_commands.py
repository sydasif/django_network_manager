from nornir_tools.utils import backup_config, run_commands, run_config_commands


def test_show_commands():
    """Test running show commands"""
    devices = ["Sw_01"]  # Replace with your device name
    commands = ["show running-config", "show ip interface brief"]
    result = run_commands(devices, commands, parallel=False)
    print("\n=== Show Commands Test ===")
    print("Commands:", commands)
    print("Results:", result)


def test_config_commands():
    """Test running config commands"""
    devices = ["Sw_01"]  # Replace with your device name
    config_commands = [
        "interface Loopback0",
        "description Test Interface",
        "no shutdown",
    ]
    result = run_config_commands(devices, config_commands, parallel=False)
    print("\n=== Config Commands Test ===")
    print("Commands:", config_commands)
    print("Results:", result)


def test_backup_config():
    """Test backup configuration"""
    devices = ["Sw_01"]  # Replace with your device name
    result = backup_config(devices, parallel=False)
    print("\n=== Backup Config Test ===")
    print("Results:", result)


if __name__ == "__main__":
    print("Starting validation tests...")
    test_show_commands()
    test_config_commands()
    test_backup_config()
    print("\nValidation complete!")
