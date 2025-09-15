# Home Catalog

A Django application for managing home inventory with categorization and tracking features.

## Features

- Catalog grouping and item management
- User ownership of catalogs
- Invitation system for sharing catalogs
- RESTful API
- Google OAuth authentication
- Docker deployment support
- Ansible automation

## Development Setup

1. Install uv:
```bash
pip install uv
```

2. Install dependencies:
```bash
uv sync --all-extras
```

3. Set up the database:
```bash
uv run manage.py migrate
```

4. Create a superuser:
```bash
uv run manage.py createsuperuser
```

## Management Commands

### Development Server
```bash
uv run manage.py dev
```

### Format and Lint Code
```bash
uv run manage.py format
```

To automatically fix any fixable linting errors, run:
```bash
uv run manage.py format --fix
```

### Deploy
```bash
uv run manage.py deploy
```

## Testing

The project includes comprehensive tests for models, views, and functionality.

Before running the tests, make sure your database schema is up-to-date and static files are collected:
```bash
uv run manage.py migrate
uv run manage.py collectstatic
```

### Using Django's test runner:
```bash
uv run manage.py test
```

### Using pytest:
```bash
uv run pytest
```

### With coverage report:
```bash
# Run tests with coverage report
uv run manage.py test_coverage

# Run tests with coverage report and generate HTML report
uv run manage.py test_coverage --html
```

### Loading test data:
```bash
uv run manage.py loaddata catalog/fixtures/test_data.json
```

## Docker Operations

### Building Docker image:
```bash
uv run manage.py build
```

### Running locally with Docker:
```bash
uv run manage.py docker
```

## Project Structure

- `catalog/` - Main application directory
  - `models.py` - Database models
  - `tests.py` - Test suite
  - `admin.py` - Admin interface configuration
  - `management/commands/` - Custom management commands
- `home_catalog/` - Project settings and configuration
- `fixtures/` - Test data
- `Dockerfile` - Docker configuration
- `ansible/` - Deployment automation

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests to ensure everything works
4. Submit a pull request
