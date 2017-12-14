import redis
import rom
import config

rom.util.CONNECTION = redis.Redis(host=config.redis_host, db=1)
