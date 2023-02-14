# Examiner
**Тестирование знаний претендентов.**

Нередко тратятся часы на проверку, знает ли очередной претендент, сколько будет ***2 + 2*** .  
В то время как можно это обернуть в оценочный сервис.

***

- [Python 3.10](https://www.python.org/ "Язык разработки")
- [Django 4.0](https://www.djangoproject.com/ "Фреймворк для веб-приложений")
- [Daphne 3.0](https://pypi.org/project/daphne/ "ASGI-сервер для UNIX от Django")
- [MySQL 8.0](https://www.mysql.com/ "Свободная реляционная система управления базами данных")
- [Pytest-django 4.5](https://pypi.org/project/pytest-django/ "Теститрует приложения Django с помощью  pytest")
- [Poetry 1.1](https://python-poetry.org/docs/ " Управление зависимостями ")

***
![Иллюстрация к проекту](https://github.com/Xewus/Examiner/blob/main/examiner.png)
***

### TODO
- Кэширование страниц и SQL-запросов.  
*Предполагается использование простейшего хостинга без доступа к установке дополнительных сервисов вроде `Redis` потому - кэш на файловой системе.*

- Регистрация через e-mail.  
*Скорее всего через gmail.com. Как мимнмум, потому-что уже делали.*

- Добавить тесты.

***

#### TODODO (*далёкие планы*)
- Добавить тестируемые предметы.
- Добавить оценку времени (по-хорошему, тут нужен JS, а это не наше).

***

#### Directions
- Создать файл `.env` со следующим содержанием:
```
DB_ENGINE='django.db.backends.mysql'
DB_NAME='examiner_db'
DB_USER='examiner_user'
DB_PASS='password'
DB_HOST='localhost'
DB_PORT=3306
DJANGO_SUPERUSER_USERNAME='admin'
DJANGO_SUPERUSER_EMAIL='admin@admin.admin'
DJANGO_SUPERUSER_PASSWORD='pass'
```
Запустить скрипт создающий БД для приложения (также будет создан администратор сайта с указанными в файле `.env` параметрами):
```
. create_db.sh
```
Запустить скрипт стартующий приложение:
```
python3 start_app.py 
```

***
### При желанни можно всё делать ручками. Например, команды для MySQL

- Вход в **MySQL** (Устанавливается на сервер отдельно):
```
 sudo mysql
```
- Создать БД для приложения:
```
CREATE DATABASE examiner_db CHARACTER SET UTF8;
```
```
USE examiner_db;
```
- Создать пользователя для подключения к БД под этим именем:

```
CREATE USER 'examiner_user'@'localhost' IDENTIFIED BY 'password';
```
- Выдать права указанному пользователю на управление БД:
```
GRANT ALL PRIVILEGES ON examiner_db.* TO 'examiner_user'@'localhost';
```
- Убрать возможность раздавать доступы (можно сделать при выдаче прав, но слишком длинно. И необязательно.):

```
REVOKE GRANT OPTION ON examiner_db.* FROM 'examiner_user'@'localhost';
```
- Закрепить права:
```
FLUSH PRIVILEGES;
```
- Покинуть **MySQL**:
```
quit
```
Далее используем стандартные минрационные команды Django.

