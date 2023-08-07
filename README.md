<h1>Реферальная система. Тестовое задание</h1>
<hr>
<h2>Технологии:</h2>
<p>Django, Django Rest Framework, Docker, docker-compose,
django-sms, phonenumberslite, flake8</p>
<hr>
<h3>Запуск проекта:</h3>
<ul>
    <li>git clone</li>
    <li>docker compose up --build</li>
</ul>
<hr>
<h3>Запуск юнит-тестов</h3>
<p>Проект должен быть запущен с Docker. Необходимо
войти в запущенный контейнер с помощью команды:</p>
docker exec -it django_service /bin/bash
<ul>
    <li>python manage.py test</li>
    или:
    <li>./manage.py test</li>
</ul>
<hr>
<h3>Тесты в Postman</h3>
https://api.postman.com/collections/27452224-63373f6d-e817-45c2-9b9b-f86c71a16991?access_key=PMAT-01H77XSVDH9Q0YP3MZ0FW95JBF
<p>Также при тестирование возникла проблема с CSRF-токен, в связи с чем пришлось закомментировать CSRFMiddleware в настройках проекта и добавить кастомный middleware.</p>
