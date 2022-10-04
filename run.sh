#!/bin/sh
PORT=6969

gunicorn --bind 0.0.0.0:$PORT app:app
echo "Shutting down Gunicorn Server"