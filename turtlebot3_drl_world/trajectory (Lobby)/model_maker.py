#!/usr/bin/env python3

import os
import re

def create_obstacles_file():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    trajectory_dir = os.path.join(base_dir, "trajectory")
    output_file = os.path.join(base_dir, "burger.model")

    # SDF 헤더 및 기본 환경 설정
    output_content = [
        '<?xml version="1.0"?>',
        '<sdf version="1.6">',
        '  <world name="default">',
        '    <include>',
        '      <uri>model://ground_plane</uri>',
        '    </include>',
        '    <include>',
        '      <uri>model://sun</uri>',
        '    </include>',
        '    <scene>',
        '      <shadows>false</shadows>',
        '    </scene>',
        '    <gui fullscreen="0">',
        '      <camera name="user_camera">',
        '        <pose>0.319654 -0.235002 9.29441 0 1.5138 0.009599</pose>',
        '        <view_controller>orbit</view_controller>',
        '        <projection_type>perspective</projection_type>',
        '      </camera>',
        '    </gui>',
        '    <physics type="ode">',
        '      <real_time_update_rate>0</real_time_update_rate>',
        '      <max_step_size>0.005</max_step_size>',
        '      <real_time_factor>1</real_time_factor>',
        '      <ode>',
        '        <solver>',
        '          <type>quick</type>',
        '          <iters>150</iters>',
        '          <precon_iters>0</precon_iters>',
        '          <sor>1.400000</sor>',
        '          <use_dynamic_moi_rescaling>1</use_dynamic_moi_rescaling>',
        '        </solver>',
        '        <constraints>',
        '          <cfm>0.00001</cfm>',
        '          <erp>0.2</erp>',
        '          <contact_max_correcting_vel>2000.000000</contact_max_correcting_vel>',
        '          <contact_surface_layer>0.01000</contact_surface_layer>',
        '        </constraints>',
        '      </ode>',
        '    </physics>',
        '    <model name="Lobby">',
        '      <static>1</static>',
        '      <include>',
        '        <uri>model://turtlebot3_new_world/Lobby</uri>',
        '      </include>',
        '    </model>'
    ]

    # 장애물 모델 생성
    for filename in sorted(os.listdir(trajectory_dir)):
        if filename.startswith("obstacle") and filename.endswith(".txt"):
            # 언더스코어 포함한 전체 obstacle 이름 추출
            obstacle_name = os.path.splitext(filename)[0]
            match = re.match(r'obstacle(\d+_?\d*)', obstacle_name)
            
            if match:
                obstacle_id = match.group(1)
                file_path = os.path.join(trajectory_dir, filename)
                initial_pose = get_first_pose(file_path)
                
                if initial_pose:
                    x, y = initial_pose
                    model_block = f"""
    <model name="turtlebot3_drl_obstacle{obstacle_id}">
      <plugin name="obstacle{obstacle_id}" filename="libobstacle{obstacle_id}.so"/>
      <include>
        <pose>{x} {y} 0 0 0 0</pose>
        <uri>model://turtlebot3_drl_world/obstacle{obstacle_id}</uri>
      </include>
    </model>"""
                    output_content.append(model_block)
                    print(f"Obstacle {obstacle_id}: 초기 위치 ({x}, {y})")

    # Burger 모델 추가
    output_content.append("""
    <include>
      <pose>0 0 0 0 0 0</pose>
      <uri>model://turtlebot3_burger</uri>
    </include>
  </world>
</sdf>""")

    with open(output_file, 'w') as f:
        f.write("\n".join(output_content))

    print(f"\n생성 완료: {output_file}")

def get_first_pose(file_path):
    """트레이젝토리 파일에서 첫 번째 포즈 추출"""
    try:
        with open(file_path, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 5:
                    return (round(float(parts[3]), 2), 
                            round(float(parts[4]), 2))
    except Exception as e:
        print(f"경고: {file_path} 처리 실패 - {e}")
    return None

if __name__ == "__main__":
    create_obstacles_file()
