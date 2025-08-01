#!/bin/bash
echo "🚀 서버 실행 중..."
export FLASK_APP=api/server.py
flask run --host=0.0.0.0 --port=5000
