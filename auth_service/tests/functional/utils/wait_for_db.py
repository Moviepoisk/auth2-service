import backoff
import psycopg2
from tests.functional.settings import test_settings


def backoff_hdlr(details):
    print(
        "Backing off {wait:0.1f} seconds after {tries} tries "
        "calling function {target} with args {args} and kwargs "
        "{kwargs}".format(**details)
    )


@backoff.on_exception(backoff.expo, psycopg2.OperationalError, max_time=60, on_backoff=backoff_hdlr)
def wait_for_db():
    pg_conn = psycopg2.connect(**test_settings.get_postgres_dsn())

    cur = pg_conn.cursor()
    cur.execute("SELECT 1")


if __name__ == "__main__":
    wait_for_db()
