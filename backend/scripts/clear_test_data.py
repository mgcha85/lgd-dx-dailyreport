#!/usr/bin/env python3
"""
테스트 데이터 정리 스크립트

Frontend 테스트 후 생성된 mock 데이터를 정리합니다.
"""

from pathlib import Path
import sys
import shutil

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal, engine, Base
from app.models import ClassificationHistory, UserSettings
from app.config import settings


def clear_database():
    """데이터베이스 정리"""
    db = SessionLocal()
    
    try:
        # 모든 이력 삭제
        deleted_history = db.query(ClassificationHistory).delete()
        print(f"✅ 이력 데이터 삭제: {deleted_history}건")
        
        # 모든 설정 삭제 (선택사항 - 주석 처리)
        # deleted_settings = db.query(UserSettings).delete()
        # print(f"✅ 설정 데이터 삭제: {deleted_settings}건")
        
        db.commit()
        
    except Exception as e:
        print(f"❌ DB 정리 중 오류: {e}")
        db.rollback()
    finally:
        db.close()


def clear_files():
    """업로드 및 결과 파일 정리"""
    upload_dir = Path(settings.upload_dir)
    results_dir = Path(settings.results_dir)
    
    # Upload 디렉토리 정리
    if upload_dir.exists():
        for file in upload_dir.glob("*"):
            if file.is_file():
                file.unlink()
                print(f"✅ 파일 삭제: {file.name}")
    
    # Results 디렉토리 정리
    if results_dir.exists():
        for file in results_dir.glob("*"):
            if file.is_file():
                file.unlink()
                print(f"✅ 결과 파일 삭제: {file.name}")


def main():
    """메인 함수"""
    print("=" * 50)
    print("테스트 데이터 정리 시작")
    print("=" * 50)
    
    try:
        # DB 정리
        clear_database()
        
        # 파일 정리
        clear_files()
        
        print("=" * 50)
        print("✅ 테스트 데이터 정리 완료!")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
