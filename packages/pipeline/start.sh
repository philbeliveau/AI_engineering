#!/bin/bash
# Start Streamlit, FastAPI, and nginx reverse proxy
# nginx on PORT (external), routes to internal services:
#   /api/*  -> FastAPI (port 8000)
#   /health -> FastAPI (port 8000)
#   /*      -> Streamlit (port 8501)

set -e

echo "Starting Knowledge Pipeline services..."
echo "PORT=${PORT:-8501}"

# Substitute only $PORT in nginx config (preserve nginx variables like $host)
export PORT=${PORT:-8501}
envsubst '$PORT' < /app/nginx.conf > /tmp/nginx.conf

# Start FastAPI on port 8000 (internal only)
echo "Starting FastAPI on port 8000..."
uvicorn api:app --host 127.0.0.1 --port 8000 &
API_PID=$!

# Start Streamlit on port 8501 (internal only)
echo "Starting Streamlit on port 8501..."
streamlit run web_app.py --server.port 8501 --server.address 127.0.0.1 --server.headless true &
STREAMLIT_PID=$!

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 5

# Verify services are running
if ! kill -0 $API_PID 2>/dev/null; then
    echo "ERROR: FastAPI failed to start"
    exit 1
fi
if ! kill -0 $STREAMLIT_PID 2>/dev/null; then
    echo "ERROR: Streamlit failed to start"
    exit 1
fi

echo "Starting nginx reverse proxy on port ${PORT}..."
# Start nginx on Railway PORT (foreground, keeps container running)
nginx -c /tmp/nginx.conf -g 'daemon off;'
