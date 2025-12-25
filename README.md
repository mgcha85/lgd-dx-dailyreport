# 일보 자동 분류 시스템

LLM을 활용한 제조 현장 일보 자동 분류 시스템입니다. 엑셀 파일의 Issue 컬럼을 분석하여 불량명, 설비명, 조치내용을 자동으로 추출합니다.

## 📋 프로젝트 개요

이 시스템은 제조 현장의 일일 보고서(일보)를 LLM(Large Language Model)을 통해 자동으로 분류하고, 웹 인터페이스를 통해 결과를 확인할 수 있는 통합 솔루션입니다.

### 주요 기능

- **파일 업로드**: 엑셀(.xlsx, .xls) 또는 PowerPoint(.pptx) 파일 업로드
- **자동 분류**: OpenAI API를 사용한 LLM 기반 자동 분류
  - 불량명 추출
  - 설비명 추출
  - 조치내용 추출
- **재시도 로직**: JSON 파싱 실패 시 최대 3회 자동 재시도
- **이력 관리**: 모든 분류 작업의 이력 저장 및 조회
- **결과 다운로드**: 분류 완료된 엑셀 파일 다운로드
- **설정 관리**: OpenAI API 설정, Few-shot 예제 관리

## 🏗️ 아키텍처

```
┌─────────────┐
│   Nginx     │ ← Reverse Proxy (Port 80)
└──────┬──────┘
       │
       ├─────────────────┐
       │                 │
  ┌────▼────┐      ┌────▼────┐
  │Frontend │      │ Backend │
  │ (Svelte)│      │(FastAPI)│
  │  Port:80│      │ Port:8000│
  └─────────┘      └────┬────┘
                        │
                   ┌────▼────┐
                   │ SQLite  │
                   │   DB    │
                   └─────────┘
```

## 🛠️ 기술 스택

### Frontend
- **프레임워크**: Svelte 4.2.8
- **빌드 도구**: Vite 5.0.11
- **HTTP 클라이언트**: Axios 1.6.5
- **컨테이너화**: Docker (nginx 기반)

### Backend
- **프레임워크**: FastAPI 0.109.0
- **웹 서버**: Uvicorn 0.27.0
- **데이터베이스**: SQLite (SQLAlchemy 2.0.25)
- **데이터 처리**: Polars 0.20.3 (Excel 처리)
- **LLM API**: OpenAI 1.10.0
- **테스트**: Pytest 7.4.4

### Infrastructure
- **리버스 프록시**: Nginx (Alpine)
- **컨테이너 오케스트레이션**: Docker Compose
- **환경 변수 관리**: .env 파일

## 📂 소스 트리

```
lgd-dx-dailyreport/
├── docker-compose.yml          # Docker Compose 설정
├── .env.example                # 환경 변수 템플릿
├── .gitignore                  # Git 제외 파일 목록
├── README.md                   # 프로젝트 문서 (본 파일)
│
├── nginx/                      # Nginx 리버스 프록시
│   ├── Dockerfile
│   └── nginx.conf              # Nginx 설정
│
├── backend/                    # FastAPI 백엔드
│   ├── Dockerfile
│   ├── requirements.txt        # Python 의존성
│   ├── pytest.ini              # Pytest 설정
│   ├── app/
│   │   ├── main.py             # FastAPI 앱 초기화
│   │   ├── config.py           # 환경 설정
│   │   ├── database.py         # DB 연결 및 세션 관리
│   │   ├── models.py           # SQLAlchemy 모델
│   │   ├── schemas.py          # Pydantic 스키마
│   │   ├── api/                # API 라우터
│   │   │   ├── upload.py       # 파일 업로드 API
│   │   │   ├── classification.py  # 분류 실행 API
│   │   │   ├── history.py      # 이력 조회 API
│   │   │   └── settings.py     # 설정 관리 API
│   │   └── services/           # 비즈니스 로직
│   │       ├── file_processor.py  # 파일 처리
│   │       ├── excel_handler.py   # Excel 읽기/쓰기
│   │       └── llm_classifier.py  # LLM 분류 서비스
│   ├── tests/                  # 유닛 테스트
│   │   ├── conftest.py         # Pytest Fixtures
│   │   ├── test_api.py         # API 테스트
│   │   └── test_services.py    # 서비스 테스트
│   ├── scripts/                # 유틸리티 스크립트
│   │   ├── create_mock_data.py # Mock 데이터 생성
│   │   └── clear_test_data.py  # 테스트 데이터 정리
│   └── data/                   # 데이터 저장소
│       ├── app.db              # SQLite 데이터베이스
│       ├── uploads/            # 업로드 파일
│       └── results/            # 분류 결과 파일
│
└── frontend/                   # Svelte 프론트엔드
    ├── Dockerfile
    ├── package.json            # Node.js 의존성
    ├── vite.config.js          # Vite 설정
    ├── svelte.config.js        # Svelte 설정
    ├── nginx.conf              # 프론트엔드용 Nginx 설정
    ├── index.html              # HTML 엔트리 포인트
    └── src/
        ├── main.js             # 앱 초기화
        ├── App.svelte          # 메인 컴포넌트
        ├── lib/
        │   ├── api.js          # Backend API 호출
        │   └── stores.js       # Svelte 상태 관리
        └── routes/             # 페이지 컴포넌트
            ├── Upload.svelte   # 파일 업로드 화면
            ├── Result.svelte   # 분류 결과 화면
            ├── History.svelte  # 이력 조회 화면
            └── Settings.svelte # 설정 화면
```

