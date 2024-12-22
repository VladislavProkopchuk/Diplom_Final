1. Регистрация пользователя

Создайте новый запрос:

* Метод: POST
* URL: `http://127.0.0.1:8000/api/register/`

Перейдите на вкладку "Headers" и добавить заголовок:

* Key: Content-Type
* Value: application/json

Перейдите на вкладку "Body", выберите "raw" и "JSON", затем вставьте следующие данные:
```yaml
{
    "username": "newuser",
    "email": "newuser@example.com",
    "first_name": "New",
    "last_name": "User",
    "password": "newpassword"
}
```

Ответ:
```yaml
{
    "status": "User created successfully"
}
```


2. Авторизация пользователя (для получения токена)

Создайте новый запрос:

* Метод: POST
* URL: `http://127.0.0.1:8000/api/auth/`

Перейдите на вкладку "Headers" и добавьте заголовок:

* Key: Content-Type
* Value: application/json

Перейдите на вкладку "Body", выбрать "raw" и "JSON", затем вставьте следующие данные:

```yaml
{
    "username": "newuser",
    "password": "newpassword"
}
```

Ответ:

```yaml
{
    "token": "your_auth_token"
}
```


3. Список товаров

Создайте новый запрос:

* Метод: GET
* URL: `http://127.0.0.1:8000/api/products/`

Перейдите на вкладку "Headers" и добавьте заголовок:

* Key: Authorization
* Value: Token your_auth_token

Ответ: JSON с списком доступных товаров.


4. Добавление товара в корзину

Создайте новый запрос:

* Метод: POST
* URL: `http://127.0.0.1:8000/api/cart/`

Перейдите на вкладку "Headers" и добавьте заголовок:

* Key: Authorization
* Value: Token your_auth_token


* Key: Content-Type
* Value: application/json

Перейдите на вкладку "Body", выберите "raw" и "JSON", затем вставьте следующие данные:

```yaml
{
    "product_info_id": 1,
    "quantity": 1
}
```

Ответ:

```yaml
{
    "status": "basket",
    "ordered_items": [
        {
            "product_info": 1,
            "quantity": 1
        }
    ]
    ... другие данные о необходимом товаре и покупателе
}
```

5. Просмотр корзины

Создайте новый запрос:

* Метод: GET
* URL: `http://127.0.0.1:8000/api/cart/`

Перейдите на вкладку "Headers" и добавьте заголовок:

* Key: Authorization
* Value: Token your_auth_token

Ответ: JSON с содержимым корзины.


6. Удаление товара из корзины

Создайте новый запрос:

* Метод: DELETE
* URL: `http://127.0.0.1:8000/api/cart/`

Перейдите на вкладку "Headers" и добавьте заголовок:

* Key: Authorization
* Value: Token your_auth_token


* Key: Content-Type
* Value: application/json


Перейдите на вкладку "Body", выберите "raw" и "JSON", затем вставьте следующие данные:

```yaml
{
    "product_info_id": 1
}
```

Ответ: JSON с данными о товаре


7. Создание контакта (адреса доставки)


Создайте новый запрос:

* Метод: POST
* URL: `http://127.0.0.1:8000/api/contacts/`

Перейдите на вкладку "Headers" и добавьте заголовок:

* Key: Authorization
* Value: Token your_auth_token


* Key: Content-Type
* Value: application/json

Перейдите на вкладку "Body", выберите "raw" и "JSON", затем вставьте следующие данные:

```yaml
{
    "type": "email",
    "value": "new_contact@example.com",
    "city": "Test City",
    "street": "Test Street",
    "house": "1",
    "structure": "",
    "building": "",
    "apartment": "1",
    "phone": "1234567890",
    "user": 1
}
```

Ответ: JSON с пользователем и адресом

8. Подтверждение заказа

Создайте новый запрос:

* Метод: POST
* URL: `http://127.0.0.1:8000/api/confirm_order/`

Перейдите на вкладку "Headers" и добавьте заголовок:

* Key: Authorization
* Value: Token your_auth_token


* Key: Content-Type
* Value: application/json

Перейдите на вкладку "Body", выберите "raw" и "JSON", затем вставьте следующие данные:
```yaml
{
    "order_id": 1,
    "contact_id": <id контакта с предыдущего шага>
}
```

Ответ:

```yaml
{
    "status": "Order confirmed",
    "email_status": "Email sent successfully"
}
```

9. Просмотр списка заказов

Создайте новый запрос:

* Метод: GET
* URL: `http://127.0.0.1:8000/api/orders/`

Перейдите на вкладку "Headers" и добавьте заголовок:

* Key: Authorization
* Value: Token your_auth_token


Ответ: JSON с списком заказов.

Пример:

```yaml
[
    {
        "id": 14,
        "user": 5,
        "dt": "2024-08-18T21:59:36.273865Z",
        "status": "confirmed",
        "contact": 18,
        "ordered_items": []
    }
]
```