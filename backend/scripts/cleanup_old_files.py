#!/usr/bin/env python3
"""
30일 이상된 파일 자동 삭제 스크립트

사용법:
    python cleanup_old_files.py              # 실제 삭제 실행
    python cleanup_old_files.py --dry-run    # 삭제 대상 파일만 출력 (삭제 안함)

cron 설정 예시 (매일 새벽 2시에 실행):
    0 2 * * * cd /path/to/backend && python scripts/cleanup_old_files.py >> logs/cleanup.log 2>&1
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime, timedelta

# 프로젝트 루트를 path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_old_files(directory: Path, days: int = 30) -> list[Path]:
    """
    지정된 디렉토리에서 특정 일수 이상 된 파일 목록 반환
    
    Args:
        directory: 검색할 디렉토리 경로
        days: 기준 일수 (기본값: 30일)
    
    Returns:
        오래된 파일들의 Path 리스트
    """
    if not directory.exists():
        logger.warning(f"디렉토리가 존재하지 않습니다: {directory}")
        return []
    
    old_files = []
    cutoff_time = datetime.now() - timedelta(days=days)
    
    for file_path in directory.iterdir():
        if file_path.is_file():
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            if mtime < cutoff_time:
                old_files.append(file_path)
    
    return old_files


def delete_files(files: list[Path], dry_run: bool = False) -> tuple[int, int]:
    """
    파일 목록 삭제
    
    Args:
        files: 삭제할 파일 목록
        dry_run: True면 실제 삭제하지 않고 로그만 출력
    
    Returns:
        (성공 개수, 실패 개수)
    """
    success_count = 0
    fail_count = 0
    
    for file_path in files:
        try:
            if dry_run:
                logger.info(f"[DRY-RUN] 삭제 예정: {file_path}")
            else:
                file_path.unlink()
                logger.info(f"삭제됨: {file_path}")
            success_count += 1
        except Exception as e:
            logger.error(f"삭제 실패: {file_path} - {e}")
            fail_count += 1
    
    return success_count, fail_count


def main():
    parser = argparse.ArgumentParser(description='30일 이상된 파일 삭제')
    parser.add_argument(
        '--dry-run', 
        action='store_true', 
        help='실제 삭제하지 않고 대상 파일만 출력'
    )
    parser.add_argument(
        '--days', 
        type=int, 
        default=30, 
        help='기준 일수 (기본값: 30)'
    )
    args = parser.parse_args()
    
    logger.info("=" * 50)
    logger.info(f"파일 정리 시작 - 기준: {args.days}일 이상 된 파일")
    if args.dry_run:
        logger.info("*** DRY-RUN 모드 (실제 삭제 안함) ***")
    logger.info("=" * 50)
    
    # 정리할 디렉토리들
    directories = [
        Path(settings.upload_dir),
        Path(settings.results_dir),
    ]
    
    total_success = 0
    total_fail = 0
    
    for directory in directories:
        logger.info(f"\n[{directory}] 검색 중...")
        
        old_files = get_old_files(directory, args.days)
        
        if not old_files:
            logger.info(f"  삭제 대상 파일 없음")
            continue
        
        logger.info(f"  삭제 대상: {len(old_files)}개 파일")
        success, fail = delete_files(old_files, args.dry_run)
        total_success += success
        total_fail += fail
    
    logger.info("\n" + "=" * 50)
    if args.dry_run:
        logger.info(f"결과: {total_success}개 파일 삭제 예정")
    else:
        logger.info(f"결과: {total_success}개 삭제됨, {total_fail}개 실패")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
