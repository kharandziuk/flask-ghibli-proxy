import os
import json

from celery import Celery
from dotenv import load_dotenv
from flask import Flask, redirect, url_for, render_template
import redis
import requests

load_dotenv(verbose=True)

GHIBLI_API_URL = 'https://ghibliapi.herokuapp.com/films/'
CACHE_KEY_NAME = 'cache:films'

app = Flask(__name__)


def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=os.getenv('CELERY_BROKER_URL'),
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


celery = make_celery(app)
redis_client = redis.StrictRedis.from_url(
    os.getenv('REDIS_URL'), decode_responses=True)


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(60.0, set_cache.s(), name='set up current time')


def get_people_data(people_urls, film_url):
    # api behaves weird here: sometimes it returns a link for all the
    # characters from all the movies
    if people_urls == ['https://ghibliapi.herokuapp.com/people/']:
        people_data = requests.get(people_urls[0]).json()
        people_data = [
            entry for entry in people_data if film_url in entry['films']]
        return [entry['name'] for entry in people_data]
    else:
        return [
            requests.get(people_url).json()['name']
            for people_url in people_urls
        ]


def get_films_data():
    result = []
    films = requests.get(GHIBLI_API_URL).json()
    for film in films:
        people = get_people_data(film['people'], film['url'])
        result.append([film['title'], people])
    return result


@celery.task()
def set_cache():
    films_data = get_films_data()
    redis_client.set(
        CACHE_KEY_NAME,
        json.dumps(films_data)
    )


# we need it for a first run
if not redis_client.exists(CACHE_KEY_NAME):
    set_cache()


@app.route('/')
def root():
    return redirect(url_for('movies'))


@app.route('/movies', methods=['GET'])
def movies():
    films_json = redis_client.get(
        CACHE_KEY_NAME,
    )
    films = json.loads(films_json)
    return render_template('movies.html', films=films)
