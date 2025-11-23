#!/bin/bash

echo "=========================================="
echo "Mock Upload 테스트"
echo "=========================================="

# 서버 시작
cd /home/ec2-user/flex/server
source /home/ec2-user/flex/venv1/bin/activate

# 기존 서버 종료
pkill -9 -f "uvicorn main:app"
sleep 2

# 서버 시작 (백그라운드)
python -m uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/test_server.log 2>&1 &
SERVER_PID=$!
echo "서버 시작됨 (PID: $SERVER_PID)"

# 서버 시작 대기
sleep 6

# Health check
echo -e "\n[1] Health Check..."
curl -s http://localhost:8000/health

# Upload 테스트
echo -e "\n\n[2] Upload 테스트..."
curl -X POST http://localhost:8000/api/v1/jd-persona/upload \
  -F pdf_file=@docs/jd.pdf \
  -F company_id=1 \
  -F title="삼성물산 패션부문 채용" \
  -s | python -m json.tool | head -50

echo -e "\n\n=========================================="
echo "✅ 테스트 완료"
echo "=========================================="
echo "서버는 계속 실행 중입니다 (PID: $SERVER_PID)"
echo "종료하려면: kill $SERVER_PID"
