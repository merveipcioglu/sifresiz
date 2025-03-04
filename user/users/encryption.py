from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import hashlib

class AESCipher:
    def __init__(self):
        self.key = base64.b64decode('yrzgMaR0e3znt21Juq0EDRGJFkJUSCtAlZku+JB0jTA=')
        self.block_size = AES.block_size

    def encrypt(self, raw):
        if not raw:
            return raw
        raw_bytes = str(raw).encode('utf-8')
        cipher = AES.new(self.key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(raw_bytes, self.block_size))
        iv = base64.b64encode(cipher.iv).decode('utf-8')
        ct = base64.b64encode(ct_bytes).decode('utf-8')
        return f"{iv}:{ct}"

    def decrypt(self, enc):
        print(f"Decrypting: {enc}")
        if not enc:
            return enc
        try:
            iv, ct = enc.split(':')
            iv = base64.b64decode(iv)
            ct = base64.b64decode(ct)
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            pt = unpad(cipher.decrypt(ct), self.block_size)
            return pt.decode('utf-8')
        except ValueError as ve:
          print(f"Decryption failed - ValueError: {ve}")
        except Exception as e:
            print(f"Decryption failed: {e}")
            return None

def generate_hash(value):
    """Generate SHA-256 hash for a value"""
    if not value:
        return None
    return hashlib.sha256(str(value).lower().encode()).hexdigest() 