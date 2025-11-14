#!/usr/bin/env python3

import os
import shutil
import glob
import re

def create_obstacle_model(obstacle_name, source_dir, target_dir):
    """
    obstacle 모델을 기반으로 새로운 장애물 모델 생성 (전체 이름 사용)
    """
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    os.makedirs(target_dir, exist_ok=True)

    # model.config 파일 수정
    config_path = os.path.join(source_dir, "model.config")
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config_content = f.read()
        
        # 이름 전체를 사용하여 변경 (예: obstacle20_1)
        config_content = re.sub(
            r'<name>.*?</name>',
            f'<name>{obstacle_name}</name>',
            config_content
        )
        
        with open(os.path.join(target_dir, "model.config"), 'w') as f:
            f.write(config_content)

    # model.sdf 파일 수정
    sdf_path = os.path.join(source_dir, "model.sdf")
    if os.path.exists(sdf_path):
        with open(sdf_path, 'r') as f:
            sdf_content = f.read()
        
        # 모델 이름 전체 변경
        sdf_content = re.sub(
            r'<model name="obstacle">',
            f'<model name="{obstacle_name}">',
            sdf_content
        )
        
        # 링크 이름 변경 (예: link_obstacle20_1)
        sdf_content = re.sub(
            r'link_obstacle',
            f'link_{obstacle_name}',
            sdf_content
        )
        
        # 플러그인 이름 변경 (예: p3d_base_controller_obstacle20_1)
        sdf_content = re.sub(
            r'name="p3d_base_controller_obstacle"',
            f'name="p3d_base_controller_{obstacle_name}"',
            sdf_content
        )
        
        with open(os.path.join(target_dir, "model.sdf"), 'w') as f:
            f.write(sdf_content)

    print(f"✓ {obstacle_name} 모델 생성 완료")

def main():
    # 경로 설정
    base_dir = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.join(base_dir, "obstacle")
    trajectory_dir = os.path.join(base_dir, "trajectory")

    # trajectory 폴더에서 파일 처리
    obstacle_files = []
    for filename in os.listdir(trajectory_dir):
        if filename.startswith("obstacle") and filename.endswith(".txt"):
            obstacle_name = os.path.splitext(filename)[0]  # 확장자 제거 (예: obstacle20_1)
            obstacle_files.append(obstacle_name)

    # 모델 생성
    for obstacle_name in obstacle_files:
        target_dir = os.path.join(base_dir, obstacle_name)
        create_obstacle_model(obstacle_name, source_dir, target_dir)

    print(f"\n처리 완료: {len(obstacle_files)}개의 장애물 모델 생성됨")

if __name__ == "__main__":
    main()
