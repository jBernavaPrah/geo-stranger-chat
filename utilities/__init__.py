import fakeredis
import redis
import rom
import config


if config.DEBUG:
	rom.util.CONNECTION = fakeredis.FakeStrictRedis()
else:
	rom.util.CONNECTION = redis.Redis(host=config.redis_host, db=0)


