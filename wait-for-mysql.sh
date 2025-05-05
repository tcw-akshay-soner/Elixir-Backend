#!/bin/sh

set -e

echo "⏳ Waiting for MySQL at $DB_HOST:$DB_PORT..."

while ! mysqladmin ping -h"$DB_HOST" -P"$DB_PORT" --silent; do
  sleep 2
done

echo "✅ MySQL is ready. Starting FastAPI backend..."
exec "$@"
