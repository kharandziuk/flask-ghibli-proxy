import os

from flask import Flask
from celery import Celery
from dotenv import load_dotenv

load_dotenv(verbose=True)

app = Flask(__name__)

app.config.update(
    CELERY_BROKER_URL=os.getenv('CELERY_BROKER_URL'),
    CELERY_RESULT_BACKEND=os.getenv('CELERY_RESULT_BACKEND')
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

@celery.task()
def add_together(a, b):
    return a + b

@app.route('/')
def hello_world():
    result = add_together.delay(23, 42)
    r = result.get()
    return str(r)
