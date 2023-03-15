#!/bin/bash

while ! nc -z db 5432; do
  sleep 1
done

# Run database migrations
python manage.py migrate

# Create a superuser (if not already present)
cat <<EOF | python manage.py shell
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='root').exists():
    User.objects.create_superuser('root', '', 'root')
EOF

# Start the Django development server
exec "$@"
