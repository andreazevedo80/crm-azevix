-- Este script é executado pelo entrypoint do Docker PostgreSQL.
-- O usuário (azevix_admin) e o banco de dados (crm_azevix) são criados automaticamente
-- pelo Docker com base nas variáveis de ambiente POSTGRES_USER, POSTGRES_PASSWORD e POSTGRES_DB
-- definidas no docker-compose.yml.

-- Portanto, não é necessário (e causa erro) tentar CREATE USER ou CREATE DATABASE aqui.
-- O db.create_all() do Flask-SQLAlchemy em app.py cuidará da criação das tabelas.

-- Se você precisar de comandos SQL adicionais que não sejam criação de usuário/DB
-- (por exemplo, para criar extensões, funções ou inserir dados iniciais),
-- eles podem ser adicionados aqui, mas sem os blocos DO $$ ... $$ para CREATE DATABASE/USER.
-- Exemplo (se necessário, mas não para o seu caso atual):
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";