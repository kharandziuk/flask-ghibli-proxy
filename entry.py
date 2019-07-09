import requests
import ipdb
import redis
import json

redis_host = "localhost"
redis_port = 6379
redis_password = ""
CACHE_KEY_NAME = 'cache:films-template'
url = 'https://ghibliapi.herokuapp.com/films/'


r = redis.StrictRedis(
        host=redis_host,
        port=redis_port,
        password=redis_password,
        decode_responses=True
        )

print(r.get(CACHE_KEY_NAME))

resp = requests.get(url)

data = resp.json() # Check the JSON Response Content documentation below
data = [x['title'] for x in data]

r.set('cache:films-template', json.dumps(data))
