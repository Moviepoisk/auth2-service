#!/bin/bash

while ! nc -z "$REDIS_HOST" "$REDIS_PORT"; do
      echo "Waiting $REDIS_HOST"
      sleep 0.1
done

while ! nc -z "$AUTH_SERVICE_DB_HOST" "$AUTH_SERVICE_DB_PORT"; do
      echo "Waiting $AUTH_SERVICE_DB_HOST"
      sleep 0.1
done

cd src
alembic upgrade heads


echo "Waiting for users"
python commands/create_users.py
sleep 0.1

echo "Waiting for roles"
python commands/create_roles.py
sleep 0.1

echo "Waiting for assigning roles to users"
python commands/assign_roles.py
sleep 0.1


if [[ "$DEBUG" = "True" ]]
then
  uvicorn src.main:app --host "$AUTH_SERVICE_HOST" --port "$AUTH_SERVICE_PORT" --reload --workers "$AUTH_SERVICE_WORKERS" --log-level "$AUTH_SERVICE_LOG_LEVEL"
else
  gunicorn src.main:app --bind  "$AUTH_SERVICE_HOST:$AUTH_SERVICE_PORT" --workers "$AUTH_SERVICE_WORKERS" --log-level "$AUTH_SERVICE_LOG_LEVEL" -k uvicorn.workers.UvicornWorker
fi
