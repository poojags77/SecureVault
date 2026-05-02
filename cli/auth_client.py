import requests

API_URL = "http://127.0.0.1:8000"


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def parse_response(response):
    try:
        data = response.json()
    except ValueError:
        return {"error": response.text or "Server returned an invalid response."}

    if response.status_code >= 400:
        return {"error": data.get("detail") or data.get("error") or "Request failed."}

    return data


def register(username, password):
    response = requests.post(
        f"{API_URL}/register",
        params={"username": username, "password": password},
        timeout=10,
    )
    return parse_response(response)


def login(username, password):
    response = requests.post(
        f"{API_URL}/login",
        params={"username": username, "password": password},
        timeout=10,
    )
    return parse_response(response)
