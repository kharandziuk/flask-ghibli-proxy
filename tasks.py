from celery import Celery
import requests

url = 'https://ghibliapi.herokuapp.com/films/'

app = Celery(
    'tasks',
    broker='redis://localhost/0',
    backend='redis://localhost/1'
)

@app.task
def add(x, y):
    return x + y
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(5.0, test.s('hello'), name='add every 10')

@app.task
def test(arg):
    resp = requests.get(url)
    data = resp.json() # Check the JSON Response Content documentation below
    print(data)
