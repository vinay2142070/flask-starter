import redis
import os

jwt_redis_blocklist =redis.from_url(os.environ['REDISCLOUD_URL'])