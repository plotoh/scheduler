Программа представляет из себя бэкенд логику сервиса уведомлений с примитивным функционалом авторизации (регистрация и аутентификация) и добавления задач(создать задачу, получить).

Хэндлеры в папке src/api
Pydantic схемы в папке src/schemas
Бизнес лоигка в папке src/service

Также внедрена подключение к бд как зависимость - dependencies.py
Файл database.py - подключение к БД, инициализация таблиц. 
config - конфиг как pydantic схема

src

|..config.py

|..database.py

|..dependencies.py

|..main.py

|..+---api

|...|..  auth.py

|...|..  notification.py

|...|..  __init__.py

|..+---schemas

|...|..  auth.py

|...|..  notification.py

|...|..  __init__.py

|..+---service

|...|..  auth.py

|...|..  notification.py
