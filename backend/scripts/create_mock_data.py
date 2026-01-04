#!/usr/bin/env python3
"""
Mock 데이터 생성 스크립트

Frontend 테스트를 위한 mock 엑셀 파일과 DB 이력 데이터를 생성합니다.
"""

import polars as pl
from pathlib import Path
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal, engine, Base
from app.models import ClassificationHistory, UserSettings
from app.config import settings


def create_mock_excel():
    """Mock 엑셀 파일 생성"""
    data = {
        "날짜": ["2025-01-01", "2025-01-02", "2025-01-03", "2025-01-04", "2025-01-05"],
        "Issue": [
            "DPU 불량 발생, 설비명: LINE-A, 조치: 재작업 실시",
            "스크래치 불량, LINE-B에서 발생, 필터 교체로 조치",
            "",  # 빈 값 테스트
            "기포 불량, 설비 LINE-C, 온도 조정하여 해결",
            "오염 불량, LINE-A, 클리닝 실시"
        ],
        "담당자": ["김철수", "이영희", "박민수", "최지원", "정수진"]
    }
    
    df = pl.DataFrame(data)
    
    # 저장 경로
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    mock_file_path = upload_dir / "mock_일보_Worst55_20250101.xlsx"
    df.write_excel(str(mock_file_path), worksheet="일보_Worst55")
    
    print(f"✅ Mock Excel 파일 생성: {mock_file_path}")
    return str(mock_file_path)


def create_mock_history(db, mock_file_path):
    """Mock 이력 데이터 생성"""
    # 완료된 이력
    history1 = ClassificationHistory(
        filename="mock_일보_Worst55_20250101.xlsx",
        file_path=mock_file_path,
        result_path=None,
        sheet_name="일보_Worst55",
        column_name="Issue",
        status="completed",
        total_rows=5,
        processed_rows=4,
        failed_rows=0,
        created_at=datetime(2025, 1, 1, 10, 0, 0),
        completed_at=datetime(2025, 1, 1, 10, 5, 0)
    )
    
    # 진행 중 이력
    history2 = ClassificationHistory(
        filename="일보_Worst55_20241231.xlsx",
        file_path="/app/data/uploads/일보_Worst55_20241231.xlsx",
        sheet_name="일보_Worst55",
        column_name="Issue",
        status="processing",
        total_rows=10,
        processed_rows=5,
        failed_rows=0,
        created_at=datetime(2024, 12, 31, 15, 30, 0)
    )
    
    # 실패한 이력
    history3 = ClassificationHistory(
        filename="일보_Worst55_20241230.xlsx",
        file_path="/app/data/uploads/일보_Worst55_20241230.xlsx",
        sheet_name="일보_Worst55",
        column_name="Issue",
        status="failed",
        total_rows=8,
        processed_rows=3,
        failed_rows=5,
        error_message="OpenAI API 키가 유효하지 않습니다.",
        created_at=datetime(2024, 12, 30, 9, 15, 0),
        completed_at=datetime(2024, 12, 30, 9, 20, 0)
    )
    
    db.add_all([history1, history2, history3])
    db.commit()
    
    print(f"✅ Mock 이력 데이터 생성: 3건")


def create_mock_settings(db):
    """Mock 사용자 설정 생성"""
    # 기존 설정 확인
    existing = db.query(UserSettings).first()
    if existing:
        print("⚠️  사용자 설정이 이미 존재합니다. 건너뜁니다.")
        return
    
    settings_data = UserSettings(
        openai_api_key="",  # 실제 테스트 시 유효한 키 입력 필요
        openai_base_url="https://api.openai.com/v1",
        model_name="gpt-4o-mini",
        sheet_name="일보_Worst55",
        column_name="Issue",
        few_shot_examples="""예제 1:
Issue: "DPU 불량 발생, 설비명: LINE-A, 조치: 재작업 실시"
결과: {"불량명": "DPU 불량", "설비명": "LINE-A", "조치내용": "재작업 실시"}

예제 2:
Issue: "스크래치 불량, LINE-B에서 발생, 필터 교체로 조치"
결과: {"불량명": "스크래치 불량", "설비명": "LINE-B", "조치내용": "필터 교체"}"""
    )
    
    db.add(settings_data)
    db.commit()
    
    print(f"✅ Mock 사용자 설정 생성")


def main():
    """메인 함수"""
    print("=" * 50)
    print("Mock 데이터 생성 시작")
    print("=" * 50)
    
    # DB 테이블 생성
    Base.metadata.create_all(bind=engine)
    
    # DB 세션
    db = SessionLocal()
    
    try:
        # Mock 엑셀 파일 생성
        mock_file_path = create_mock_excel()
        
        # Mock 이력 데이터 생성
        create_mock_history(db, mock_file_path)
        
        # Mock 설정 생성
        create_mock_settings(db)
        
        print("=" * 50)
        print("✅ Mock 데이터 생성 완료!")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
