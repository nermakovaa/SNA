from redis import Redis
import json



r = Redis(host='localhost', port=6379, decode_responses=True)


def redis_get(key):
    return json.loads(r.get(key))
