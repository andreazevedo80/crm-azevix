# Use uma versão específica do Python para consistência
FROM python:3.11.8-slim

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0 libgdk-pixbuf-2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copia o arquivo de dependências primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o resto do código da aplicação para o contêiner
COPY . .

# Torna o script de inicialização executável
RUN chmod +x /app/boot.sh

# Expõe a porta que a aplicação irá usar
EXPOSE 5090

# Define o script de inicialização como o comando padrão do contêiner
CMD ["/app/boot.sh"]