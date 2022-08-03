# Examiner
**Тестирование знаний претендентов.**

Нередко тратятся часы на проверку, знает ли очередной претендент, сколько будет ***2 + 2*** .  
В то время как можно это обернуть в оценочный сервис.

***

- [Python 3.10](https://www.python.org/ "Язык разработки")
- [Django 4.0](https://www.djangoproject.com/ "Фреймворк для веб-приложений")
- [Daphne 3.0](https://pypi.org/project/daphne/ "ASGI-сервер для UNIX от Django")
- [Pytest-django 4.5](https://pypi.org/project/pytest-django/ "Теститрует приложения Django с помощью  pytest")
- [Poetry 1.1](https://python-poetry.org/docs/ " Управление зависимостями ")

***
![Иллюстрация к проекту](https://github.com/Xewus/Examiner/blob/main/examiner.png)
***

### TODO
- Кэширование страниц и SQL-запросов.  
*Предполагается использование простейшего хостинга без доступа к установке дополнительных сервисов вроде `Redis` потому - кэш на файловой системе.*

- MySQL.  
*По тем же причинам, что указано выше.*

- Регистрация через e-mail.  
*Скорее всего через gmail.com. Как мимнмум, потому-что уже делали.*

- Добавить тесты.

***

#### TODODO (*далёкие планы*)
- Добавить тестируемые предметы.
- Добавить оценку времени (по-хорошему, тут нужен JS, а это не наше).

#### Directions
- Вход в **MySQL** (Устанавливается на сервер отдельно):

 > sudo mysql

- Создать БД для приложения:

`CREATE DATABASE  examiner_db CHARACTER SET UTF8;`

- Создать пользователя для подключения к БД под этим именем:

`CREATE USER 'examiner_user'@'localhost' IDENTIFIED BY 'password';`

- Выдать права указанному пользователю на управление БД:

`GRANT ALL PRIVILEGES ON examiner_db  TO 'examiner_user'@'localhost';`

- Убрать возможность раздавать доступы (можно сделать при выдаче прав, но слишком длинно. И необязательно.):

`REVOKE GRANT OPTION ON examiner_db.* FROM 'examiner_user'@'localhost';`

- Закрепить права:

`FLUSH PRIVILEGES;`

Далее используем стандартные минрационные команды Django.

