# FastAPI + OpenAI API 백엔드 서버

FastAPI를 사용하여 OpenAI API를 호출하는 백엔드 API 서버입니다.

## 📋 목차

- [설치 및 설정](#설치-및-설정)
- [환경 변수 설정](#환경-변수-설정)
- [프로젝트 구조](#프로젝트-구조)
- [실행 방법](#실행-방법)
- [API 엔드포인트](#api-엔드포인트)
- [개발 가이드](#개발-가이드)

## 🚀 설치 및 설정

### 1. Python 환경 설정

```bash
# Python 3.8+ 버전 확인
python --version

# 가상환경 생성 (권장)
python -m venv .venv

# 가상환경 활성화
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 2. 의존성 설치

```bash
# requirements.txt 파일 생성 후 설치
pip install fastapi uvicorn openai python-dotenv redis

# 또는 직접 설치
pip install fastapi==0.104.1
pip install uvicorn[standard]==0.24.0
pip install openai==1.3.0
pip install python-dotenv==1.0.0
pip install redis==5.0.1
```

### 3. requirements.txt 파일 생성

프로젝트 루트에 `requirements.txt` 파일을 생성하고 다음 내용을 추가:

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
openai==1.3.0
python-dotenv==1.0.0
redis==5.0.1
pydantic==2.5.0
```

## 🔧 환경 변수 설정

### 1. .env 파일 생성

프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 추가:

```env
# OpenAI API 설정
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_ORG_ID=your_organization_id_here

# Redis 설정
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=your_redis_password

# 서버 설정
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

### 2. 환경 변수 로드

Python 코드에서 환경 변수를 로드하려면:

```python
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REDIS_URL = os.getenv("REDIS_URL")
```

## 📁 프로젝트 구조

```
fast-ai/
├── app/
│   ├── api/               # 라우터 (product_orders, customers 등)
│   ├── core/              # 환경 설정 및 공통 설정
│   ├── db/                # SQLAlchemy Base, SessionLocal
│   ├── main.py            # FastAPI 앱 초기화 및 lifespan 훅
│   ├── models/            # SQLAlchemy ORM 모델
│   ├── schemas/           # Pydantic 요청/응답 모델
│   └── services/          # 비즈니스 로직 및 DB 조작 함수
├── docker-compose.yml     # Postgres 컨테이너 정의
├── main.py                # uvicorn 진입점 (app.main.app re-export)
├── requirements.txt
└── README.md
```

## 🏃‍♂️ 실행 방법

### 1. 개발 서버 실행

```bash
# 기본 실행
uvicorn main:app --reload

# 특정 호스트와 포트로 실행
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 환경 변수와 함께 실행
uvicorn main:app --reload --env-file .env
```

### 2. 프로덕션 서버 실행

```bash
# Gunicorn 사용 (Linux/macOS)
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

# Docker 사용
docker build -t fast-ai-api .
docker run -p 8000:8000 --env-file .env fast-ai-api
```

## 🔌 API 엔드포인트

### 기본 엔드포인트

- `GET /` - 서버 상태 확인
- `GET /docs` - Swagger UI 문서
- `GET /redoc` - ReDoc 문서

### OpenAI API 엔드포인트

- `POST /api/chat` - 채팅 완성 요청
- `POST /api/completion` - 텍스트 완성 요청
- `POST /api/embedding` - 텍스트 임베딩 생성

## 🛠️ 개발 가이드

### 1. 코드 스타일

- PEP 8 스타일 가이드 준수
- Type hints 사용
- Docstring 작성

### 2. 에러 처리

```python
from fastapi import HTTPException

try:
    result = openai_service.generate_text(prompt)
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
```

### 3. 로깅 설정

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

### 4. 테스트 실행

```bash
# pytest 설치
pip install pytest pytest-asyncio httpx

# 테스트 실행
pytest tests/
```

## 🔒 보안 고려사항

- API 키와 비밀번호 등은 환경 변수로 관리하고 코드에 직접 작성하지 않습니다.
- HTTPS 환경에서 API를 제공하도록 설정합니다.
- 요청 검증 및 rate limiting을 통해 abuse를 방지합니다.
