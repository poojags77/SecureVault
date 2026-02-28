import getpass
from wallet import create_wallet, sign_message
from auth_client import register, login

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
                dashboard_menu()
            else:
                print("Login failed:", response)

        elif choice == "3":
            print("Exiting SecureVault.")
            break

        else:
            print("Invalid choice. Try again.")


def dashboard_menu():
    while True:
        print("\n=== Dashboard ===")
        print("1. Create Wallet")
        print("2. Sign Message")
        print("3. Logout")

        choice = input("Select option: ")

        if choice == "1":
            create_wallet()

        elif choice == "2":
            message = input("Enter message to sign: ")
            sign_message(message)

        elif choice == "3":
            print("Logged out.")
            break

        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    auth_menu()