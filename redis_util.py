import redis
import os
import urlparser

'''jwt_redis_blocklist = redis.StrictRedis(
    host="localhost", port=6379, db=0, decode_responses=True
)'''
url = urlparser.urlparse(os.environ.get('REDIS_URL'))
jwt_redis_blocklist = redis.Redis(host=url.hostname, port=url.port, password=url.password)