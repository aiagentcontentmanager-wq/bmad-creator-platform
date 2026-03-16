FROM python:3.11-slim

RUN addgroup --system app && adduser --system --group app

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY config ./config
COPY landing ./landing
COPY .env.example .env

RUN mkdir -p /app/data && chown -R app:app /app
USER app

EXPOSE 8000

ENV PYTHONPATH=/app
ENV DATABASE_PATH=/app/data/bmad.db
ENV ENV=production

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
