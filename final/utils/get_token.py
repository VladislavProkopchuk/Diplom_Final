import requests

url = "http://127.0.0.1:8000/api-token-auth/"
data = {
    "username": "your_username",  # Имя
    "password": "your_password",  # Пароль (меняется на свой в целях безопасности, в открытом доступе не предоставлять)
}

response = requests.post(url, json=data)
print(response.json())
