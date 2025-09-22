# FastAPI + PostgreSQL 환경 설정 순서

아래 단계들을 순서대로 진행하면 로컬 개발 환경을 구축하고 `product_order` CRUD API까지 실행할 수 있습니다.

## 1단계. 개발 환경 초기화
1. Python 3.11 이상과 Docker Desktop(또는 Docker Engine)이 설치되어 있다고 가정합니다.
2. 프로젝트 루트(`/Users/yanadoo/experience/fast-ai/fast-ai`)에서 가상환경을 만들고 활성화합니다.
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```
3. 의존성을 설치합니다.
   ```bash
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```
   `requirements.txt`에는 FastAPI, SQLAlchemy, PostgreSQL 드라이버, Pydantic 관련 패키지가 포함되어 있습니다.

## 2단계. 환경 변수 구성
1. `.env` 파일에 데이터베이스 연결 문자열을 선언합니다.
   ```env
   DATABASE_URL=postgresql://postgres:1234@localhost:5432/postgres
   ```
2. `app/core/config.py`는 `pydantic-settings`의 `BaseSettings`를 사용해 `.env`를 자동으로 로드합니다.
   ```python
   from pydantic import Field
   from pydantic_settings import BaseSettings


   class Settings(BaseSettings):
       database_url: str = Field(
           "postgresql://postgres:1234@localhost:5432/postgres", env="DATABASE_URL"
       )

       class Config:
           env_file = ".env"
           env_file_encoding = "utf-8"


   settings = Settings()
   ```

## 3단계. PostgreSQL 실행
1. `docker-compose.yml`에는 Postgres 15 컨테이너가 정의되어 있습니다.
   ```yaml
   services:
     postgres:
       image: postgres:15
       container_name: fastai-postgres
       ports:
         - "5432:5432"
       environment:
         POSTGRES_USER: postgres
         POSTGRES_PASSWORD: 1234
         POSTGRES_DB: postgres
       volumes:
         - postgres-data:/var/lib/postgresql/data
       restart: unless-stopped
   ```
2. Docker daemon이 실행 중인지 확인한 뒤 컨테이너를 시작합니다.
   ```bash
   docker compose up -d postgres
   docker compose ps
   docker logs -f fastai-postgres  # 초기화 확인용
   ```
3. 중지할 때는 `docker compose stop postgres` 또는 `docker compose down`을 사용합니다.

## 4단계. 애플리케이션 구조 이해
```
fast-ai/
├── app/
│   ├── api/               # 라우터, 의존성 선언
│   ├── core/              # 설정 로직 (Settings)
│   ├── db/                # SQLAlchemy Base, 세션
│   ├── main.py            # FastAPI 앱 초기화 및 라우터 등록
│   ├── models/            # SQLAlchemy 모델
│   ├── schemas/           # Pydantic 스키마 (from_attributes 사용)
│   └── services/          # 비즈니스 로직 계층
├── docker-compose.yml
├── main.py                # uvicorn 진입점
├── requirements.txt
└── .env
```
- `app/main.py`는 Lifespan 컨텍스트에서 `Base.metadata.create_all(bind=engine)`을 호출해 개발 환경에서 초기 테이블을 생성합니다.
- `app/api/dependencies.py`의 `get_db` 의존성이 요청마다 SQLAlchemy 세션을 제공합니다.

## 5단계. product_order CRUD 구성요소
1. **모델** (`app/models/product_order.py`)
   ```python
   class ProductOrder(Base):
       __tablename__ = "product_order"
       id = Column(Integer, primary_key=True, index=True)
       order_number = Column(String(64), unique=True, nullable=False, index=True)
       product_name = Column(String(255), nullable=False)
       shipping_address = Column(String(255), nullable=False)
       shipping_status = Column(String(50), nullable=False, default="pending")
   ```
2. **스키마** (`app/schemas/product_order.py`)는 `ConfigDict(from_attributes=True)`로 ORM 객체를 응답 모델로 변환합니다.
3. **서비스** (`app/services/product_order.py`)가 생성/조회/수정/삭제 로직을 캡슐화합니다.
4. **라우터** (`app/api/routers/product_orders.py`)는 `/product-orders` 경로에 CRUD API를 제공합니다.

## 6단계. 애플리케이션 실행 및 확인
1. 가상환경이 활성화되어 있는지 확인합니다 (`source .venv/bin/activate`).
2. PostgreSQL 컨테이너가 실행 중인지 확인합니다 (`docker compose ps`).
3. FastAPI 서버를 실행합니다.
   ```bash
   uvicorn main:app --reload
   ```
4. 브라우저에서 `http://127.0.0.1:8000/docs`를 열어 OpenAPI 문서와 CRUD 엔드포인트를 테스트합니다.
