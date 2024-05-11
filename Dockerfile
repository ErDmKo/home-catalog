FROM python:3.10-alpine as builder
WORKDIR /app

COPY requirements.txt /app
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip
RUN pip install -Ur requirements.txt --no-cache-dir

FROM python:3-slim
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="/opt/venv/lib/python3.10/site-packages"
EXPOSE 80
COPY . /app 


CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
