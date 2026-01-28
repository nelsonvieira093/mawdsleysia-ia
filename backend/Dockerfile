FROM python:3.11-slim

# Diretório de trabalho
WORKDIR /app

# Configurações de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Dependências do sistema (necessárias para psycopg2)
RUN apt-get update && apt-get install -y \
  build-essential \
  && rm -rf /var/lib/apt/lists/*

# Dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código da aplicação
COPY . .

# Porta usada pelo Fly
EXPOSE 8080

# Comando de inicialização (VALIDADO)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
