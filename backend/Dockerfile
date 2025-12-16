FROM python:3.11-slim

WORKDIR /app

# Evita cache inútil
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código
COPY . .

# Ajuste se o seu main for outro arquivo
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
