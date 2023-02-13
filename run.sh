#!/bin/sh
PORT=6969

gunicorn --bind 0.0.0.0:$PORT --timeout 120 app:app
echo "Shutting down Gunicorn Server"