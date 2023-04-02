export BUILD="$(cat /app/.build)"

# Update database
alembic upgrade head
