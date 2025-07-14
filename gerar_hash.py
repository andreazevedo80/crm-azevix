from werkzeug.security import generate_password_hash

# Coloque aqui a senha que você quer usar para todos os usuários de teste
senha_para_teste = "123456" 

# Gera o hash
hash_da_senha = generate_password_hash(senha_para_teste)

# Imprime o hash para você poder copiar
print("\nSeu hash de senha é:\n")
print(hash_da_senha)
print("\nCopie este código e use nos comandos UPDATE do psql.\n")