import requests

API_URL = "http://127.0.0.1:8000"

def register(username, password):
    response = requests.post(
        f"{API_URL}/register",
        params={"username": username, "password": password}
    )
    return response.json()

def login(username, password):
    response = requests.post(
        f"{API_URL}/login",
        params={"username": username, "password": password}
    )
    return response.json()