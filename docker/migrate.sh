#!/bin/sh
set -e

until nc -z postgres 5432; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

echo "Waiting 10 seconds..."
sleep 10

echo "Running migrations..."
exec alembic upgrade head
