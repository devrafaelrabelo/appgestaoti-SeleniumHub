# Etapa 1: Build
FROM python:3.12-slim as builder

WORKDIR /app

# Instala dependências de sistema necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
  gcc build-essential libldap2-dev libsasl2-dev \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --prefix=/install -r requirements.txt

# Etapa 2: Imagem final (mais leve)
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONPATH=/app

WORKDIR /app

COPY --from=builder /install /usr/local
COPY . .

EXPOSE 5000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]
