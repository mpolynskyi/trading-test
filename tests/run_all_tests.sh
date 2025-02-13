#!/bin/sh

# Run API tests in parallel first
pytest -m api -n 5 --html=reports/api_test_report.html --self-contained-html --url http://server:8000

# Then run WebSocket tests sequentially
pytest -m websockets --html=reports/websockets_test_report.html --self-contained-html --url http://server:8000
