FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependências Python
# Copiamos primeiro para aproveitar o cache do Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante da aplicação
COPY . .

# Expor porta
EXPOSE 5090

# Comando para iniciar a aplicação via Gunicorn
# O ponto de entrada agora é o objeto 'app' dentro de 'run.py'
CMD ["gunicorn", "--bind", "0.0.0.0:5090", "--workers", "4", "run:app"]