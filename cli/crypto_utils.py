from ecdsa import SigningKey, SECP256k1
import hashlib
import base58

def generate_private_key():
    return SigningKey.generate(curve=SECP256k1)

def generate_address(public_key):
    pub_bytes = public_key.to_string()
    sha = hashlib.sha256(pub_bytes).digest()
    ripemd = hashlib.new('ripemd160', sha).digest()
    return base58.b58encode(ripemd).decode()