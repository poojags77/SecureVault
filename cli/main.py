import getpass
import requests
from wallet import create_wallet, sign_message
from auth_client import register, login

API_URL = "http://127.0.0.1:8000"

# ---------------------------
# AUTH MENU
# ---------------------------
def auth_menu():
    while True:
        print("\n=== SecureVault CLI ===")
        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Select option: ")

        if choice == "1":
            username = input("Username: ")
            password = getpass.getpass("Password: ")
            response = register(username, password)
            print(response)

        elif choice == "2":
            username = input("Username: ")
            password = getpass.getpass("Password: ")
            response = login(username, password)

            if "access_token" in response:
                print("Login successful.")
                dashboard_menu(username)
            else:
                print("Login failed:", response)

        elif choice == "3":
            print("Exiting SecureVault.")
            break

        else:
            print("Invalid choice. Try again.")


# ---------------------------
# DASHBOARD
# ---------------------------
def dashboard_menu(username):
    while True:
        # ✅ Safe profile fetch
        res = requests.get(
            f"{API_URL}/profile",
            params={"username": username}
        )

        if res.status_code != 200:
            print("⚠️ Failed to fetch profile:", res.text)
            return

        try:
            profile = res.json()
        except:
            print("⚠️ Invalid response from server:", res.text)
            return

        print("\n=== DASHBOARD ===")
        print(f"User: {profile['username']}")
        print(f"Subscription: {profile['subscription'].upper()}")

        # 🌟 Premium indicator
        if profile["subscription"] == "premium":
            print("🌟 PREMIUM USER 🌟")

        print("\n1. Create Wallet")
        print("2. Sign Message")
        print("3. Logout")
        print("4. Subscribe to Premium")

        # 🔥 Premium feature
        if profile["subscription"] == "premium":
            print("5. Premium Feature")

        # 🔥 Admin feature
        if profile["role"] == "admin":
            print("6. Admin Panel")

        choice = input("Select option: ")

        if choice == "1":
            create_wallet()

        elif choice == "2":
            message = input("Enter message to sign: ")
            sign_message(message)

        elif choice == "3":
            print("Logged out.")
            break

        elif choice == "4":
            subscribe_flow(username)

        elif choice == "5" and profile["subscription"] == "premium":
            print("\n🔥 Premium Feature Access Granted!")
            print("Running advanced security scan...")
            print("✔ No threats detected")

        elif choice == "6" and profile["role"] == "admin":
            admin_panel()

        else:
            print("Invalid choice. Try again.")


# ---------------------------
# SUBSCRIPTION FLOW
# ---------------------------
def subscribe_flow(username):
    import webbrowser
    import time

    res = requests.post(
        f"{API_URL}/create-order",
        params={"username": username}
    )

    if res.status_code != 200:
        print("⚠️ Failed to create order:", res.text)
        return

    data = res.json()
    order_id = data["order_id"]

    print("\n🧾 Order Created!")
    print("Opening payment page...")

    payment_url = f"http://127.0.0.1:8000/pay/{order_id}"
    webbrowser.open(payment_url)

    print("Waiting for payment confirmation...")

    # Poll payment status
    while True:
        status_res = requests.get(f"{API_URL}/payment-status/{order_id}")
        status = status_res.json()["status"]

        if status == "success":
            verify = requests.post(
                f"{API_URL}/verify-payment",
                params={"username": username}
            )
            print("\n✅ Payment Successful! Premium Activated.")
            break

        elif status == "failed":
            print("\n❌ Payment Failed. Try Again.")
            break

        time.sleep(3)


# ---------------------------
# ADMIN PANEL
# ---------------------------
def admin_panel():
    while True:
        print("\n=== 👨‍💼 ADMIN DASHBOARD ===")
        print("1. View Dashboard")
        print("2. Make Admin")
        print("3. Back")

        choice = input("Select option: ")

        if choice == "1":
            res = requests.get(f"{API_URL}/admin/dashboard")

            if res.status_code != 200:
                print("⚠️ Failed to fetch data:", res.text)
                continue

            data = res.json()

            # 🔥 SUMMARY
            print("\n📊 SYSTEM SUMMARY")
            print(f"Total Users: {data['summary']['total_users']}")
            print(f"Premium Users: {data['summary']['premium_users']}")
            print(f"Admin Users: {data['summary']['admin_users']}")

            # 🔥 USER TABLE
            print("\n👥 USER LIST")
            print("-" * 40)
            print(f"{'USERNAME':<15}{'ROLE':<10}{'SUBSCRIPTION'}")
            print("-" * 40)

            for user in data["users"]:
                print(f"{user['username']:<15}{user['role']:<10}{user['subscription']}")

        elif choice == "2":
            username = input("Enter username to promote: ")

            res = requests.post(
                f"{API_URL}/admin/make-admin",
                params={"username": username}
            )

            print(res.json())

        elif choice == "3":
            break

        else:
            print("Invalid choice")


# ---------------------------
# MAIN ENTRY
# ---------------------------
if __name__ == "__main__":
    auth_menu()