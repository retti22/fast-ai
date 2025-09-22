# FastAPI + PostgreSQL CRUD 서버

FastAPI와 SQLAlchemy를 사용해 PostgreSQL과 연동하는 기본 CRUD 백엔드입니다. `product_order`와 `customer` 리소스를 예시로 포함하고 있으며, Docker Compose로 손쉽게 로컬 개발 환경을 구성할 수 있습니다.

## 📋 목차

- [설치 및 설정](#설치-및-설정)
- [환경 변수](#환경-변수)
- [PostgreSQL 실행](#postgresql-실행)
- [프로젝트 구조](#프로젝트-구조)
- [실행 방법](#실행-방법)
- [API 엔드포인트](#api-엔드포인트)
- [개발 가이드](#개발-가이드)

## 설치 및 설정

### 1. Python 환경 준비

```bash
python --version            # Python 3.11 이상 권장
python -m venv .venv        # 가상환경 생성
source .venv/bin/activate   # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

`requirements.txt`에는 FastAPI, SQLAlchemy, Pydantic, PostgreSQL 드라이버 등의 기본 의존성이 정의되어 있습니다.

## 환경 변수

루트에 `.env` 파일을 만들고 데이터베이스 연결 문자열을 정의합니다. 값이 없으면 `app/core/config.py`의 기본값이 사용됩니다.

```env
DATABASE_URL=postgresql://postgres:1234@localhost:5432/postgres
```

`Settings` 클래스가 `.env`를 읽어 `settings.database_url`을 제공하며, `app/db/session.py`에서 SQLAlchemy `engine` 생성 시 사용합니다.

## PostgreSQL 실행

`docker-compose.yml`에는 Postgres 15 컨테이너가 정의되어 있습니다.

```bash
docker compose up -d postgres
docker compose ps            # 상태 확인
docker logs -f fastai-postgres  # 초기화 로그 확인 (선택)
```

중단 시에는 `docker compose stop postgres` 또는 `docker compose down`을 사용합니다.

## 프로젝트 구조

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
├── README-origin.md       # 이전 README 보관본
└── README.md              # 현재 문서
```

`app/main.py`의 lifespan 훅은 앱 기동 시 `Base.metadata.create_all(bind=engine)`을 호출해 개발 환경에서 필요한 테이블을 자동 생성합니다. `app/api/routers/__init__.py`는 라우터를 리스트로 묶어 `main.py`에서 순회하며 등록합니다.

## 실행 방법

```bash
uvicorn main:app --reload
```

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## API 엔드포인트

주요 엔드포인트는 FastAPI 문서(`/docs`, `/redoc`)에서 확인할 수 있습니다. 기본적으로 `/` 헬스체크와 `/product-orders`, `/customers` CRUD 경로가 제공됩니다.

## 개발 가이드

- `.env`, `.venv`, `__pycache__` 등 임시 파일은 `.gitignore`에 포함되어 있으니 그대로 두면 됩니다.
- 현재는 `Base.metadata.create_all`로 스키마를 초기화하지만, 운영 환경에서는 Alembic 등 마이그레이션 도구 도입을 권장합니다.
- 라우터가 늘어날 경우 `app/api/routers/__init__.py`의 리스트에만 추가하면 됩니다.
- 복잡한 조회가 필요하다면 `app/services/product_order.py`의 Raw SQL 예시(`fetch_complex_class_payload`)처럼 SQLAlchemy의 `text()`를 사용해 구현할 수 있습니다.

---
