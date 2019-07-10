# flask-ghibli-proxy
a small project to show Celery integration. There is a periodic task which calls  https://ghibliapi.herokuapp.com/, makes some data manipulations and put the result in Redis.

Tested with Python 3

# Installation
To run a project:
* `cp env.example .env`
* install dependencies from requirements.txt
* `docker-compose up` # if you want to use your own redis then change .env file
* `celery -A main.celery worker -B --loglevel=info`
* `FLASK_APP=main.py flask run # it can be slow on a first run`
