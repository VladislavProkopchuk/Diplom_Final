from locust import HttpUser, task, between


class QuickUser(HttpUser):
    wait_time = between(0.1, 0.5)

    def on_start(self):
        """ Регистрация нового пользователя и аутентификация """

        # Создание уникальных данных пользователя для регистрации
        import random
        username = f"testuser{random.randint(1, 100000)}"
        email = f"{username}@example.com"
        password = "testpassword"

        # Регистрация пользователя
        register_response = self.client.post("/api/register/", json={
            "username": username,
            "email": email,
            "first_name": "Test",
            "last_name": "User",
            "password": password
        })
        print("Register User:", register_response.status_code, register_response.json())

        # Аутентификация пользователя и получение токена
        login_response = self.client.post("/api/login/", json={
            "email": username,
            "password": password
        })
        print("Login User:", login_response.status_code, login_response.json())
        if login_response.status_code == 200:
            self.token = login_response.json().get('token')
        else:
            print("Error during login:", login_response.text)

    @task
    def load_product_list(self):
        """ Загрузка списка продуктов с высокой частотой """
        if hasattr(self, 'token'):
            with self.client.get("/api/products/", headers={"Authorization": f"Token {self.token}"},
                                 catch_response=True) as response:
                if response.status_code == 429:
                    response.failure("Rate limit exceeded")

    @task
    def add_to_cart(self):
        """ Добавление товара в корзину с высокой частотой """
        if hasattr(self, 'token'):
            product_info_id = 1  # ID товара
            self.client.post(
                "/api/cart/",
                json={"product_info_id": product_info_id, "quantity": 1},
                headers={"Authorization": f"Token {self.token}"},
                catch_response=True
            )
