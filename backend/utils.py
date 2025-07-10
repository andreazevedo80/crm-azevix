from cryptography.fernet import Fernet
from validate_docbr import CNPJ
import os

# --- Lógica de Criptografia ---

# 1. Pega a chave diretamente do seu arquivo .env
#    A chave já deve estar no formato correto (url-safe base64-encoded de 32 bytes)
key = os.getenv('SECRET_KEY')

# 2. Validação para garantir que a chave foi configurada
if not key:
    raise ValueError("Nenhuma SECRET_KEY foi encontrada no arquivo .env. Por favor, adicione a chave gerada.")

# 3. Cria o objeto de criptografia usando a chave
#    O .encode() a transforma em bytes, como a biblioteca espera.
try:
    cipher_suite = Fernet(key.encode())
except Exception:
    raise ValueError("A SECRET_KEY no arquivo .env não é uma chave Fernet válida.")


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

# --- Lógica de Validação de Documentos ---
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