## 🚀 설치 및 실행

### 사전 요구사항

- Docker
- Docker Compose
- OpenAI API Key (또는 호환 가능한 LLM API)

### 1. 환경 설정

```bash
# 레포지토리 클론 (이미 있다면 생략)
cd lgd-dx-dailyreport

# 환경 변수 파일 생성
cp .env.example .env

# .env 파일 편집 (필요시)
nano .env
```

`.env` 파일에서 필요한 설정을 수정할 수 있습니다. 기본값으로도 작동하지만, OpenAI API 키는 웹 인터페이스에서 설정해야 합니다.

### 2. Docker Compose로 실행

```bash
# 모든 서비스 빌드 및 시작
docker compose up -d --build

# 로그 확인
docker compose logs -f

# 서비스 상태 확인
docker compose ps
```

### 3. 접속

브라우저에서 `http://localhost`로 접속합니다.

### 4. 종료

```bash
# 서비스 중지
docker compose down

# 볼륨까지 모두 삭제 (DB 포함)
docker compose down -v
```

## 🧪 Backend 유닛 테스트

### 테스트 실행

```bash
# Backend 컨테이너에서 pytest 실행
docker compose exec backend pytest -v

# 특정 테스트 파일만 실행
docker compose exec backend pytest tests/test_api.py -v

# Coverage 리포트와 함께 실행
docker compose exec backend pytest --cov=app --cov-report=html
```

### 테스트 구성

- **test_api.py**: API 엔드포인트 테스트
  - 파일 업로드
  - 설정 CRUD
  - 이력 조회
- **test_services.py**: 서비스 로직 테스트
  - Excel 처리
  - 파일 검증

## 📡 API 문서

Backend가 실행 중일 때 다음 URL에서 대화형 API 문서를 확인할 수 있습니다:

- Swagger UI: `http://localhost/api/docs`
- ReDoc: `http://localhost/api/redoc`

### API 엔드포인트

#### 1. 파일 업로드

```bash
curl -X POST http://localhost/api/upload \
  -F "file=@/path/to/your/file.xlsx"
```

**응답 예시:**
```json
{
  "filename": "일보_DPU_20250101.xlsx",
  "file_path": "/app/data/uploads/일보_DPU_20250101_20250125_174800.xlsx",
  "message": "파일이 성공적으로 업로드되었습니다."
}
```

#### 2. 설정 조회

```bash
curl -X GET http://localhost/api/settings
```

**응답 예시:**
```json
{
  "id": 1,
  "openai_api_key": "sk-...",
  "openai_base_url": "https://api.openai.com/v1",
  "model_name": "gpt-4o-mini",
  "sheet_name": "일보_DPU",
  "column_name": "Issue",
  "few_shot_examples": "...",
  "updated_at": "2025-01-25T08:30:00"
}
```

#### 3. 설정 업데이트

