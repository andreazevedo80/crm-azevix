#!/bin/sh

# Este script garante que o banco de dados seja criado antes de iniciar o servidor.

# Aborta o script se qualquer comando falhar
set -e

# Executa um comando Python para chamar nossa função 'init_db'
# O Flask é importado dentro do comando para garantir que tudo seja carregado corretamente.
echo "Aguardando o banco de dados iniciar..."
python -c "import time; time.sleep(5)" # Pequena pausa para garantir que o DB esteja pronto

echo "Inicializando o banco de dados..."
python -c "from backend import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

# Inicia o servidor Gunicorn
echo "Iniciando o servidor Gunicorn..."
exec gunicorn --bind 0.0.0.0:5090 --workers 4 --timeout 120 run:app