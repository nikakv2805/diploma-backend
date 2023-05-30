from redis import Redis
import os

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_DB = int(os.environ.get("REDIS_DB", "0"))
REDIS_USER = os.environ.get("REDIS_USER", "default")
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", "")

redis_client = Redis(host='gateway_redis', port=6379, db=0, username=REDIS_USER, password=REDIS_PASSWORD)

JWT_ACCESS_TOKEN_EXP = int(os.environ.get("JWT_ACCESS_TOKEN_EXP", 900))
JWT_REFRESH_TOKEN_EXP = int(os.environ.get("JWT_REFRESH_TOKEN_EXP", 1800))

class Blocklist:
    def __init__(self, redis_client: Redis = redis_client):
        self.redis_client = redis_client

    def in_blocklist(self, jti: str):
        if self.redis_client.get(jti):
            return True
        return False

    def put_blocklist(self, jti: str):
        self.redis_client.set(jti, 1, ex=max(JWT_ACCESS_TOKEN_EXP, JWT_REFRESH_TOKEN_EXP))


BLOCKLIST = Blocklist()
