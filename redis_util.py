import redis
import os

'''jwt_redis_blocklist = redis.StrictRedis(
    host="localhost", port=6379, db=0, decode_responses=True
)'''
jwt_redis_blocklist=os.getenv("REDIS_URL") 