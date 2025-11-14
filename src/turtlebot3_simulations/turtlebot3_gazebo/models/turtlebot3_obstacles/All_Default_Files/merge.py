import os
import shutil
import re

def merge_and_clean(src_dirs, dest_dir):
    """
    1. src_dirs의 모든 파일을 dest_dir로 복사 (중복 이름은 _N으로 변경)
    2. dest_dir의 기존 obstacle*.txt 파일(언더스코어 없는)만 삭제
    """
    # 1. 파일 병합 (중복 시 이름 변경)
    os.makedirs(dest_dir, exist_ok=True)
    existing_files = set(os.listdir(dest_dir))

    for src_dir in src_dirs:
        if not os.path.exists(src_dir):
            print(f"경고: {src_dir} 경로가 존재하지 않습니다.")
            continue
            
        for filename in os.listdir(src_dir):
            if filename.endswith('.txt'):
                src_path = os.path.join(src_dir, filename)
                dest_path = os.path.join(dest_dir, filename)
                
                # 중복 파일 처리
                if filename in existing_files:
                    base, ext = os.path.splitext(filename)
                    count = 1
                    new_filename = f"{base}_{count}{ext}"
                    new_dest_path = os.path.join(dest_dir, new_filename)
                    
                    while os.path.exists(new_dest_path):
                        count += 1
                        new_filename = f"{base}_{count}{ext}"
                        new_dest_path = os.path.join(dest_dir, new_filename)
                    
                    dest_path = new_dest_path
                    existing_files.add(new_filename)
                    print(f"중복 파일: {filename} → {new_filename}로 이름 변경")
                else:
                    existing_files.add(filename)
                    print(f"파일 복사: {filename}")
                
                # 파일 복사
                shutil.copy2(src_path, dest_path)
    
    print(f"\n작업 완료!")
    print(f"- 모든 파일이 {dest_dir}에 병합되었습니다.")

# 실제 경로 설정
base_path = "/home/janggm/turtlebot3_drlnav/src/turtlebot3_simulations/turtlebot3_gazebo/models/turtlebot3_obstacles/Courtyard"
src_dirs = [
    f"{base_path}/Courtyard_2/trajectory"  # Courtyard_7 경로만 소스로 지정 (Courtyard_5는 대상 폴더)
]
dest_dir = f"{base_path}/Courtyard_5/trajectory"

# 실행
if __name__ == "__main__":
    merge_and_clean(src_dirs, dest_dir)
