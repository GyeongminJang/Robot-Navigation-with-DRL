import os
import glob

def process_all_trajectories(base_dir, output_base_dir='processed_data'):
    """
    모든 폴더의 txt 파일을 처리하고, 각 파일별로 전용 폴더 생성
    """
    # 출력 디렉토리 생성
    os.makedirs(output_base_dir, exist_ok=True)
    
    # 통계 카운터
    total_files = 0
    total_objects = 0
    
    # 모든 환경 폴더 탐색 (Cafe_street, Corridor 등)
    for env_folder in [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f))]:
        env_path = os.path.join(base_dir, env_folder)
        
        # 출력 디렉토리는 처리 대상에서 제외
        if env_path == os.path.join(base_dir, output_base_dir):
            continue
            
        print(f"처리 중: {env_folder}")
        
        # 환경 폴더 내 모든 txt 파일 재귀적으로 검색
        for root, dirs, files in os.walk(env_path):
            for file in files:
                if file.endswith('.txt'):
                    total_files += 1
                    file_path = os.path.join(root, file)
                    
                    # 환경 폴더 기준 상대 경로 계산
                    rel_path = os.path.relpath(root, env_path)
                    
                    # 파일명에서 확장자 제거한 이름으로 폴더 생성
                    file_name_without_ext = os.path.splitext(file)[0]
                    
                    # 출력 디렉토리 경로 생성 (폴더 구조 유지)
                    if rel_path == '.':  # 환경 폴더 직접 하위 파일인 경우
                        output_dir = os.path.join(output_base_dir, env_folder, file_name_without_ext)
                    else:
                        output_dir = os.path.join(output_base_dir, env_folder, rel_path, file_name_without_ext)
                    
                    os.makedirs(output_dir, exist_ok=True)
                    
                    # 파일 처리
                    print(f"  - 파일 처리 중: {os.path.join(rel_path, file)}")
                    objects_count = process_single_trajectory(file_path, output_dir)
                    total_objects += objects_count
    
    print(f"\n처리 완료:")
    print(f"총 {total_files}개 파일에서 {total_objects}개 객체를 처리했습니다.")
    print(f"결과는 '{output_base_dir}' 폴더에 저장되었습니다.")

def process_single_trajectory(input_file, output_dir):
    """
    개별 궤적 파일을 처리하고 결과를 output_dir에 저장
    """
    # 기존 process_single_trajectory 함수 코드 유지
    # 데이터 저장 구조: {object_id: {frame: (x, y)}}
    data = {}
    
    # 입력 파일 처리
    with open(input_file, 'r') as f:
        for line in f:
            parts = line.strip().split()
            
            # 필드 길이 확인
            if len(parts) < 5:
                continue
                
            try:
                frame = int(parts[0])
                obj_type = parts[1]
                obj_id = int(parts[2])
                x = round(float(parts[3]), 2)
                y = round(float(parts[4]), 2)
            except (ValueError, IndexError):
                continue  # 잘못된 형식 무시
            
            # husky 제외 및 프레임 제한
            if obj_type == 'husky' or frame > 199:
                continue
            
            # 데이터 저장
            if obj_id not in data:
                data[obj_id] = {}
            data[obj_id][frame] = (x, y)
    
    # 각 장애물별 파일 생성
    for obj_id in sorted(data.keys()):
        output_file = os.path.join(output_dir, f'obstacle{obj_id}.txt')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # 프레임별 데이터 작성
            for frame in sorted(data[obj_id].keys()):
                x, y = data[obj_id][frame]
                f.write(f"{frame} Pedestrian {obj_id} {x:.2f} {y:.2f}\n")
    
    return len(data)  # 처리된 객체 수 반환

# 메인 실행
if __name__ == "__main__":
    # 현재 디렉토리 기준
    current_dir = os.path.dirname(os.path.abspath(__file__))
    process_all_trajectories(current_dir)
