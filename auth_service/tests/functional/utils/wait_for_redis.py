import backoff
from redis import Redis
from redis.exceptions import ConnectionError
from tests.functional.settings import test_settings


def backoff_hdlr(details):
    print(
        "Backing off {wait:0.1f} seconds after {tries} tries "
        "calling function {target} with args {args} and kwargs "
        "{kwargs}".format(**details)
    )


@backoff.on_exception(backoff.expo, ConnectionError, max_time=60, on_backoff=backoff_hdlr)
def wait_for_redis():
    redis_client = Redis(host=test_settings.redis_host, port=test_settings.redis_port, db=0)

    redis_ping = redis_client.ping()
    if redis_ping:
        return redis_ping

    raise ConnectionError


if __name__ == "__main__":
    wait_for_redis()
