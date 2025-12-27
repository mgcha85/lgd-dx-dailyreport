# 일보 자동 분류 시스템

LLM을 활용한 제조 현장 일보 자동 분류 시스템입니다. 엑셀 파일의 Issue 컬럼을 분석하여 불량명, 설비명, 조치내용을 자동으로 추출합니다.

## 📋 프로젝트 개요

- **제조 현장 일보 자동화**: 작업자가 작성한 비정형 텍스트 데이터를 정형 데이터로 변환
- **LLM 기반 분류**: Few-shot Prompting을 활용하여 높은 정확도의 분류 수행
- **사용자 피드백 루프**: 분류 결과 수정 시 이를 학습하여 지속적인 성능 향상
- **설정 관리**: OpenAI API 설정, Few-shot 예제 관리

## 🛠️ 사전 요구 사항 (Prerequisites)

이 프로젝트를 로컬 환경에서 실행하기 위해서는 다음 도구들이 설치되어 있어야 합니다.

1.  **Python & uv** (Backend)
    -   Python 3.10 이상
    -   [`uv`](https://github.com/astral-sh/uv) (Python 패키지 관리자) 설치:
        ```bash
        # macOS/Linux
        curl -LsSf https://astral.sh/uv/install.sh | sh
        
        # Windows
        powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
        ```

2.  **Node.js & npm** (Frontend)
    -   Node.js 18.0.0 이상 권장
    -   [Node.js 공식 홈페이지](https://nodejs.org/)에서 설치 가능

## 🚀 설치 및 실행 방법

### 1. 환경 변수 설정

프로젝트 루트 디렉토리에서 `.env` 파일을 생성하고 필요한 환경 변수를 설정합니다.

```bash
# 레포지토리 클론 (이미 있다면 생략)
cd lgd-dx-dailyreport

# 환경 변수 파일 생성
cp .env.example .env

# .env 파일 편집 (필요시)
# API_KEY 등은 웹 화면에서도 설정 가능하므로 기본값 유지 가능
```

### 2. Backend 실행 (Python)

`backend` 디렉토리로 이동하여 `uv`를 사용해 의존성을 설치하고 서버를 실행합니다.

```bash
cd backend

# 가상환경 생성 및 의존성 설치
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

# 서버 실행 (개발 모드)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

*   서버가 정상적으로 실행되면 `http://localhost:8000/docs` 에서 Swagger UI를 확인할 수 있습니다.
*   **외부 접속**: `http://<서버IP>:8000/docs`로 접속하여 외부에서도 API 문서를 확인할 수 있습니다.

### 3. Frontend 실행 (Svelte/Vite)

새로운 터미널을 열고 `frontend` 디렉토리로 이동하여 패키지를 설치하고 개발 서버를 실행합니다.

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

*   브라우저에서 `http://localhost:5173` 으로 접속하여 애플리케이션을 사용합니다.
*   **외부 접속**: `http://<서버IP>:5173`으로 접속하면, 내부적으로 `vite`가 API 요청을 로컬 백엔드(`localhost:8000`)로 안전하게 전달(Proxy)합니다. 따라서 별도의 설정 없이 외부에서도 정상적으로 기능이 동작합니다.

### 4. 스크립트로 실행 (간편 실행)

매번 터미널을 따로 열 필요 없이 스크립트를 통해 백그라운드에서 실행하고 로그를 관리할 수 있습니다.

#### 실행 (`start.sh`)
```bash
./start.sh
```
*   `logs/` 디렉토리에 로그(`backend.log`, `frontend.log`)가 저장됩니다.
*   백그라운드에서 실행되므로 터미널을 종료해도 서버는 계속 실행됩니다.

#### 중지 (`stop.sh`)
```bash
./stop.sh
```
*   실행 중인 서버 프로세스를 안전하게 종료합니다.

## 📂 소스 트리

```
lgd-dx-dailyreport/
├── .env.example                # 환경 변수 템플릿
├── .gitignore                  # Git 제외 파일 목록
├── README.md                   # 프로젝트 문서 (본 파일)
│
├── backend/                    # FastAPI 백엔드
│   ├── app/
│   │   ├── main.py            # 진입점
│   │   ├── api/               # API 라우터
│   │   ├── core/              # 핵심 로직 (LLM 등)
│   │   └── database.py        # DB 연결
│   ├── data/                   # 데이터 저장소 (SQLite, 파일)
│   └── requirements.txt        # Python 의존성
│
└── frontend/                   # Svelte 프론트엔드
    ├── src/
    │   ├── App.svelte         # 메인 앱 컴포넌트
    │   ├── components/        # UI 컴포넌트
    │   └── stores.js          # 상태 관리
    ├── package.json            # Node.js 의존성
    └── vite.config.js          # Vite 설정 (Proxy 설정 포함)
```

## 💻 사용 가이드

### 1. 설정 화면 (⚙️ Settings)

첫 사용 시 반드시 설정을 완료해야 합니다.

1.  **OpenAI API 설정**
    -   API Key 입력 (필수)
    -   Base URL (기본값 사용 가능)
    -   Model Name (기본값: gpt-4o-mini)

### 2. 파일 업로드 및 분류

1.  **Upload 탭**: 분석할 엑셀 파일을 업로드합니다.
2.  분석할 시트와 컬럼(예: Issue)을 선택합니다.
3.  **"분류 시작"** 버튼을 클릭하여 분석을 실행합니다.

### 3. 결과 확인 및 다운로드

1.  **Result 탭**: 분류된 결과를 확인합니다.
2.  결과가 만족스럽지 않은 경우, 직접 수정하고 저장할 수 있습니다.
3.  **"엑셀 다운로드"** 버튼으로 결과를 파일로 저장합니다.

## 📝 라이선스

본 프로젝트는 내부 사용을 위한 것이며, 외부 배포 시 관련 라이선스를 확인해야 합니다.
