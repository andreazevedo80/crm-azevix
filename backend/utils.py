from cryptography.fernet import Fernet
from validate_docbr import CNPJ
import os

# --- Lógica de Criptografia ---
# A chave de criptografia deve ser a mesma durante a vida da aplicação.
# Idealmente, ela também deveria vir de uma variável de ambiente.
# Por simplicidade, vamos gerá-la a partir da SECRET_KEY do Flask.
# ATENÇÃO: Se a SECRET_KEY mudar, os dados criptografados antigos não poderão ser lidos.
key = os.getenv('SECRET_KEY', 'default-key-for-dev-must-be-32-bytes').encode()
# A chave Fernet precisa ter 32 bytes. Vamos ajustá-la.
fernet_key = (key[:32]).ljust(32, b'\0')
cipher_suite = Fernet(fernet_key)

def encrypt_data(data: str) -> str:
    if not data:
        return None
    return cipher_suite.encrypt(data.encode()).decode('utf-8')

def decrypt_data(encrypted_data: str) -> str:
    if not encrypted_data:
        return None
    try:
        return cipher_suite.decrypt(encrypted_data.encode()).decode('utf-8')
    except Exception:
        return None # Retorna None se a descriptografia falhar

# --- Lógica de Validação ---
cnpj_validator = CNPJ()

def is_valid_cnpj(cnpj: str) -> bool:
    if not cnpj:
        return True # Permite CNPJ nulo
    return cnpj_validator.validate(cnpj)

def normalize_name(name: str) -> str:
    """Normaliza o nome para busca, removendo variações comuns."""
    if not name:
        return ""
    return name.upper().replace("LTDA", "").replace("S/A", "").replace(".", "").replace("/", "").replace("-", "").strip()