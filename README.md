# SecureVault CLI – Milestone 1

## Features Implemented

- Secure key generation (ECDSA secp256k1)
- Encrypted private key storage (AES + PBKDF2)
- bcrypt password hashing
- JWT authentication
- Password strength validation
- Login attempt lockout
- STRIDE threat modeling
- Secure environment configuration

---

## Technologies Used

- Python
- FastAPI
- SQLAlchemy
- bcrypt
- PyJWT
- cryptography
- SQLite

---

## Security Focus

Milestone 1 focuses on:

- Private key lifecycle protection
- Authentication security
- Basic abuse-case handling
- Secure system design principles