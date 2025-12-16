FROM python:3.11-slim



# Copia TODO o projeto
COPY . /app/backend

# Define PYTHONPATH corretamente
ENV PYTHONPATH=/app

WORKDIR /app/backend

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .
RUN npm run build