```bash
curl -X PUT http://localhost/api/settings \
  -H "Content-Type: application/json" \
  -d '{
    "openai_api_key": "sk-your-api-key-here",
    "openai_base_url": "https://api.openai.com/v1",
    "model_name": "gpt-4o-mini",
    "sheet_name": "일보_DPU",
    "column_name": "Issue",
    "few_shot_examples": "예제 1:\nIssue: \"DPU 불량, LINE-A, 재작업\"\n결과: {\"불량명\": \"DPU 불량\", \"설비명\": \"LINE-A\", \"조치내용\": \"재작업\"}"
  }'
```

#### 4. 분류 실행

```bash
curl -X POST http://localhost/api/classify \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/app/data/uploads/일보_DPU_20250101_20250125_174800.xlsx",
    "sheet_name": "일보_DPU",
    "column_name": "Issue",
    "prompt": "다음 Issue 내용을 분석하여 불량명, 설비명, 조치내용을 JSON 형식으로 추출해주세요."
  }'
```

**응답 예시:**
```json
{
  "history_id": 1,
  "filename": "일보_DPU_20250101.xlsx",
  "status": "completed",
  "total_rows": 10,
  "processed_rows": 8,
  "failed_rows": 2,
  "result_path": "/app/data/results/classified_일보_DPU_20250101_20250125_175200.xlsx",
  "message": "분류가 완료되었습니다. (성공: 8, 실패: 2)"
}
```

#### 5. 이력 조회

```bash
# 전체 이력 조회
curl -X GET http://localhost/api/history

# 특정 이력 조회
curl -X GET http://localhost/api/history/1
```

**응답 예시:**
```json
[
  {
    "id": 1,
    "filename": "일보_DPU_20250101.xlsx",
    "sheet_name": "일보_DPU",
    "column_name": "Issue",
    "status": "completed",
    "total_rows": 10,
    "processed_rows": 8,
    "failed_rows": 2,
    "created_at": "2025-01-25T08:52:00",
    "completed_at": "2025-01-25T08:53:30",
    "error_message": null
  }
]
```

#### 6. 결과 파일 다운로드

```bash
curl -X GET http://localhost/api/classify/1/download \
  --output classified_result.xlsx
```

## 💻 Frontend 사용 가이드

### 1. 설정 화면 (⚙️ Settings)

첫 사용 시 반드시 설정을 완료해야 합니다.

1. **OpenAI API 설정**
   - API Key 입력 (필수)
   - Base URL (기본값 사용 가능)
   - Model Name (기본값: gpt-4o-mini)

2. **데이터 설정**
   - Sheet Name (기본값: 일보_DPU)
   - Column Name (기본값: Issue)

3. **Few-Shot Examples** (선택사항)
   - 분류 성능 향상을 위한 예제 입력

### 2. 파일 업로드 화면 (📤 Upload)

1. 엑셀 파일을 드래그 앤 드롭하거나 클릭하여 선택
2. 필요시 시트명, 컬럼명, 프롬프트 수정
3. "업로드 및 분류 시작" 버튼 클릭
4. 분류 완료 후 자동으로 결과 화면으로 이동

### 3. 분류 결과 화면 (📋 Result)

- 분류 상태 확인 (완료/진행중/실패)
- 전체 행 수, 성공 건수, 실패 건수 통계
- 결과 파일 다운로드 버튼

### 4. 이력 조회 화면 (📑 History)

- 모든 분류 작업의 이력 테이블
- 각 이력의 "결과 보기" 버튼으로 상세 결과 확인

## 🔍 코드 개념 설명

### Backend 주요 개념

#### 1. Polars를 사용한 Excel 처리

Pandas 대신 Polars를 사용하여 더 빠른 성능과 메모리 효율성을 제공합니다.

```python
# excel_handler.py
df = pl.read_excel(file_path, sheet_name=sheet_name)
df = df.with_columns([
    pl.Series("불량명", 불량명_list),
    pl.Series("설비명", 설비명_list),
    pl.Series("조치내용", 조치내용_list)
])
df.write_excel(file_path, worksheet=sheet_name)
```

#### 2. LLM 분류 및 재시도 로직

JSON 파싱 실패 시 최대 3회까지 자동으로 재시도합니다.

