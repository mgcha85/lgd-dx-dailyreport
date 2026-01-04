from openai import OpenAI
import json
import os
import random
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


# Mock 응답 데이터
MOCK_RESPONSES = [
    {"불량명": "스크래치", "설비명": "컨베이어 A-1", "조치내용": "청소 및 점검 완료"},
    {"불량명": "기포 발생", "설비명": "코팅기 B-2", "조치내용": "온도 조절 및 재가동"},
    {"불량명": "이물질 혼입", "설비명": "혼합기 C-3", "조치내용": "필터 교체 및 세척"},
    {"불량명": "치수 불량", "설비명": "프레스 D-4", "조치내용": "금형 점검 및 조정"},
    {"불량명": "색상 불량", "설비명": "믹서기 E-5", "조치내용": "원료 비율 재조정"},
]


class LLMClassifier:
    """LLM을 사용한 분류 서비스"""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openai.com/v1",
        model: str = "gpt-4o-mini",
        mock_mode: bool = False
    ):
        """
        LLM Classifier 초기화
        
        Args:
            api_key: OpenAI API 키
            base_url: API Base URL
            model: 사용할 모델명
            mock_mode: Mock 모드 사용 여부
        """
        self.mock_mode = mock_mode
        if not mock_mode:
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )
        else:
            self.client = None
        self.model = model
    
    def classify(
        self,
        issue_content: str,
        prompt: str,
        few_shot_examples: Optional[str] = None,
        max_retries: int = 3
    ) -> Tuple[Optional[Dict[str, str]], bool]:
        """
        Issue 내용을 분류
        
        Args:
            issue_content: 분류할 Issue 내용
            prompt: 사용자 정의 프롬프트
            few_shot_examples: Few-shot learning 예제
            max_retries: JSON 파싱 실패 시 최대 재시도 횟수
            
        Returns:
            (분류 결과 dict, 성공 여부)
            분류 결과: {"불량명": "", "설비명": "", "조치내용": ""}
        """
        # Mock 모드일 때 랜덤 응답 반환
        if self.mock_mode:
            import time
            time.sleep(0.2)  # 실제 API 호출처럼 약간의 딜레이
            mock_response = random.choice(MOCK_RESPONSES).copy()
            logger.info(f"[MOCK] 분류 결과: {mock_response}")
            return mock_response, True
        
        # 전체 프롬프트 구성
        system_prompt = self._build_system_prompt(few_shot_examples)
        user_message = f"{prompt}\n\nIssue 내용: {issue_content}"
        
        for attempt in range(max_retries):
            try:
                # OpenAI API 호출
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
                
                # 응답 추출
                content = response.choices[0].message.content
                
                # JSON 파싱
                result = json.loads(content)
                
                # 필수 키 검증
                if self._validate_result(result):
                    return result, True
                else:
                    logger.warning(f"Invalid result format (attempt {attempt + 1}/{max_retries}): {result}")
                    
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parsing failed (attempt {attempt + 1}/{max_retries}): {e}")
            except Exception as e:
                logger.error(f"Classification failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    return None, False
        
        # 모든 재시도 실패
        return None, False
    
    def _build_system_prompt(self, few_shot_examples: Optional[str] = None) -> str:
        """시스템 프롬프트 구성"""
        base_prompt = """당신은 제조 현장의 일보를 분석하는 전문가입니다.
Issue 내용을 분석하여 다음 정보를 JSON 형식으로 추출해야 합니다:
- 불량명: 발생한 불량의 이름
- 설비명: 불량이 발생한 설비의 이름
- 조치내용: 불량에 대한 조치 내용

응답은 반드시 다음 JSON 형식이어야 합니다:
{"불량명": "추출된 불량명", "설비명": "추출된 설비명", "조치내용": "추출된 조치내용"}

정보를 추출할 수 없는 경우 빈 문자열("")을 사용하세요."""
        
        if few_shot_examples:
            base_prompt += f"\n\n### 예제:\n{few_shot_examples}"
        
        return base_prompt
    
    def _validate_result(self, result: Dict) -> bool:
        """분류 결과 검증"""
        required_keys = ["불량명", "설비명", "조치내용"]
        return all(key in result for key in required_keys)
