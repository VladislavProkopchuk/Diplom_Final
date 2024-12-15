import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"


# Регистрация пользователя
def register_user():
    url = f"{BASE_URL}/register/"
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "testpassword",
    }
    response = requests.post(url, json=data)
    print("Register User:", response.status_code, response.json())


# Авторизация пользователя
def login_user():
    url = f"{BASE_URL}/login/"
    data = {"email": "testuser", "password": "testpassword"}
    response = requests.post(url, json=data)
    print("Login User:", response.status_code, response.json())
    if response.status_code == 200:
        return response.json().get("token")
    return None


# Получение списка товаров
def get_product_list(token):
    url = f"{BASE_URL}/products/"
    headers = {"Authorization": f"Token {token}"}
    response = requests.get(url, headers=headers)
    print("Product List:", response.status_code, response.json())


# Добавление товара в корзину
def add_to_cart(token, product_info_id, quantity):
    url = f"{BASE_URL}/cart/"
    headers = {"Authorization": f"Token {token}"}
    data = {"product_info_id": product_info_id, "quantity": quantity}
    response = requests.post(url, json=data, headers=headers)
    print("Add to Cart:", response.status_code, response.json())


# Создание контакта (адреса доставки)
def create_contact(token, user_id):
    url = f"{BASE_URL}/contacts/"
    headers = {"Authorization": f"Token {token}"}
    data = {
        "user": user_id,
        "type": "email",
        "value": "contact@example.com",
        "city": "Test City",
        "street": "Test Street",
        "house": "1",
        "structure": "",
        "building": "",
        "apartment": "1",
    }
    response = requests.post(url, json=data, headers=headers)
    print("Create Contact:", response.status_code, response.json())
    if response.status_code == 201:
        return response.json().get("id")
    return None


# Подтверждение заказа
def confirm_order(token, contact_id):
    url = f"{BASE_URL}/orders/confirm/"
    headers = {"Authorization": f"Token {token}"}
    data = {"contact_id": contact_id}
    response = requests.post(url, json=data, headers=headers)
    print("Confirm Order:", response.status_code, response.json())


# Получение списка заказов
def get_order_list(token):
    url = f"{BASE_URL}/orders/"
    headers = {"Authorization": f"Token {token}"}
    response = requests.get(url, headers=headers)
    print("Order List:", response.status_code, response.json())


def main():
    register_user()
    token = login_user()
    if not token:
        print("Authentication failed. Exiting...")
        return

    user_id = 3  # замените на реальный ID пользователя
    get_product_list(token)

    # Пример ID товара и количество
    product_info_id = 1  # замените на реальный ID продукта
    quantity = 2
    add_to_cart(token, product_info_id, quantity)

    contact_id = create_contact(token, user_id)
    if not contact_id:
        print("Creating contact failed. Exiting...")
        return

    confirm_order(token, contact_id)
    get_order_list(token)


if __name__ == "__main__":
    main()
