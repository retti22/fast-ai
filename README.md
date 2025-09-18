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
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
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
├── README.md
├── requirements.txt
├── .env
├── .gitignore
├── main.py                 # FastAPI 애플리케이션 진입점
├── app/
│   ├── __init__.py
│   ├── config.py           # 설정 파일
│   ├── models/             # Pydantic 모델
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── services/           # 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── openai_service.py
│   │   └── redis_service.py
│   └── routers/            # API 라우터
│       ├── __init__.py
│       └── api.py
└── tests/                  # 테스트 파일
    ├── __init__.py
    └── test_api.py
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

1. **API 키 보안**

   - `.env` 파일을 `.gitignore`에 추가
   - 환경 변수로 API 키 관리
   - 프로덕션에서는 시크릿 관리 서비스 사용

2. **CORS 설정**

   ```python
   from fastapi.middleware.cors import CORSMiddleware

   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

3. **Rate Limiting**

   ```python
   from slowapi import Limiter, _rate_limit_exceeded_handler
   from slowapi.util import get_remote_address
   from slowapi.errors import RateLimitExceeded

   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
   ```

## 📚 추가 리소스

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [OpenAI API 문서](https://platform.openai.com/docs)
- [Redis 공식 문서](https://redis.io/docs/)
- [Uvicorn 문서](https://www.uvicorn.org/)

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.
