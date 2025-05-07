# Cisco Lab Setup Configuration

## Router Configuration (R1)

1. **Access the Router:**
    Connect to the router using a console cable and terminal software.

2. **Basic Configuration:**

```plaintext
enable
configure terminal
hostname R1
```

3. **Interface Configuration:**
    Assign IP addresses to the interfaces:

```plaintext
interface GigabitEthernet0/0
ip address 192.168.1.1 255.255.255.0
no shutdown

interface GigabitEthernet0/1
ip address 192.168.2.1 255.255.255.0
no shutdown

interface GigabitEthernet0/2
ip address 192.168.3.1 255.255.255.0
no shutdown

interface GigabitEthernet0/3
ip address 192.168.4.1 255.255.255.0
no shutdown
```

4. **Routing Configuration:**
    Configure static routes or dynamic routing protocols as needed.

## Switch Configuration (SW-1)

1. **Access the Switch:**
    Connect to the switch using a console cable and terminal software.

2. **Basic Configuration:**

```plaintext
enable
configure terminal
hostname SW-1
```

3. **VLAN Configuration:**
    Create VLANs and assign ports:

```plaintext
vlan 10
name Site-01

vlan 20
name Site-02
```

4. **Interface Configuration:**
    Assign VLANs to interfaces:

```plaintext
interface GigabitEthernet0/0
switchport mode access
switchport access vlan 10

interface GigabitEthernet0/1
switchport mode access
switchport access vlan 20
```

## Access Switch Configuration (Access-1 and Access-2)

1. **Access the Switch:**
    Connect to the switch using a console cable and terminal software.

2. **Basic Configuration:**

```plaintext
enable
configure terminal
hostname Access-1
```

3. **VLAN Configuration:**
    Assign VLANs to interfaces:

```plaintext
interface Ethernet0/0
switchport mode access
switchport access vlan 10

interface Ethernet0/1
switchport mode access
switchport access vlan 10
```

Repeat similar steps for Access-2, assigning VLAN 20 to its interfaces.

## PC Configuration

1. **IP Configuration:**
    Assign IP addresses to the PCs in the respective VLANs.

2. **Testing Connectivity:**
    Use `ping` to test connectivity between devices.

## Troubleshooting

If you encounter any issues during setup, refer to the Cisco documentation or consult with your network administrator for assistance.