import requests

url = "http://127.0.0.1:8000/api-token-auth/"
data = {
    "username": "your_username",  # Замените на реальный логин
    "password": "your_password",  # Замените на реальный пароль
}

response = requests.post(url, json=data)
print(response.json())
