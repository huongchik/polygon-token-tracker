# Описание

Этот проект состоит из двух основных компонентов:

1. Основной скрипт: Выполняет операции с токенами ERC20 на сети Polygon, такие как получение баланса, получение топ-адресов, и получение информации о токене.
2. Сервер Flask: Предоставляет HTTP API для взаимодействия с функциями основного скрипта.

## Зависимости

Убедитесь, что у вас установлены все необходимые зависимости: `pip install -r requirements.txt`.

### Переменные окружения
Создайте файл .env в корневой директории проекта с содержимым:
```makefeile
POLYGON_RPC_URL=https://polygon-rpc.com
TOKEN_ADDRESS=0x1a9b54a3075119f1546c52ca0940551a6ce5d2d0
POLYGONSCAN_API_KEY=your_polygonscan_api_key
```

### Запуск сервера
```python
python server.py
```
Сервер будет работать на http://localhost:8080.

### Конечные точки API
#### Получение баланса адреса
Запрос:

- Метод: GET
- URL: /get_balance
- Параметры:
    - address (обязательный): Адрес кошелька для проверки баланса.
Пример запроса:
```python
GET http://localhost:8080/get_balance?address=
```
#### Получение балансов нескольких адресов
Запрос:

- Метод: POST
- URL: /get_balance_batch
- Тело запроса:
    ```python
    {
        "addresses": [
    
        ]
  }
    ```

Пример запроса:
```python
POST http://localhost:8080/get_balance_batch
Content-Type: application/json

{
  "addresses": [

  ]
}

```
#### Получение топ-адресов с последними транзакциями
Запрос:

- Метод: GET
- URL: /get_top_with_transactions
- Параметры:
    - N (обязательный): Количество топ-адресов.
    - token_address (обязательный): Адрес токена. 
Пример запроса:
```python
GET http://localhost:8080/get_top_with_transactions?N=10&token_address=
```
#### Получение информации о токене
Запрос:

- Метод: GET
- URL: /get_token_info
- Параметры:
    - token_address (обязательный): Адрес токена.
Пример запроса:
```python
GET http://localhost:8080/get_token_info?token_address=
```

### Тестирование
Тесты для сервера написаны с использованием unittest и могут быть выполнены следующей командой:
```python
python -m unittest tests.py
```
### Примечания
Убедитесь, что вы используете правильный адрес токена ERC20 и адреса кошельков.
Для запросов к API требуется работающий экземпляр сервера на http://localhost:8080.

