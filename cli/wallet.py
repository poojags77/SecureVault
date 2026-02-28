import getpass
import hashlib
from ecdsa import SigningKey, SECP256k1
from crypto_utils import generate_private_key, generate_address
from secure_storage import encrypt_private_key, decrypt_private_key

WALLET_FILE = "wallet.dat"

def create_wallet():
    password = getpass.getpass("Set wallet password: ")

    private_key = generate_private_key()
    address = generate_address(private_key.get_verifying_key())

    encrypted = encrypt_private_key(private_key.to_string(), password)

    with open(WALLET_FILE, "wb") as f:
        f.write(encrypted)

    print("Wallet created successfully.")
    print("Address:", address)

def sign_message(message):
    password = getpass.getpass("Enter wallet password: ")

    try:
        with open(WALLET_FILE, "rb") as f:
            encrypted = f.read()

        private_bytes = decrypt_private_key(encrypted, password)
        sk = SigningKey.from_string(private_bytes, curve=SECP256k1)

        message_hash = hashlib.sha256(message.encode()).digest()
        signature = sk.sign(message_hash)

        print("Signature:", signature.hex())

    except Exception:
        print("Invalid password or wallet corrupted.")