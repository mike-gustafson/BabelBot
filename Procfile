web: gunicorn babelbot.wsgi
release: python manage.py collectstatic --noinput && python manage.py migrate
