# CLAUDE.md — 마씨(Merci) 프로젝트 가이드

## 프로젝트 개요
치매 환자의 회상 활동을 돕는 가족 중심 디지털 앨범 서비스.  
PRD 전체 내용은 `docs/prd.md` 를 참고한다.

---

## 기술 스택

| 항목 | 선택 |
|------|------|
| 언어 | Python 3.11+ |
| 프레임워크 | FastAPI |
| ORM | SQLAlchemy 2.0 (async) |
| DB | PostgreSQL |
| 인증 | OAuth 2.0 (카카오 / 네이버) + JWT |
| 파일 스토리지 | AWS S3 (or Supabase Storage) |
| 유효성 검증 | Pydantic v2 |
| 마이그레이션 | Alembic |
| 환경변수 | python-dotenv (.env) |

---

## 폴더 구조

```
app/
├── main.py                  # FastAPI 앱 진입점
├── core/
│   ├── config.py            # 환경변수 설정
│   ├── database.py          # DB 엔진 / 세션
│   ├── dependencies.py      # 공통 의존성 (현재 유저 추출 등)
│   └── security.py          # JWT 생성 / 검증
├── auth/
│   ├── router.py            # (NestJS controller)
│   ├── service.py           # (NestJS service)
│   └── schema.py            # (NestJS DTO)
├── group/
│   ├── router.py
│   ├── service.py
│   └── schema.py
├── memory/
│   ├── router.py
│   ├── service.py
│   └── schema.py
├── recall/
│   ├── router.py
│   ├── service.py
│   └── schema.py
└── models.py                # SQLAlchemy 테이블 전체 정의
docs/
└── prd.md                   # 기획 문서
.env
.env.example
alembic/
requirements.txt
```

---

## 코딩 컨벤션

### 네이밍
- 파일명: `snake_case`
- 클래스명: `PascalCase`
- 함수/변수: `snake_case`
- 상수: `UPPER_SNAKE_CASE`

### 레이어 규칙
- **router.py**: 엔드포인트 정의만. 비즈니스 로직 금지.
- **service.py**: 비즈니스 로직 전담. DB 직접 접근 금지 (repository 패턴 적용 시).
- **schema.py**: Request / Response Pydantic 모델 정의.
- **models.py**: SQLAlchemy ORM 모델만. 비즈니스 로직 없음.

### 비동기
- DB 접근은 항상 `async / await` 사용
- SQLAlchemy `AsyncSession` 사용

### 에러 처리
- HTTPException 사용
- 공통 에러 메시지는 `core/exceptions.py` 에 정의

---

## 인증 구조

```
카카오/네이버 OAuth → access_token 획득
→ 유저 정보 조회 (provider_user_id)
→ DB에 없으면 자동 회원가입
→ 서비스 자체 JWT 발급 (access_token)
→ 이후 요청: Authorization: Bearer {token}
```

현재 유저는 `dependencies.py` 의 `get_current_user` 의존성으로 추출.

---

## 역할(Role) 정책

- `OWNER`: 그룹 생성자. 초대 코드 조회 가능.
- `MEMBER`: 초대 코드로 참여. 콘텐츠 등록/조회 가능.
- MVP에서 한 유저는 1개 그룹만 소속 가능.

---

## 환경변수 목록 (.env.example)

```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/merci
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

KAKAO_CLIENT_ID=
KAKAO_REDIRECT_URI=

NAVER_CLIENT_ID=
NAVER_CLIENT_SECRET=
NAVER_REDIRECT_URI=

AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_S3_BUCKET_NAME=
AWS_REGION=ap-northeast-2
```

---

## API 엔드포인트 구조 (예정)

```
POST   /auth/kakao/callback
POST   /auth/naver/callback
POST   /auth/logout

PATCH  /users/me/nickname

POST   /groups
POST   /groups/join
GET    /groups/me/invite-code

POST   /memories
GET    /memories
GET    /memories/{memory_id}

POST   /memories/{memory_id}/recalls
```

---

## 권한 정책

- Memory 수정/삭제: `created_by == current_user.id` 인 경우만 허용
- Comment 수정/삭제: `user_id == current_user.id` 인 경우만 허용

---

## 작업 시 참고사항

- 새 기능 구현 전 반드시 `docs/prd.md` 의 해당 기능 정의 확인
- 마씨 배지는 RecallLog.result == "기억하심" 일 때만 생성
- 치료/평가 기능은 MVP 범위 밖 — 구현하지 않음
