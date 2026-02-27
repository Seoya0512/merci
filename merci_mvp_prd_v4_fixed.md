# 마씨(Merci) - MVP 기획 문서 (Figma 반영 v4)

작성일: 2026-02-27

---

## 1. 서비스 정의

마씨(Merci)는 치매 환자와의 회상 활동을 기록하는 가족 중심 디지털 앨범
서비스이다. 가족은 사진, 이야기, 음성을 등록하고 방문 후 어르신의 반응을
기록한다.

기억을 평가하거나 정답/오답을 구분하지 않으며, 관찰 기반 기록만
저장한다.

---

## 2. 사용자 및 역할

- 1차 사용자: 치매 환자의 가족
- 환자는 앱을 직접 조작하지 않음

역할: - OWNER (그룹 생성자) - MEMBER (초대 코드 참여자)

MVP 기준: 1유저 = 1그룹 소속

---

## 3. IA (정보 구조)

- 랜딩
- 로그인/회원가입(OAuth)
- 온보딩 (그룹 생성 / 코드 참여)
- 그룹 홈 (목록 + 필터)
- 사진 상세
- 사진 등록
- 설정 (관계 설정 / 코드 공유 / 로그아웃)

---

## 4. 핵심 기능 정의

### 4.1 회원가입/로그인

- 네이버/카카오 OAuth
- 최초 로그인 시 자동 가입

### 4.2 그룹 생성

- 어르신 성함 입력
- invite_code 자동 생성
- 생성자 OWNER 지정

### 4.3 초대 코드 참여

- 코드 입력
- 유효성 검사
- MEMBER 등록

### 4.4 사진 등록

입력 항목: - 사진(필수) - 연도 - 장소 - 함께한 인물 - 이야기(필수) -
음성(선택)

- 사진 업로드는 presigned url 을 사용해서 AWS S3에 업로드 예정
- 음성도 마찬가지이며, 모든 자료는 파일 선업로드 방식을 사용해서 완전히 포스팅이 등록된 후에 파일 영구 저장 예정임

스토리지 업로드 후 Memory 생성

### 4.5 사진 목록

- 그룹 단위 조회
- 기간/작성자 필터
- 기억하심 배지 노출

배지 규칙: RecallLog 중 REMEMBERED 존재 시 표시 (누적 수량 표시 안함)

### 4.6 사진 상세

구성: - 이미지 - 음성 플레이어 - 이야기 - 함께한 인물 - 기록 날짜

### 4.7 어르신 반응 기록

질문: "오늘 어르신의 반응은 어떠셨나요?"

옵션: - 기억하심 - 가물가물 - 낯설어하심

※ 틀림 개념 없음

저장: - memory_id - result - recorded_by - visited_at

### 4.8 가족 메모

- 댓글 형태 기록
- 작성자/시간 표시

### 4.9 설정

- 어르신과의 관계 설정
- 초대 코드 복사/카카오 공유
- 로그아웃

---

## 5. 데이터 구조 요약

User - id - provider - provider_user_id - email - name - nickname -
relation_to_elder - created_at

Group - id - elder_name - invite_code - created_by - created_at

Memory - id - group_id - image_url - year - location - people - story -
voice_url - created_by - created_at

RecallLog - id - memory_id - result - recorded_by - visited_at

Comment - id - memory_id - user_id - content - created_at

---

## 6. MVP 포함 범위

포함: - OAuth 로그인 - 그룹 구조 - 사진 + 이야기 + 음성 - 관찰형 반응
기록 - 단일 마씨 배지 시스템 - 가족 메모

제외: - 통계/AI - 추천 알고리즘 - 게임화
