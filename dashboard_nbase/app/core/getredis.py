import redis
import os

timeout = 20

""" Get acrus connection singleton object
"""
_redis = None

def get_client() :

	global _redis
	if _redis: 
		return _redis
	else :
		_redis = redis.StrictRedis(
			host = os.environ.get('REDIS_HOST', 'localhost'),
			port = int(os.environ.get('REDIS_PORT', '6000')),
			db = 0
		)

		return _redis

