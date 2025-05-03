# Contributing to Django Network Manager

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Git Workflow](#git-workflow)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Security Guidelines](#security-guidelines)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

We are committed to providing a welcoming and inspiring community for all. Please treat all contributors with respect and help us maintain a positive environment.

## Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/django_network_manager.git
   cd django_network_manager
   ```

3. Set up the development environment:
   ```bash
   python -m venv venv
   # On Windows
   .\venv\Scripts\activate
   # On Linux/Mac
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```env
   DEBUG=True
   SECRET_KEY=your-secret-key
   DATABASE_URL=sqlite:///db.sqlite3
   ```

## Coding Standards

### Python Style Guide
- Follow PEP 8 style guide
- Use 4 spaces for indentation
- Maximum line length: 88 characters (compatible with black)
- Use descriptive variable names
- Add docstrings to all functions, classes, and modules

### Django Best Practices
- Use class-based views when appropriate
- Keep models thin, views fat
- Use model managers for complex queries
- Follow Django's security best practices
- Use Django's built-in features instead of reinventing the wheel

### Code Organization
- Keep related functionality together
- Use apps to separate distinct functionality
- Follow the Django app structure:
  ```
  app_name/
    ├── migrations/
    ├── templates/
    ├── static/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── urls.py
    ├── views.py
    └── tests.py
  ```

## Git Workflow

1. Create a new branch for each feature/bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit:
   ```bash
   git add .
   git commit -m "Description of changes"
   ```

3. Keep your branch updated:
   ```bash
   git fetch origin
   git rebase origin/main
   ```

4. Push your changes:
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Format
```
type(scope): Brief description

Longer description if needed

Resolves: #issue-number
```

Types: feat, fix, docs, style, refactor, test, chore

## Testing Guidelines

- Write tests for all new features and bug fixes
- Maintain test coverage above 80%
- Run tests before submitting PR:
  ```bash
  python manage.py test
  ```

### Test Structure
```python
from django.test import TestCase

class YourFeatureTests(TestCase):
    def setUp(self):
        # Setup test data
        pass

    def test_feature_behavior(self):
        # Test implementation
        pass
```

## Documentation

- Update documentation for new features
- Include docstrings in code
- Update README.md when needed
- Document API endpoints using docstrings

### Docstring Format
```python
def function_name(param1, param2):
    """Brief description.

    Detailed description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ExceptionType: Why this exception occurs
    """
    pass
```

## Security Guidelines

- Never commit sensitive data (API keys, passwords)
- Use environment variables for secrets
- Follow Django's security best practices
- Report security vulnerabilities privately
- Use HTTPS for all external communications

## Pull Request Process

1. Update documentation
2. Add/update tests
3. Ensure all tests pass
4. Update CHANGELOG.md if applicable
5. Request review from maintainers
6. Address review comments
7. Squash commits before merging

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Added new tests
- [ ] All tests passing

## Checklist
- [ ] Updated documentation
- [ ] Added to CHANGELOG
- [ ] Followed coding standards
```