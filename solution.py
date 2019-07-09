from celery import Celery
import time

app = Celery(
    'test_celery',
    broker= 'redis://localhost/0'
)

app.conf.update(
    CELERY_RESULT_BACKEND = 'redis://localhost/1'
    )

@app.task
def add(x, y):
    time.sleep(2)
    return x + y

if __name__ == '__main__':
    result = add.delay(4, 4)
    print( result.wait() )
