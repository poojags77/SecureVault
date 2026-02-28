# 🔐 SecureVault CLI – Milestone 2

SecureVault CLI is a security-focused cryptocurrency wallet application with a hardened authentication backend.  
Milestone 2 focuses on secure key management, authentication security, and foundational threat modeling.

---

# 🚀 Features Implemented

- Secure key generation (ECDSA secp256k1)
- Encrypted private key storage (AES + PBKDF2)
- bcrypt password hashing
- JWT authentication
- Password strength validation
- Login attempt lockout (brute-force protection)
- STRIDE threat modeling
- Secure environment configuration

---

# 🛠 Technologies Used

- Python
- FastAPI
- SQLAlchemy
- bcrypt
- PyJWT
- cryptography
- SQLite
- Requests

---

# 📁 Project Structure

```
securevault/
│
├── backend/            # FastAPI authentication backend
├── cli/                # CLI wallet application
├── docs/               # Threat model & architecture docs
├── requirements.txt
└── .env
```


---

# ⚙️ How To Run The Project

Follow these steps carefully.

---

## 1️⃣ Clone Repository

```bash
git clone https://github.com/poojags77/SecureVault.git
cd SecureVault
```
## 2️⃣ Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Mac/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

You should see:

```bash
(venv)
```

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4️⃣ Create `.env` File

Create a file named `.env` in the root directory and add:

```env
SECRET_KEY=your_super_secret_key_here
JWT_EXPIRE_MINUTES=60
DATABASE_URL=sqlite:///./securevault.db
```
## 5️⃣ Start Backend Server

```bash
cd backend
uvicorn main:app --reload
```

Backend will run at:

```bash
http://127.0.0.1:8000
```

Swagger API documentation available at:

```bash
http://127.0.0.1:8000/docs
```

Keep this terminal running.

## 6️⃣ Run CLI Application

Open a new terminal window.

```bash
cd cli
python main.py
```

You will see:

```text
=== SecureVault CLI ===
1. Register
2. Login
3. Exit
```

## 🧪 Usage Flow

1. Register (password must meet strength requirements)
2. Login
3. Create Wallet
4. Sign Message
5. Logout

---

## 📁 Files Generated During Execution

| File            | Purpose                                      |
|-----------------|----------------------------------------------|
| securevault.db | Stores user accounts (SQLite database)      |
| wallet.dat     | Encrypted private key storage               |


## 🔐 Security Design Highlights

- Private keys never leave local machine
- No plaintext password storage
- bcrypt hashing with salt
- JWT-based authentication
- Brute-force protection via login lockout
- Environment-based secret configuration

---

## 🧠 Threat Modeling

STRIDE threat model implemented in:

```text
docs/threat_model.md
```

## 🎯 Milestone 2 Scope

This milestone establishes:

- Secure wallet foundation
- Secure authentication system
- Abuse-case handling
- Encrypted private key lifecycle
- Foundational secure system design

Future milestones will introduce:

- Attack simulation
- Payment integration
- Admin dashboard
- Deployment & domain setup

---

## 📜 License

Academic project – Cybersecurity coursework.
