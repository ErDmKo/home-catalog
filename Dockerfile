FROM python:3.10-alpine as builder
WORKDIR /app

COPY requirements.txt /app
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip
RUN pip install -Ur requirements.txt --no-cache-dir

ENV PYTHONPATH="/opt/venv/lib/python3.10/site-packages"
ENV IS_LIVE=1
EXPOSE 80
COPY . /app 

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "home_catalog.asgi:application"]
