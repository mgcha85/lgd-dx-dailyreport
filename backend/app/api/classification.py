from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from pathlib import Path
from datetime import datetime
import logging
import json
import asyncio

from ..database import get_db
from ..models import ClassificationHistory, UserSettings
from ..schemas import ClassificationRequest, ClassificationResponse
from ..services.excel_handler import ExcelHandler
from ..services.llm_classifier import LLMClassifier
from ..config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/classify", response_model=ClassificationResponse)
async def classify_file(
    request: ClassificationRequest,
    db: Session = Depends(get_db)
):
    """
    파일 분류 실행
    
    엑셀 파일을 읽어서 각 row의 Issue 컬럼을 LLM으로 분류하고
    불량명, 설비명, 조치내용 컬럼을 추가한 결과 파일 생성
    """
    # 파일 존재 확인
    file_path = Path(request.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")
    
    # 사용자 설정 조회
    user_settings = db.query(UserSettings).first()
    if not user_settings or not user_settings.openai_api_key:
        raise HTTPException(
            status_code=400,
            detail="OpenAI API 키가 설정되지 않았습니다. 설정 메뉴에서 API 키를 입력해주세요."
        )
    
    # 이력 생성
    history = ClassificationHistory(
        filename=file_path.name,
        file_path=str(file_path),
        sheet_name=request.sheet_name,
        column_name=request.column_name,
        status="processing"
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    
    try:
        # Excel 읽기
        excel_handler = ExcelHandler()
        df = excel_handler.read_excel(str(file_path), request.sheet_name)
        
        # LLM Classifier 초기화
        classifier = LLMClassifier(
            api_key=user_settings.openai_api_key,
            base_url=user_settings.openai_base_url,
            model=user_settings.model_name,
            mock_mode=settings.mock_llm
        )
        
        # 각 row 처리
        issue_values = excel_handler.get_column_values(df, request.column_name)
        total_rows = len(issue_values)
        classifications = []
        processed_count = 0
        failed_count = 0
        
        for idx, issue_value in enumerate(issue_values):
            # 빈 값이면 skip
            if excel_handler.is_empty_value(issue_value):
                classifications.append({
                    "불량명": "",
                    "설비명": "",
                    "조치내용": ""
                })
                logger.info(f"Row {idx + 1}: Issue 값이 비어있어 건너뜁니다.")
                continue
            
            # LLM 분류
            result, success = classifier.classify(
                issue_content=str(issue_value),
                prompt=request.prompt,
                few_shot_examples=user_settings.few_shot_examples,
                max_retries=3
            )
            
            if success and result:
                classifications.append(result)
                processed_count += 1
                logger.info(f"Row {idx + 1}: 분류 성공 - {result}")
            else:
                classifications.append({
                    "불량명": "",
                    "설비명": "",
                    "조치내용": ""
                })
                failed_count += 1
                logger.warning(f"Row {idx + 1}: 분류 실패")
        
        # 결과 파일 저장 (기존 파일에 컬럼 추가)
        result_filename = f"classified_{file_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        result_path = Path(settings.results_dir) / result_filename
        
        # append_results_to_file 사용 (merged cells 유지)
        excel_handler.append_results_to_file(
            original_file_path=str(file_path),
            output_file_path=str(result_path),
            classifications=classifications,
            sheet_name=request.sheet_name
        )
        
        # 이력 업데이트
        history.status = "completed"
        history.result_path = str(result_path)
        history.total_rows = total_rows
        history.processed_rows = processed_count
        history.failed_rows = failed_count
        history.completed_at = datetime.utcnow()
        db.commit()
        
        return ClassificationResponse(
            history_id=history.id,
            filename=history.filename,
            status=history.status,
            total_rows=total_rows,
            processed_rows=processed_count,
            failed_rows=failed_count,
            result_path=str(result_path),
            message=f"분류가 완료되었습니다. (성공: {processed_count}, 실패: {failed_count})"
        )
        
    except Exception as e:
        # 이력 업데이트 (실패)
        history.status = "failed"
        history.error_message = str(e)
        db.commit()
        
        logger.error(f"분류 중 오류 발생: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"분류 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/classify/stream")
async def classify_file_stream(
    request: ClassificationRequest,
    db: Session = Depends(get_db)
):
    """
    파일 분류 실행 (SSE 스트리밍)
    
    분류 진행상황을 Server-Sent Events로 실시간 전송
    """
    # 파일 존재 확인
    file_path = Path(request.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")
    
    # 사용자 설정 조회
    user_settings = db.query(UserSettings).first()
    if not user_settings or not user_settings.openai_api_key:
        raise HTTPException(
            status_code=400,
            detail="OpenAI API 키가 설정되지 않았습니다. 설정 메뉴에서 API 키를 입력해주세요."
        )

    async def generate():
        # 이력 생성
        history = ClassificationHistory(
            filename=file_path.name,
            file_path=str(file_path),
            sheet_name=request.sheet_name,
            column_name=request.column_name,
            status="processing"
        )
        db.add(history)
        db.commit()
        db.refresh(history)
        
        try:
            # Excel 읽기
            excel_handler = ExcelHandler()
            df = excel_handler.read_excel(str(file_path), request.sheet_name)
            
            # LLM Classifier 초기화
            classifier = LLMClassifier(
                api_key=user_settings.openai_api_key,
                base_url=user_settings.openai_base_url,
                model=user_settings.model_name,
                mock_mode=settings.mock_llm
            )
            
            # 각 row 처리
            issue_values = excel_handler.get_column_values(df, request.column_name)
            total_rows = len(issue_values)
            classifications = []
            processed_count = 0
            failed_count = 0
            
            # 시작 이벤트 전송
            yield f"data: {json.dumps({'type': 'start', 'total': total_rows})}\n\n"
            
            for idx, issue_value in enumerate(issue_values):
                # 빈 값이면 skip
                if excel_handler.is_empty_value(issue_value):
                    classifications.append({
                        "불량명": "",
                        "설비명": "",
                        "조치내용": ""
                    })
                else:
                    # LLM 분류
                    result, success = classifier.classify(
                        issue_content=str(issue_value),
                        prompt=request.prompt,
                        few_shot_examples=user_settings.few_shot_examples,
                        max_retries=3
                    )
                    
                    if success and result:
                        classifications.append(result)
                        processed_count += 1
                    else:
                        classifications.append({
                            "불량명": "",
                            "설비명": "",
                            "조치내용": ""
                        })
                        failed_count += 1
                
                # 진행상황 이벤트 전송
                yield f"data: {json.dumps({'type': 'progress', 'current': idx + 1, 'total': total_rows})}\n\n"
                await asyncio.sleep(0)  # Allow other tasks to run
            
            # 결과 파일 저장
            result_filename = f"classified_{file_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            result_path = Path(settings.results_dir) / result_filename
            
            excel_handler.append_results_to_file(
                original_file_path=str(file_path),
                output_file_path=str(result_path),
                classifications=classifications,
                sheet_name=request.sheet_name
            )
            
            # 이력 업데이트
            history.status = "completed"
            history.result_path = str(result_path)
            history.total_rows = total_rows
            history.processed_rows = processed_count
            history.failed_rows = failed_count
            history.completed_at = datetime.utcnow()
            db.commit()
            
            # 완료 이벤트 전송
            result = {
                'type': 'complete',
                'history_id': history.id,
                'filename': history.filename,
                'status': history.status,
                'total_rows': total_rows,
                'processed_rows': processed_count,
                'failed_rows': failed_count,
                'result_path': str(result_path),
                'message': f"분류가 완료되었습니다. (성공: {processed_count}, 실패: {failed_count})"
            }
            yield f"data: {json.dumps(result)}\n\n"
            
        except Exception as e:
            # 이력 업데이트 (실패)
            history.status = "failed"
            history.error_message = str(e)
            db.commit()
            
            logger.error(f"분류 중 오류 발생: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.get("/classify/{history_id}/download")
async def download_result(
    history_id: int,
    db: Session = Depends(get_db)
):
    """
    분류 결과 파일 다운로드
    """
    history = db.query(ClassificationHistory)\
        .filter(ClassificationHistory.id == history_id)\
        .first()
    
    if not history:
        raise HTTPException(status_code=404, detail="이력을 찾을 수 없습니다.")
    
    if not history.result_path or history.status != "completed":
        raise HTTPException(status_code=400, detail="다운로드할 수 있는 결과 파일이 없습니다.")
    
    result_path = Path(history.result_path)
    if not result_path.exists():
        raise HTTPException(status_code=404, detail="결과 파일을 찾을 수 없습니다.")
    
    return FileResponse(
        path=str(result_path),
        filename=result_path.name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
