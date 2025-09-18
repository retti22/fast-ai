# 가상환경 생성
python -m venv .venv
source .venv/bin/activate

# FastAPI와 ASGI 서버인 Uvicorn을 설치
pip install fastapi uvicorn

# 다음 명령어로 서버 실행
uvicorn main:app --reload
http://localhost:8000

# Swagger 기반의 자동 문서
http://localhost:8000/docs