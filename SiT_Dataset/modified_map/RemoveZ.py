import json
import os
from pathlib import Path

def process_json_files(input_dir=".", output_dir="modified2"):
    """
    폴더 내 모든 JSON 파일의 z좌표 제거
    - input_dir: 원본 파일이 있는 폴더 (기본값: 현재 폴더)
    - output_dir: 수정본 저장 폴더 (기본값: 'modified')
    """
    
    # 출력 폴더 생성
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 폴더 내 모든 JSON 파일 처리
    for filename in os.listdir(input_dir):
        if not filename.endswith(".json"):
            continue
        
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)
        
        # JSON 파일 처리
        with open(input_path, 'r', encoding='utf-8') as f:
            try:
                original_data = json.load(f)
            except json.JSONDecodeError:
                print(f"⚠️ {filename} 파싱 실패: 유효하지 않은 JSON 형식")
                continue
        
        # z좌표 제거 함수
        def remove_z_coord(obj):
            if isinstance(obj, dict):
                return {k: remove_z_coord(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                if all(isinstance(i, (int, float)) for i in obj) and len(obj) == 3:
                    return obj[:2]  # x,y만 남김
                else:
                    return [remove_z_coord(i) for i in obj]
            else:
                return obj
        
        # 데이터 변환
        modified_data = remove_z_coord(original_data)
        
        # 수정본 저장
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(modified_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ {filename} 처리 완료 → {output_path}")

# 사용 예시 (현재 폴더의 모든 JSON 파일 처리)
process_json_files()
