from cryptography.fernet import Fernet
from src.config import config

cipher = Fernet(config.server.encryption_key.encode()) #utf-8 encoding bytes

def encrypt(string:str):
    return cipher.encrypt(string.encode()).decode()

def decrypt(string:str):
    return cipher.decrypt(string.encode()).decode()