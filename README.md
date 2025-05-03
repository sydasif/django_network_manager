# Django Network Device Manager

A Django application for network device management using Netmiko library. This tool provides a web interface for managing and interacting with network devices through SSH connections.

## Features

- Manage multiple network devices (routers, switches, firewalls)
- Store device credentials securely
- Execute commands on network devices
- View command history and results
- User-friendly web interface
- Support for various device types (Cisco IOS, Juniper, etc.)

## Prerequisites

- Python 3.8 or higher
- Django 4.0 or higher
- Netmiko library
- PostgreSQL (recommended) or SQLite

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/django_network_manager.git
   cd django_network_manager
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows
   .\venv\Scripts\activate
   # On Linux/Mac
   source venv/bin/activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   Create a `.env` file in the project root and add:
   ```env
   DEBUG=True
   SECRET_KEY=your-secret-key
   DATABASE_URL=postgresql://user:password@localhost/dbname
   # Or for SQLite
   # DATABASE_URL=sqlite:///db.sqlite3
   ```

5. Run database migrations:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Usage

1. Access the admin interface at `http://localhost:8000/admin/`
2. Log in with your superuser credentials
3. Add network devices through the admin interface:
   - Provide device name, IP address, and credentials
   - Select appropriate device type
   - Set optional parameters like port and enable password

4. Access the main application at `http://localhost:8000/`
   - View list of configured devices
   - Execute commands on devices
   - View command history

## Security Considerations

- Store sensitive credentials in environment variables
- Use strong passwords for device access
- Implement proper user authentication and authorization
- Keep Django and all dependencies updated
- Use HTTPS in production

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository.
