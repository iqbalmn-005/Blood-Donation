echo "Building the project..."
python3 -m pip install -r requirements.txt
python3 manage.py collectstatic --noinput --clear

if [ -n "$DATABASE_URL" ]; then
    echo "Running database migrations..."
    python3 manage.py migrate --noinput
else
    echo "Skipping build-time migration (DATABASE_URL is not set)."
fi

echo "Build complete."
