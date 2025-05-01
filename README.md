# Django Network Device Manager

A Django application for network device management using Netmiko library.

## Installation

```bash
# Clone repository
git clone https://github.com/example/django-network-manager.git
cd django-network-manager

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install django netmiko python-dotenv
```

## Configuration

1. Create `.env` file:

```ini
SECRET_KEY=your-django-secret-key
DEBUG=True
```

2. Database setup (SQLite by default):

```python
# network_manager/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

## Core Features

### Device Management

- CRUD operations for network devices
- Bulk import/export via CSV/Excel
- Device connection testing

### Command Execution

- Single device commands
- Bulk operations
- Command template library
- Output formatting and storage

### Security

- Encrypted credential storage using Django Cryptography
- Role-based access control
- Audit logging

## Database Models

```python
# netmiko_tools/models.py
class NetworkDevice(models.Model):
    hostname = models.CharField(max_length=100)
    device_type = models.CharField(max_length=50)
    ip_address = models.GenericIPAddressField()
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)  # Encrypted in implementation
    platform = models.CharField(max_length=50)

class CommandHistory(models.Model):
    device = models.ForeignKey(NetworkDevice, on_delete=models.CASCADE)
    command = models.TextField()
    output = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
```

## Usage

1. Add device:
   - Navigate to Devices > Add Device
   - Fill connection details
   - Test connection before saving

2. Execute commands:
   - Select devices from list
   - Choose command template or enter custom command
   - View real-time output

## API Endpoints

```python
# netmiko_tools/urls.py
path('api/devices/', DeviceListAPI.as_view()),
path('api/commands/', CommandHistoryAPI.as_view()),
```

## Optional Features

Enable in settings:

```python
# network_manager/settings.py
FEATURE_FLAGS = {
    'API_ENABLED': True,
    'SCHEDULED_TASKS': False,
    'CONFIG_BACKUPS': True
}
