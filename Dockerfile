FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

COPY sentinel /app/sentinel

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "sentinel.dashboard.app:app", "--host", "0.0.0.0", "--port", "8000"]
