# homework_bot
Проект, в котором реализован Telegram-bot, который обращается к API-сервису Яндекс.Домашка и сообщает о статусе домашней работы: принята ли она или ревьюер внёс правки и её нужно доработать.
## Технологии
* Python 3

* Django REST Framework

* SQLite3

* SimpleJWT

## Запуск проекта

Копировать проект на рабочую машину:
```
git@github.com:Sausetardar/homework_bot.git
```

```
cd homework_bot
```
Создать виртуальное окружение:
```
py -m venv venv
```
И активировать его
```
source venv/Scripts/activate
```
Установить зависимости
```
pip install -r requirements.txt
```
Выполнить миграции
```
python3 manage.py migrate
```
