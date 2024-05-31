import calendar
from datetime import datetime, timedelta

from sqlalchemy import text


def create_partitions(op, table_name: str = "users_login_history", months: int = 36) -> None:
    """creating partition by table_name"""
    current_date = datetime.utcnow()

    for _ in range(months):
        start_date = current_date.replace(day=1)
        end_date = (start_date + timedelta(days=calendar.monthrange(start_date.year, start_date.month)[1])).replace(
            day=1
        )

        partition_name = f"{table_name}_{start_date.strftime('%Y_%m')}"
        partition_start = start_date.strftime("%Y-%m-%d")
        partition_end = end_date.strftime("%Y-%m-%d")

        op.execute(
            text(
                f"""
                    CREATE TABLE IF NOT EXISTS {partition_name}
                    PARTITION OF {table_name}
                    FOR VALUES
                    FROM ('{partition_start}')
                    TO ('{partition_end}')
                    """
            )
        )
        current_date = end_date


def delete_partitions(op, table_name: str = "users_login_history") -> None:
    list_partitions_query = text(
        f"""
            SELECT tablename
            FROM pg_tables
            WHERE tablename LIKE '{table_name}_%';
        """
    )

    connection = op.get_bind()
    result = connection.execute(list_partitions_query)
    partitions = [row[0] for row in result.fetchall()]

    for partition_name in partitions:
        op.execute(text(f"DROP TABLE IF EXISTS {partition_name}"))
