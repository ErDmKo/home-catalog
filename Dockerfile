FROM python:3.10-alpine as builder
WORKDIR /app

COPY pyproject.toml /app
COPY uv.lock /app
ENV PATH="/app/.venv/bin:$PATH"
RUN pip install --upgrade pip
RUN pip install uv
RUN uv sync

ENV IS_LIVE=1
EXPOSE 80
COPY . /app 

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "home_catalog.asgi:application"]
