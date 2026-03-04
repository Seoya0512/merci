# Merci 프로젝트 메모리

## 프로젝트 개요
치매 환자 회상 앨범 서비스. FastAPI + SQLAlchemy 2.0 (async) + PostgreSQL + Redis + Cloudflare R2.

## 폴더 구조
- `app/auth/` - 카카오/네이버 OAuth, JWT
- `app/group/` - 그룹 생성/참여/초대코드
- `app/memory/` - 추억 CRUD
- `app/recall/` - 회상 결과 기록
- `app/comment/` - 댓글 CRUD
- `app/upload/` - Presigned URL 발급
- `app/users/` - 유저 정보 수정
- `app/core/` - 공통 유틸 (config, dependencies, security, storage, utils, responses)
- `app/models.py` - SQLAlchemy 모델 전체

## 핵심 패턴
- 트랜잭션: `get_db`가 자동 commit/rollback. service에서 `commit()` 직접 호출 금지.
- 인증: `get_current_user` 의존성으로 현재 유저 추출 (`app.core.dependencies`)
- 그룹 권한: `get_membership_or_403(db, user_id)` → `app.core.utils`
- 에러 응답 문서화: `app.core.responses` → `AUTH_RESPONSES`, `BAD_REQUEST`, `NOT_FOUND`, `CONFLICT`
- 파일 스토리지: Cloudflare R2 (S3 호환), `app.core.storage`
- `get_db` import: 항상 `from app.core.dependencies import get_db` 사용

## 파일 업로드 흐름
1. `POST /uploads/presigned-url` → `upload_url` + `object_key` (temp/images/uuid.jpg) 반환
2. 클라이언트가 PUT으로 R2에 직접 업로드
3. `POST /memories` 시 `image_key` 전달 → 서버가 temp/ → images/{group_id}/ 이동

## R2 key 구조
- 임시: `temp/images/{uuid}.ext` / `temp/voices/{uuid}.ext`
- 영구: `images/{group_id}/{uuid}.ext` / `voices/{group_id}/{uuid}.ext`

## 구현 완료 상태 (2026-03-04)
- auth, group, memory, recall, comment, upload, users 모듈 모두 구현 완료
- responses.py 모든 라우터에 적용 완료
- `app/core/utils.py` - `get_membership_or_403` 공통 유틸 생성
- memory/service.py가 `MemoryResponse`를 직접 반환 (router에서 변환 없음)
- memory/router.py에 `MemoryResponse` import 필요 (response_model로 사용)

## 환경변수 (Cloudflare R2)
```
CF_ACCOUNT_ID=
CF_R2_ACCESS_KEY_ID=
CF_R2_SECRET_ACCESS_KEY=
CF_R2_BUCKET_NAME=
CF_R2_PUBLIC_URL=  # 공개 버킷 URL (presigned get URL의 base)
```

## 마씨 배지
`RecallLog.result == "기억하심"` (RecallResult.REMEMBERED) 일 때만 has_badge=True.
가장 최근 회상 기록 기준으로 판단 (`max(recall_logs, key=lambda l: l.visited_at)`).
