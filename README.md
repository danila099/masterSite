# Сервис поиска и управления мастерами

Веб-приложение на Flask для поиска, добавления и управления мастерами и их услугами. Поддерживается регистрация пользователей, авторизация, а также административные функции (удаление мастеров).

## Возможности

- Регистрация и вход пользователей
- Просмотр списка мастеров и их услуг
- Добавление новых мастеров и услуг (форма)
- Удаление мастеров (только для администратора)
- Страницы "О нас" и "Контакты"(Можно заполнить под себя в about.html и contacts.html)
- Профиль пользователя

## Установка

1. **Клонируйте репозиторий:**
   ```bash
   git clone <URL-репозитория>
   cd <папка_проекта>
   ```

2. **Создайте виртуальное окружение (рекомендуется):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Установите зависимости:**
   ```bash
   pip install flask werkzeug
   ```

4. **Запустите приложение:**
   ```bash
   python main.py
   ```
   Приложение будет доступно по адресу: [http://localhost:8080](http://localhost:8080)

## Структура проекта

```
нет/
  main.py                # Основной файл приложения Flask
  users.db               # SQLite база данных (создаётся автоматически)
  templates/             # HTML-шаблоны для страниц
    404.html
    about.html
    base.html
    contacts.html
    createmaster.html
    index.html
    login.html
    master.html
    profile.html
    register.html
```

## Администрирование

- Для удаления мастеров используйте аккаунт с именем пользователя `admin`.
- Пароль администратора задаётся при регистрации пользователя с этим именем.

## Примечания

- При первом запуске автоматически создаются тестовые мастера и услуги.
- Для смены секретного ключа Flask замените строку `app.secret_key` в `main.py` на более сложное значение.

## Лицензия

MIT (или укажите вашу лицензию) 
