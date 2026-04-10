# Лабораторная работа: JWT-аутентификация в FastAPI

## Задание 1. Подготовительный этап: создание проекта и первый коммит

1. Создайте новую директорию для проекта, назовите её `фамилия_инициалы_jwt` (например, `ivanov_ii_jwt`) и перейдите в неё.   
![](./PrtSc/1.png)    
2. Инициализируйте git-репозиторий командой `git init`.   
![](./PrtSc/2.png)    
3. Создайте файл `.gitignore` и добавьте стандартные исключения для Python-проектов (шаблон: https://github.com/github/gitignore/blob/main/Python.gitignore).   
![](./PrtSc/3.png)    
4. Инициализируйте проект при помощи `uv` командой `uv init`.   
![](./PrtSc/4.png)    
5. Создайте виртуальное окружение и установите необходимые пакеты:
   - `uv venv`
   - Активация: для Linux/macOS `source .venv/bin/activate`, для Windows `.venv\Scripts\activate`
   - `uv add fastapi uvicorn sqlalchemy alembic pydantic-settings python-jose[cryptography] passlib[bcrypt]`
   - Проверьте файл `pyproject.toml` – зависимости должны появиться в `[project.dependencies]`.   
![](./PrtSc/5.png)    
6. Создайте структуру директорий:
   - `app/`
     - `__init__.py`
     - `main.py`
     - `config.py`
     - `database.py`
     - `models/` (с `__init__.py`)
     - `schemas/` (с `__init__.py`)
     - `routers/` (с `__init__.py`)
     - `core/` (с `__init__.py`)   
![](./PrtSc/6.png)    
7. В `app/config.py` создайте базовый класс настроек с параметрами для JWT и БД (наследуйтесь от `BaseSettings`, используйте `SettingsConfigDict` для загрузки из `.env`).   
![](./PrtSc/7.png)    
8. В `app/database.py` настройте асинхронное подключение к SQLite: создайте асинхронный движок, фабрику сессий, декларативную базу и зависимость `get_db()`.   
![](./PrtSc/8.png)    
9. В `app/main.py` создайте минимальное приложение FastAPI с автогенерацией таблиц при старте и корневым эндпоинтом.   
![](./PrtSc/9.png)    
10. Запустите приложение командой `uvicorn app.main:app --reload`. Откройте `http://127.0.0.1:8000/docs` – документация должна быть доступна.   
![](./PrtSc/10.png)    
11. Сделайте первый коммит:
    - `git add .gitignore pyproject.toml uv.lock .python-version app/`
    - `git commit -m "init: базовое FastAPI приложение с настройками БД и JWT"`
   
![](./PrtSc/11.png)    
## Задание 2. Модель пользователя и CRUD (без хеширования)

1. Создайте файл `app/models/user.py` с моделью `User` (поля: `id`, `email`, `hashed_password`, `is_active`).   
![](./PrtSc/12_1.png)    
   
![](./PrtSc/12_2.png)    
2. В `app/models/__init__.py` импортируйте модель `User`.   
![](./PrtSc/13.png)    
3. Создайте Pydantic-схемы в `app/schemas/user.py`: `UserBase`, `UserCreate`, `User` (с конфигурацией `from_attributes = True`).   
![](./PrtSc/14.png)    
4. В `app/schemas/__init__.py` экспортируйте `User` и `UserCreate`.   
![](./PrtSc/15.png)    
5. Создайте роутер `app/routers/users.py` с эндпоинтами:
   - `POST /users/` – создание пользователя (пароль пока хранится открытым текстом).
   - `GET /users/` – список пользователей с пагинацией.
   - `GET /users/{user_id}` – получение пользователя по ID.   
![](./PrtSc/16.png)    
6. В `app/routers/__init__.py` экспортируйте роутер пользователей.
   
![](./PrtSc/17.png)    
7. Подключите роутер в `app/main.py`.
   
![](./PrtSc/18.png)    
8. Запустите приложение и через Swagger UI создайте пользователя (POST /users/). Убедитесь, что пользователь создаётся.   
![](./PrtSc/19_1.png)    
   
![](./PrtSc/19_2.png)       
![](./PrtSc/19_3.png)    
9. Сделайте коммит:
   - `git add app/models/ app/schemas/ app/routers/ app/main.py`
   - `git commit -m "feat: модель User и базовый CRUD (пароль открыт)"`
   
![](./PrtSc/20.png)    
## Задание 3. Хеширование паролей

1. В `app/core/security.py` создайте функции хеширования с использованием `passlib` (алгоритм `bcrypt`).   
![](./PrtSc/21.png)    
2. В роутере `users.py` импортируйте `get_password_hash` и замените прямое сохранение пароля на хеш.   
![](./PrtSc/22.png)    
3. Запустите приложение, создайте нового пользователя – в базе данных пароль должен храниться в захешированном виде.   
![](./PrtSc/23_1.png)       
![](./PrtSc/23_2.png)    
![](./PrtSc/23_3.png)    
4. Сделайте коммит:
   - `git add app/core/security.py app/routers/users.py`
   - `git commit -m "feat: добавлено хеширование паролей bcrypt"`
   
![](./PrtSc/24.png)    
## Задание 4. JWT: создание токенов и эндпоинт /token

1. В `app/core/security.py` добавьте функцию создания JWT-токена (`create_access_token`), используя библиотеку `python-jose` и настройки из `config.py`.   
![](./PrtSc/25.png)    
2. Создайте схему токена в `app/schemas/token.py`: классы `Token` и `TokenData`.   
![](./PrtSc/26.png)    
3. Обновите `app/schemas/__init__.py`, добавив экспорт схем токена.   
![](./PrtSc/27.png)    
4. Создайте роутер `app/routers/auth.py` с эндпоинтом `POST /token`. Используйте `OAuth2PasswordRequestForm` для получения email и пароля, проверьте пользователя и верните JWT.   
![](./PrtSc/28.png)    
5. В `app/routers/__init__.py` добавьте экспорт `auth_router`.   
![](./PrtSc/29.png)    
6. В `app/main.py` подключите `auth_router`.   
![](./PrtSc/30.png)    
7. Запустите приложение. В Swagger UI появится кнопка "Authorize". Выполните `POST /token` с параметрами username (email) и password – получите JSON с access_token.   
![](./PrtSc/31_1.png)   
   
![](./PrtSc/31_2.png)     
8. Сделайте коммит:
   - `git add app/core/security.py app/schemas/token.py app/routers/auth.py app/main.py`
   - `git commit -m "feat: добавлен JWT-эндпоинт /token"`
   
![](./PrtSc/32.png)    
## Задание 5. Защита маршрутов: зависимость get_current_user

1. В `app/core/security.py` добавьте функцию `get_current_user`, которая:
   - использует `OAuth2PasswordBearer` для извлечения токена,
   - декодирует JWT и проверяет подпись,
   - извлекает email и ищет пользователя в БД,
   - возвращает объект пользователя или выбрасывает 401.   
![](./PrtSc/33.png)    
2. Добавьте защищённый эндпоинт `GET /users/me` в `app/routers/users.py`, использующий `Depends(get_current_user)`.   
![](./PrtSc/34.png)    
3. Проверьте: откройте `/docs`, нажмите "Authorize", введите полученный ранее токен, затем вызовите `GET /users/me`. Должны получить данные текущего пользователя.   
![](./PrtSc/35_1.png)       
![](./PrtSc/35_2.png)    
4. Сделайте коммит:
   - `git add app/core/security.py app/routers/users.py`
   - `git commit -m "feat: добавлена защита маршрутов через get_current_user"`
   
![](./PrtSc/36.png)    
## Задание 6. OAuth2 Scopes: разграничение доступа

1. В модели `User` (файл `app/models/user.py`) добавьте поле `scopes` (строка, по умолчанию `"read:items"`).   
![](./PrtSc/37.png)    
2. При создании пользователя можно задавать scopes (оставьте по умолчанию).   
![](./PrtSc/38.png)    
3. В схеме `TokenData` (файл `app/schemas/token.py`) добавьте поле `scopes`.   
![](./PrtSc/39.png)    
4. При создании токена в функции `login` (роутер `auth.py`) включайте `scopes` пользователя в payload JWT.   
![](./PrtSc/40.png)    
5. Модифицируйте `get_current_user` для проверки scopes:
   - Добавьте параметр `security_scopes: SecurityScopes`.
   - В `oauth2_scheme` определите доступные scopes с описаниями.
   - Декодируйте scopes из токена и проверьте, что все требуемые scopes присутствуют. Если нет – выбросьте 403 Forbidden.   
![](./PrtSc/41.png)    
6. Создайте тестовый эндпоинт, требующий scope `read:items` (например, `GET /items/` в новом роутере `items.py`). Подключите роутер в `main.py`.   
![](./PrtSc/42.png)    
7. Проверьте:
   - Без токена – 401 Unauthorized.
   - С токеном, у которого нет scope `read:items` – 403 Forbidden.
   
![](./PrtSc/43_1.png)    
   
![](./PrtSc/43_2.png)    
8. Сделайте коммит:
   - `git add app/models/user.py app/schemas/token.py app/routers/auth.py app/core/security.py app/routers/items.py app/main.py`
   - `git commit -m "feat: добавлена поддержка scopes"`
   
![](./PrtSc/44.png)    
## Задание 7. Самостоятельная работа (дополнительные коммиты)

Каждый пункт должен быть отдельным коммитом с соответствующим префиксом (feat, fix, docs и т.д.).

1. **Добавьте refresh token**
   - Создайте таблицу `refresh_tokens` (связь с пользователем).
   - При логине выдавайте `refresh_token` (JWT с долгим сроком жизни).
   - Эндпоинт `/refresh` принимает refresh token, проверяет его и выдаёт новый access token.
   
![](./PrtSc/45.png)    
![](./PrtSc/46.png)       
![](./PrtSc/46_2.png)       
![](./PrtSc/46_3.png)       
![](./PrtSc/46_4.png)    
2. **Логирование действий**
   - Подключите стандартную библиотеку `logging` или `loguru`.
   - Логируйте попытки входа, ошибки аутентификации, доступ к защищённым ресурсам.
![](./PrtSc/47.png)    

3. **Роли пользователей (админ, обычный пользователь)**
   - Расширьте модель `User` полем `role` (значения `"admin"` или `"user"`).
   - При создании токена добавляйте роль в payload.
   - Напишите зависимость `require_role(role)`, проверяющую роль из токена.
   
![](./PrtSc/48_1.png)    
![](./PrtSc/48_2.png)       
![](./PrtSc/48_3.png)       
![](./PrtSc/48_4.png)    
4. **Тесты для аутентификации**
   - Установите `pytest`, `pytest-asyncio`, `httpx`.
   - Напишите тесты на регистрацию, логин, доступ к защищённому маршруту с валидным и невалидным токеном.
![](./PrtSc/49_2.png)       
5. **Документация в Swagger**
   - Добавьте детальные описания для всех эндпоинтов (summary, description, примеры ответов).
   - Убедитесь, что scopes отображаются в документации.
![](./PrtSc/50_1.png)       
![](./PrtSc/50_2.png)       