```python
# llm_classifier.py
for attempt in range(max_retries):
    try:
        response = self.client.chat.completions.create(...)
        result = json.loads(content)
        if self._validate_result(result):
            return result, True
    except json.JSONDecodeError:
        continue
```

#### 3. 빈 값 Skip 로직

Issue 컬럼이 비어있으면 분류를 건너뜁니다.

```python
# classification.py
if excel_handler.is_empty_value(issue_value):
    classifications.append({"불량명": "", "설비명": "", "조치내용": ""})
    continue
```

#### 4. Few-Shot Learning 지원

시스템 프롬프트에 사용자가 제공한 예제를 포함시켜 분류 정확도를 향상시킵니다.

```python
# llm_classifier.py
def _build_system_prompt(self, few_shot_examples):
    base_prompt = """..."""
    if few_shot_examples:
        base_prompt += f"\n\n### 예제:\n{few_shot_examples}"
    return base_prompt
```

### Frontend 주요 개념

#### 1. Svelte Stores를 통한 상태 관리

```javascript
// stores.js
export const currentTab = writable('upload');
export const classificationResult = writable(null);
export const userSettings = writable({...});
```

#### 2. Tab 기반 SPA 라우팅

```svelte
<!-- App.svelte -->
{#if activeTab === 'upload'}
  <Upload />
{:else if activeTab === 'result'}
  <Result />
{/if}
```

#### 3. Drag & Drop 파일 업로드

```svelte
<!-- Upload.svelte -->
<div 
  on:dragover={handleDragOver}
  on:drop={handleDrop}
>
```

## 🧪 Frontend 테스트

### Mock 데이터 생성

```bash
# Backend 컨테이너에서 실행
docker compose exec backend python scripts/create_mock_data.py
```

이 스크립트는 다음을 생성합니다:
- Mock 엑셀 파일 (5개 행 포함)
- 3개의 테스트 이력 데이터 (완료/진행중/실패)
- 기본 사용자 설정

### Frontend 테스트 시나리오

1. **설정 테스트**
   - 설정 화면에서 API 키 입력 및 저장
   - 설정이 올바로 저장되고 조회되는지 확인

2. **파일 업로드 및 분류 테스트**
   - Mock 엑셀 파일 업로드
   - 분류 진행 상태 확인
   - 결과 화면 자동 이동 확인

3. **결과 조회 테스트**
   - 분류 통계 표시 확인
   - 결과 파일 다운로드

4. **이력 조회 테스트**
   - 이력 목록 표시 확인
   - "결과 보기" 버튼으로 결과 화면 이동

### 테스트 데이터 정리

```bash
# Backend 컨테이너에서 실행
docker compose exec backend python scripts/clear_test_data.py
```

## 🛠️ 개발 모드 실행

개발 중에는 hot-reload를 위해 다음과 같이 실행할 수 있습니다:

```bash
# Backend 개발 모드 (별도 터미널)
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend 개발 모드 (별도 터미널)
cd frontend
npm install
npm run dev
```

## 🐛 트러블슈팅

### 1. Nginx 502 Bad Gateway

**원인**: Backend 또는 Frontend 컨테이너가 정상적으로 시작되지 않음

**해결**:
```bash
docker compose logs backend
docker compose logs frontend
```

### 2. OpenAI API 키 오류

**원인**: 유효하지 않은 API 키 또는 네트워크 문제

**해결**:
- 설정 화면에서 올바른 API 키 입력 확인
- Base URL이 올바른지 확인
- 네트워크 연결 확인

### 3. Excel 파일 읽기 오류

**원인**: 잘못된 시트명 또는 컬럼명

**해결**:
- 엑셀 파일의 시트명 확인
- 설정에서 올바른 시트명, 컬럼명 입력

### 4. DB 초기화

문제 발생 시 DB를 초기화할 수 있습니다:

```bash
docker compose down -v
docker compose up -d
```

## 📝 라이선스

본 프로젝트는 내부 사용을 위한 것이며, 외부 배포 시 관련 라이선스를 확인해야 합니다.

## 👥 기여

버그 리포트나 기능 제안은 이슈로 등록해 주세요.

## 📞 연락처

문의사항이 있으시면 프로젝트 관리자에게 연락해 주세요.
