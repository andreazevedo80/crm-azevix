from cryptography.fernet import Fernet
from validate_docbr import CNPJ
import os
import hashlib

# --- Lógica de Criptografia ---
key = os.getenv('SECRET_KEY')
if not key:
    raise ValueError("Nenhuma SECRET_KEY foi encontrada no arquivo .env.")
try:
    cipher_suite = Fernet(key.encode())
except Exception:
    raise ValueError("A SECRET_KEY no arquivo .env não é uma chave Fernet válida.")

def encrypt_data(data: str) -> str:
    if not data: return None
    return cipher_suite.encrypt(data.encode()).decode('utf-8')

def decrypt_data(encrypted_data: str) -> str:
    if not encrypted_data: return None
    try:
        return cipher_suite.decrypt(encrypted_data.encode()).decode('utf-8')
    except Exception:
        return None

# --- Lógica de Validação, Normalização e Hashing ---
cnpj_validator = CNPJ()

def normalize_cnpj(cnpj: str) -> str:
    """Remove toda a pontuação de um CNPJ, deixando apenas os dígitos."""
    if not cnpj: return None
    return ''.join(filter(str.isdigit, cnpj))

def format_cnpj(cnpj: str) -> str:
    """Aplica a máscara de formatação a uma string de dígitos de CNPJ."""
    if not cnpj or len(cnpj) != 14:
        return cnpj
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"

def get_cnpj_hash(cnpj: str) -> str:
    """Gera um hash SHA-256 determinístico para um CNPJ normalizado."""
    if not cnpj: return None
    normalized = normalize_cnpj(cnpj)
    return hashlib.sha256(normalized.encode()).hexdigest()

def is_valid_cnpj(cnpj: str) -> bool:
    if not cnpj: return True
    return cnpj_validator.validate(cnpj)

def normalize_name(name: str) -> str: # <--- NOME CORRIGIDO DE VOLTA
    """Normaliza o nome para busca, removendo variações comuns."""
    if not name: return ""
    return name.upper().replace("LTDA", "").replace("S/A", "").replace(".", "").replace("/", "").replace("-", "").strip()