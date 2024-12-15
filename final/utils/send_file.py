import requests

url = "http://127.0.0.1:8000/api/import/"
headers = {
    "Authorization": "Token <token>",  # Замените на ваш реальный токен
}
files = {
    "file": open(
        "path/to/your/file.yaml", "rb"
    )  # Замените 'path/to/your/file.yaml' на реальный путь к файлу
}

response = requests.post(url, headers=headers, files=files)
print(response.json())
