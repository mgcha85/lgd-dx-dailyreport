#!/usr/bin/env python3
"""샘플 일보 엑셀 파일 생성 스크립트 (openpyxl만 사용)"""

from openpyxl import Workbook
from pathlib import Path

# 샘플 데이터
headers = ["날짜", "라인", "Issue", "담당자"]
data = [
    ["2025-01-01", "A라인", "컨베이어 A-1에서 스크래치 발견, 표면 청소 및 점검 완료", "김철수"],
    ["2025-01-01", "B라인", "코팅기 B-2 온도 이상으로 기포 발생, 온도 조절 후 재가동", "이영희"],
    ["2025-01-02", "A라인", "혼합기 C-3 필터에 이물질 혼입 발생, 필터 교체 및 세척 완료", "박민수"],
    ["2025-01-02", "C라인", "프레스 D-4 치수 불량 발생, 금형 점검 및 조정", "정수진"],
    ["2025-01-03", "B라인", "믹서기 E-5에서 색상 불량 확인, 원료 비율 재조정", "김철수"],
    ["2025-01-03", "A라인", "로봇암 F-6 동작 지연 발생, 모터 점검 및 그리스 주입", "이영희"],
    ["2025-01-04", "C라인", "레이저 커터 G-7 정밀도 저하, 렌즈 청소 및 교정", "박민수"],
    ["2025-01-04", "B라인", "포장기 H-8에서 접착 불량 발생, 온도 및 압력 조정 완료", "정수진"],
]

# 워크북 생성
wb = Workbook()
ws = wb.active
ws.title = "일보_Worst55"

# 헤더 추가
ws.append(headers)

# 데이터 추가
for row in data:
    ws.append(row)

# 파일 경로 설정 및 저장
output_dir = Path("/mnt/data/pythonProjects/lgd-dx-dailyreport/backend/data/uploads")
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / "sample_daily_report.xlsx"

wb.save(output_path)
print(f"샘플 엑셀 파일 생성 완료: {output_path}")
