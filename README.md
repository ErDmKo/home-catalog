## Managment commands

### Install for develop
```bash
uv sync --all-extras
```

### Deploy
```bash
uv run manage.py deploy
```

### Format
```bash
uv run manage.py format
```

### Develop
```bash
uv run manage.py compile && uv run manage.py runserver
```
