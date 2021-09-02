import redis
import os
import urllib.parse

'''jwt_redis_blocklist = redis.StrictRedis(
    host="localhost", port=6379, db=0, decode_responses=True
)'''
url = urllib.parse.urlparse(os.environ.get('REDIS_URL'))
jwt_redis_blocklist = redis.Redis(host=url.hostname, port=url.port, password=url.password)