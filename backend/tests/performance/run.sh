#!/bin/sh

# exit immediately if any command fails, and use a trap to kill the server
set -e

export MODE="load_test"
cd ../../
export PYTHONPATH="$(pwd):${PYTHONPATH}"

# function to clean up the background server
cleanup() {
    if [ -n "$SERVER_PID" ] && kill -0 "$SERVER_PID" 2>/dev/null; then
        echo "Stopping server (PID $SERVER_PID)..."
        kill "$SERVER_PID"
        wait "$SERVER_PID" 2>/dev/null
        echo "Server stopped."
    fi
}
trap cleanup EXIT INT TERM

# DB setup
uv run alembic downgrade base
uv run alembic upgrade head
uv run tests/performance/setup.py

# --- start the server in the background ---
echo "Starting server..."
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --loop uvloop --workers 4 &
SERVER_PID=$!
echo "Server started with PID $SERVER_PID"

# give the server a moment to start
sleep 5

# --- Run the load test ---
echo "--- Running k6 ---"
ulimit -n 65535
# open http://localhost:5665 in the browser and reload the page when the test started to view real time stats
# K6_WEB_DASHBOARD=true k6 run -q --summary-export=tests/performance/k6_booking_journey_test.json tests/performance/k6_booking_journey_test.js
K6_WEB_DASHBOARD=true k6 run -q --summary-export=tests/performance/k6_booking_stress_test.json tests/performance/k6_booking_stress_test.js

# --- cleanup ---
uv run tests/performance/teardown.py
# The trap will kill the server automatically when the script exits
# (including right now, if you want an explicit teardown later)
