# Детальна документація до системи інвентаризації

## Технічний огляд

### Архітектура додатку

Додаток побудований з використанням наступних компонентів:
- **Frontend**: Flet (Python фреймворк для створення крос-платформних додатків)
- **База даних**: SQLite (зберігається у файлі `inventory.db`)
- **Мова програмування**: Python 3.8+

### Структура файлів

- `main.py` - Вхідна точка програми, ініціалізація додатку
- `db.py` - Взаємодія з базою даних
- `models.py` - Моделі даних
- `ui.py` - Графічний інтерфейс користувача
- `requirements.txt` - Залежності проекту
- `images/` - Директорія для зберігання зображень об'єктів

## Детальний опис функціоналу

### 1. Робота з інвентарем

#### Модель даних `InventoryItem`
```python
class InventoryItem:
    def __init__(self, id: int, name: str, quantity: int, inv_number: str, 
                 category: str, added_at: str, location_id: int, status: str, 
                 image_path: Optional[str], custom_fields: Optional[str], 
                 description: Optional[str]):
        self.id = id
        self.name = name
        self.quantity = quantity
        self.inv_number = inv_number
        self.category = category
        self.added_at = added_at
        self.location_id = location_id
        self.status = status
        self.image_path = image_path
        self.custom_fields = custom_fields
        self.description = description
```

#### Основні операції з БД

**Отримання списку об'єктів**
```python
def get_inventory(sort_by="name", ascending=True, filters=None):
    # Повертає список об'єктів інвентаризації
    # sort_by - поле для сортування
    # ascending - напрямок сортування
    # filters - словник фільтрів у форматі {поле: значення}
```

**Додавання нового об'єкта**
```python
def add_inventory(item):
    # Додає новий об'єкт інвентаризації
    # item - словник з даними об'єкта
```

**Оновлення існуючого об'єкта**
```python
def edit_inventory(item_id, item):
    # Оновлює дані об'єкта за ID
    # item_id - ID об'єкта для оновлення
    # item - словник з оновленими даними
```

**Видалення об'єкта**
```python
def delete_inventory(item_id):
    # Видаляє об'єкт за ID
    # Також автоматично видаляє пов'язані зображення
```

### 2. Керування місцями зберігання

#### Модель даних `Location`
```python
class Location:
    def __init__(self, id: int, name: str, parent_id: Optional[int]):
        self.id = id
        self.name = name
        self.parent_id = parent_id  # Для створення ієрархії
```

#### Основні операції
- `get_locations()` - отримання списку місць зберігання
- `add_location(name, parent_id)` - додавання нового місця
- `edit_location(loc_id, name, parent_id)` - редагування місця
- `delete_location(loc_id)` - видалення місця

### 3. Категорії та статуси

#### Отримання списків
- `get_categories()` - отримання списку категорій
- `get_statuses()` - отримання списку статусів

### 4. Експорт даних

#### Доступні формати експорту
- **CSV** - для подальшої обробки в електронних таблицях
- **PDF** - для друку або архівування

```python
def export_inventory(fmt="csv", filename="inventory_export"):
    # Експортує дані у вказаний формат
    # fmt - формат експорту ('csv' або 'pdf')
    # filename - ім'я файлу для експорту (без розширення)
```

### 5. Журнал змін

#### Модель даних `HistoryRecord`
```python
class HistoryRecord:
    def __init__(self, id: int, inventory_id: int, action: str, 
                 timestamp: str, details: str):
        self.id = id
        self.inventory_id = inventory_id
        self.action = action
        self.timestamp = timestamp
        self.details = details
```

#### Основні операції
- `log_history(inventory_id, action, details)` - додавання запису в журнал
- `get_history()` - отримання всіх записів журналу

## Інтеграція з іншими системами

### REST API (можливий розвиток)
Додаток може бути розширений для надання REST API для віддаленого керування через HTTP-запити.

### Імпорт/Експорт даних
Підтримується експорт у формати CSV та PDF. Для імпорту даних можна використовувати стандартні засоби обробки CSV-файлів.

## Розширення функціоналу

### Додавання нових полів
Для додавання нових полів до об'єктів інвентаризації використовуйте механізм користувацьких полів:

```python
def add_custom_field(name, field_type):
    # Додає нове користувацьке поле
    # name - назва поля
    # field_type - тип поля (наприклад, 'text', 'number', 'date')
```

### Кастомні звіти
Для створення кастомних звітів можна використовувати SQL-запити безпосередньо до бази даних або розширити функціонал експорту.

## Налагодження та логування

Додаток веде лог роботи у консолі. Для розширеного логування рекомендується додати модуль `logging`.

## Відомі обмеження

1. Розмір бази даних SQLite обмежений розміром диска
2. Відсутня підтримка одночасної роботи кількох користувачів
3. Відсутня авторизація та розмежування прав доступу

## Майбутні покращення

1. Додавання веб-інтерфейсу
2. Реалізація клієнт-серверної архітектури
3. Додавання системи авторизації
4. Підтримка роботи з зовнішніми API
5. Впровадження автоматичного резервного копіювання
