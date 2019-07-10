import os

from flask import Flask
from celery import Celery
from dotenv import load_dotenv
import redis

load_dotenv(verbose=True)

CACHE_KEY_NAME = 'cache:films-template'
redis_host = "localhost"
redis_port = 6379
redis_password = ""

app = Flask(__name__)

app.config.update(
    CELERY_BROKER_URL=os.getenv('CELERY_BROKER_URL'),
    CELERY_RESULT_BACKEND=os.getenv('CELERY_RESULT_BACKEND')
)

redis_client = redis.StrictRedis(
        host=redis_host,
        port=redis_port,
        password=redis_password,
        decode_responses=True
        )

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
celery = make_celery(app)

time = ''
@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(1.0, set_response.s(), name='set up current time')

@celery.task()
def set_response():
    import datetime
    redis_client.set(CACHE_KEY_NAME, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

@app.route('/')
def hello_world():
    response = redis_client.get(CACHE_KEY_NAME)
    return response
