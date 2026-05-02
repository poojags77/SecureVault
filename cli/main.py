import getpass
import time
import webbrowser

import requests

from auth_client import API_URL, auth_headers, login, parse_response, register
from wallet import create_wallet, sign_message


def print_error(message):
    print(f"❌ {message}")


def auth_menu():
    while True:
        print("\n=== SecureVault CLI ===")
        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Select option: ").strip()

        if choice == "1":
            username = input("Username: ").strip()
            print("Password must be at least 8 characters and include uppercase, lowercase, number, and special character.")
            password = getpass.getpass("Password: ")
            response = register(username, password)

            if "error" in response:
                print_error(response["error"])
            else:
                print(f"✅ {response['message']}")

        elif choice == "2":
            username = input("Username: ").strip()
            password = getpass.getpass("Password: ")
            response = login(username, password)

            if "access_token" in response:
                print("✅ Login successful.")
                dashboard_menu(response["access_token"])
            else:
                print_error(response.get("error", "Invalid credentials. Please try again."))

        elif choice == "3":
            print("Exiting SecureVault.")
            break

        else:
            print_error("Invalid option. Please choose 1, 2, or 3.")


def fetch_profile(token):
    response = requests.get(
        f"{API_URL}/profile",
        headers=auth_headers(token),
        timeout=10,
    )
    return parse_response(response)


def dashboard_menu(token):
    while True:
        try:
            profile = fetch_profile(token)
        except requests.RequestException as exc:
            print_error(f"Unable to reach backend: {exc}")
            return

        if "error" in profile:
            print_error(profile["error"])
            return

        role = profile["role"].upper()
        subscription = profile["subscription"].upper()
        role_icon = "👨‍💼" if profile["role"] == "admin" else "👤"
        subscription_icon = "🌟" if profile["subscription"] == "premium" else "🔒"

        print("\n=== SecureVault CLI ===")
        print(f"User: {profile['username']}")
        print(f"Role: {role} {role_icon}")
        print(f"Subscription: {subscription} {subscription_icon}")

        print("\n1. Create Wallet")
        print("2. Sign Message")
        print("3. Subscribe to Premium")
        print("4. Logout")

        if profile["subscription"] == "premium":
            print("5. Premium Security Scan")

        if profile["role"] == "admin":
            print("6. Admin Panel")

        choice = input("Select option: ").strip()

        if choice == "1":
            create_wallet()

        elif choice == "2":
            message = input("Enter message to sign: ")
            sign_message(message)

        elif choice == "3":
            subscribe_flow(token)

        elif choice == "4":
            print("Logged out.")
            break

        elif choice == "5" and profile["subscription"] == "premium":
            print("\n✅ Premium Feature Access Granted.")
            print("Running advanced security scan...")
            print("✅ No threats detected.")

        elif choice == "6" and profile["role"] == "admin":
            admin_panel(token)

        else:
            print_error("Invalid option for your current account permissions.")


def subscribe_flow(token):
    try:
        response = requests.post(
            f"{API_URL}/create-order",
            headers=auth_headers(token),
            timeout=15,
        )
        data = parse_response(response)
    except requests.RequestException as exc:
        print_error(f"Unable to create payment order: {exc}")
        return

    if "error" in data:
        print_error(data["error"])
        return

    order_id = data["order_id"]
    payment_url = f"{API_URL}{data['payment_url']}"

    print("\n✅ Payment order created.")
    print(f"Order ID: {order_id}")
    print("Opening payment page...")
    webbrowser.open(payment_url)

    print("Waiting for payment confirmation...")

    while True:
        try:
            status_res = requests.get(f"{API_URL}/payment-status/{order_id}", timeout=10)
            status = status_res.json()["status"]
        except (requests.RequestException, KeyError, ValueError) as exc:
            print_error(f"Unable to check payment status: {exc}")
            return

        if status == "success":
            verify = requests.post(
                f"{API_URL}/verify-payment",
                headers=auth_headers(token),
                timeout=10,
            )
            verify_data = parse_response(verify)
            if "error" in verify_data:
                print_error(verify_data["error"])
            else:
                print("\n✅ Payment successful. Premium activated.")
            break

        if status == "failed":
            print_error("Payment failed. Please try again.")
            break

        time.sleep(3)


def admin_panel(token):
    while True:
        print("\n=== ADMIN DASHBOARD ===")
        print("1. View Dashboard")
        print("2. Promote User to Admin")
        print("3. Upgrade User to Premium")
        print("4. Remove Premium")
        print("5. Back")

        choice = input("Select option: ").strip()

        if choice == "1":
            show_admin_dashboard(token)

        elif choice == "2":
            update_user(token, "/admin/make-admin", "Enter username to promote: ")

        elif choice == "3":
            update_user(token, "/admin/make-premium", "Enter username to upgrade: ")

        elif choice == "4":
            update_user(token, "/admin/remove-premium", "Enter username to downgrade: ")

        elif choice == "5":
            break

        else:
            print_error("Invalid option. Please choose a number from 1 to 5.")


def show_admin_dashboard(token):
    try:
        response = requests.get(
            f"{API_URL}/admin/dashboard",
            headers=auth_headers(token),
            timeout=10,
        )
        data = parse_response(response)
    except requests.RequestException as exc:
        print_error(f"Unable to fetch admin dashboard: {exc}")
        return

    if "error" in data:
        print_error(data["error"])
        return

    print("\nSYSTEM SUMMARY")
    print(f"Total Users: {data['summary']['total_users']}")
    print(f"Premium Users: {data['summary']['premium_users']}")
    print(f"Admin Users: {data['summary']['admin_users']}")

    print("\nUSER LIST")
    print("-" * 44)
    print(f"{'USERNAME':<16}{'ROLE':<12}{'SUBSCRIPTION'}")
    print("-" * 44)

    for user in data["users"]:
        print(f"{user['username']:<16}{user['role']:<12}{user['subscription']}")


def update_user(token, endpoint, prompt):
    username = input(prompt).strip()

    if not username:
        print_error("Username is required.")
        return

    try:
        response = requests.post(
            f"{API_URL}{endpoint}",
            params={"username": username},
            headers=auth_headers(token),
            timeout=10,
        )
        data = parse_response(response)
    except requests.RequestException as exc:
        print_error(f"Unable to update user: {exc}")
        return

    if "error" in data:
        print_error(data["error"])
    else:
        print(f"✅ {data['message']}")


if __name__ == "__main__":
    auth_menu()
