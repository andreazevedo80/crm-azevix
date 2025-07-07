#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Run the database initialization function from app.py
echo "Running database migrations..."
python -c 'from app import create_tables; create_tables()'

# Now, execute the main command (start Gunicorn)
# "exec" replaces the shell process with the Gunicorn process.
exec gunicorn --bind 0.0.0.0:5090 --workers 4 app:app