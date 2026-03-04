import redis.asyncio as aioredis
from redis.asyncio import Redis

_client: Redis | None = None


async def init_redis(url: str) -> None:
    global _client
    _client = aioredis.from_url(url, decode_responses=True, ssl_cert_reqs=None)


async def close_redis() -> None:
    if _client:
        await _client.aclose()


def get_redis() -> Redis:
    return _client
