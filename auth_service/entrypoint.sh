#!/bin/bash

while ! nc -z "$REDIS_HOST" "$REDIS_PORT"; do
      echo "Waiting $REDIS_HOST"
      sleep 0.1
done

while ! nc -z "$AUTH_SERVICE_DB_HOST" "$AUTH_SERVICE_DB_PORT"; do
      echo "Waiting $AUTH_SERVICE_DB_HOST"
      sleep 0.1
done

# shellcheck disable=SC2164
cd src
alembic upgrade heads

echo "Waiting for users"
python commands/create_user.py --email=admin@mail.com --password=admin_password --first-name=admin --last-name=admin --access-level=5
python commands/create_user.py --email=staff@mail.com --password=staff_password --first-name=staff --last-name=staff --access-level=3
python commands/create_user.py --email=user@mail.com --password=user_password --first-name=user --last-name=user --access-level=1
python commands/create_user.py --email=staff_user@mail.com --password=staff_user_password --first-name=staff_user --last-name=staff_user --access-level=3
sleep 0.1

echo "Waiting for roles"
python commands/create_role.py --name=admin
python commands/create_role.py --name=user
python commands/create_role.py --name=staff
sleep 0.1

echo "Waiting for assigning roles to users"
python commands/assign_role.py --email=admin@mail.com --role=admin
python commands/assign_role.py --email=staff@mail.com --role=staff
python commands/assign_role.py --email=user@mail.com --role=user
python commands/assign_role.py --email=staff_user@mail.com --role=staff
python commands/assign_role.py --email=staff_user@mail.com --role=user
sleep 0.1


if [[ "$DEBUG" = "True" ]]
then
  uvicorn src.main:app --host "$AUTH_SERVICE_HOST" --port "$AUTH_SERVICE_PORT" --reload --workers "$AUTH_SERVICE_WORKERS" --log-level "$AUTH_SERVICE_LOG_LEVEL"
else
  gunicorn src.main:app --bind  "$AUTH_SERVICE_HOST:$AUTH_SERVICE_PORT" --workers "$AUTH_SERVICE_WORKERS" --log-level "$AUTH_SERVICE_LOG_LEVEL" -k uvicorn.workers.UvicornWorker
fi
