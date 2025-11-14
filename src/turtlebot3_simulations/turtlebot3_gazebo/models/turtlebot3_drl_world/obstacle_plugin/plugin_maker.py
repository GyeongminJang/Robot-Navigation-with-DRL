import os
import re
import glob

PLUGIN_TEMPLATE = """// Auto-generated obstacle plugin

#include <ignition/math.hh>
#include <stdio.h>

#include <gazebo/common/common.hh>
#include <gazebo/gazebo.hh>
#include <gazebo/physics/physics.hh>

namespace gazebo {{

class Obstacle{obstacle_id} : public ModelPlugin
{{
public:
  void Load(physics::ModelPtr _parent, sdf::ElementPtr /*_sdf*/)
  {{
    this->model = _parent;

    gazebo::common::PoseAnimationPtr anim(
      new gazebo::common::PoseAnimation("move{obstacle_id}", 39.8, true));

    gazebo::common::PoseKeyFrame *key;

    // 1. 초기 대기 (0초 ~ 시작 시간)
{phase1_frames}

    // 2. 정방향 이동 (시작 시간 ~ 종료 시간)
{phase2_frames}

    // 3. 최종 위치 고정 (종료 시간 ~ 19.9초)
{phase3_frames}

    // 4. 최종 위치 고정 역순 (19.9초 ~ 20.0초)
{phase4_frames}

    // 5. 역방향 이동 (20.0초 ~ (39.8 - 시작 시간)초)
{phase5_frames}

    // 6. 초기 위치 복귀 후 대기 (~39.8초)
{phase6_frames}

    _parent->SetAnimation(anim);
  }}

private:
  physics::ModelPtr model;
  event::ConnectionPtr updateConnection;
}};

GZ_REGISTER_MODEL_PLUGIN(Obstacle{obstacle_id})
}} // namespace gazebo
"""

def parse_trajectory(filepath):
    abs_points = []
    with open(filepath, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 5: continue
            frame = int(parts[0])
            time = frame * 0.1
            x = float(parts[3])
            y = float(parts[4])
            abs_points.append((time, x, y))
    
    if not abs_points:
        return None, None, None, None, None

    # 기준점 설정
    start_time = abs_points[0][0]
    end_time = abs_points[-1][0]
    x0, y0 = abs_points[0][1], abs_points[0][2]
    rel_points = [(t, x-x0, y-y0) for t, x, y in abs_points]
    final_x, final_y = rel_points[-1][1], rel_points[-1][2]

    return start_time, end_time, rel_points, final_x, final_y

def generate_plugin_code(obstacle_id, trajectory_file):
    result = parse_trajectory(trajectory_file)
    if not result:
        return PLUGIN_TEMPLATE.format(
            obstacle_id=obstacle_id,
            phase1_frames='',
            phase2_frames='',
            phase3_frames='',
            phase4_frames='',
            phase5_frames='',
            phase6_frames=''
        )
    
    start_time, end_time, rel_points, final_x, final_y = result
    phases = {1:[], 2:[], 3:[], 4:[], 5:[], 6:[]}

    # 1. 초기 대기 (0초 ~ 시작 시간)
    t = 0.0
    while t < start_time:
        phases[1].append(
            f'    key = anim->CreateKeyFrame({t:.1f});\n'
            f'    key->Translation(ignition::math::Vector3d(0.0, 0.0, 0.01));\n'
            f'    key->Rotation(ignition::math::Quaterniond(0, 0, 0));\n'
        )
        t += 0.1

    # 2. 정방향 이동
    for t, dx, dy in rel_points:
        phases[2].append(
            f'    key = anim->CreateKeyFrame({t:.1f});\n'
            f'    key->Translation(ignition::math::Vector3d({dx:.2f}, {dy:.2f}, 0.01));\n'
            f'    key->Rotation(ignition::math::Quaterniond(0, 0, 0));\n'
        )

    # 3. 최종 위치 고정
    t = end_time + 0.1 if end_time < 19.9 else end_time
    while t <= 19.9:
        phases[3].append(
            f'    key = anim->CreateKeyFrame({t:.1f});\n'
            f'    key->Translation(ignition::math::Vector3d({final_x:.2f}, {final_y:.2f}, 0.01));\n'
            f'    key->Rotation(ignition::math::Quaterniond(0, 0, 0));\n'
        )
        t += 0.1

    # 4. 최종 위치 고정 역순 (3단계 역순)
    t = 19.9
    while t < 20.0:
        phases[4].append(
            f'    key = anim->CreateKeyFrame({t:.1f});\n'
            f'    key->Translation(ignition::math::Vector3d({final_x:.2f}, {final_y:.2f}, 0.01));\n'
            f'    key->Rotation(ignition::math::Quaterniond(0, 0, 0));\n'
        )
        t += 0.1

    # 5. 역방향 이동 (2단계 역순)
    reverse_start = 20.0
    reverse_points = list(reversed(rel_points))
    for t, dx, dy in reverse_points:
        phases[5].append(
            f'    key = anim->CreateKeyFrame({reverse_start:.1f});\n'
            f'    key->Translation(ignition::math::Vector3d({dx:.2f}, {dy:.2f}, 0.01));\n'
            f'    key->Rotation(ignition::math::Quaterniond(0, 0, 0));\n'
        )
        reverse_start += 0.1

    # 6. 초기 위치 복귀 (1단계 역순)
    t = reverse_start
    while t <= 39.8:
        phases[6].append(
            f'    key = anim->CreateKeyFrame({t:.1f});\n'
            f'    key->Translation(ignition::math::Vector3d(0.0, 0.0, 0.01));\n'
            f'    key->Rotation(ignition::math::Quaterniond(0, 0, 0));\n'
        )
        t += 0.1

    return PLUGIN_TEMPLATE.format(
        obstacle_id=obstacle_id,
        phase1_frames="".join(phases[1]),
        phase2_frames="".join(phases[2]),
        phase3_frames="".join(phases[3]),
        phase4_frames="".join(phases[4]),
        phase5_frames="".join(phases[5]),
        phase6_frames="".join(phases[6])
    )

def update_cmake(obstacle_ids, cmake_path):
    if not os.path.exists(cmake_path):
        print(f"오류: {cmake_path} 파일을 찾을 수 없습니다.")
        return False

    with open(cmake_path, 'r') as f:
        lines = f.readlines()

    added = set()
    new_lines = []
    for line in lines:
        new_lines.append(line.rstrip('\n'))
        if 'add_library(' in line:
            lib_name = line.split('(')[1].split()[0]
            added.add(lib_name)

    for oid in obstacle_ids:
        lib_name = f"obstacle{oid}"
        if lib_name not in added:
            new_lines.append(f"add_library({lib_name} SHARED {lib_name}.cc)")
            new_lines.append(f"target_link_libraries({lib_name} ${{GAZEBO_LIBRARIES}})")
            added.add(lib_name)

    with open(cmake_path, 'w') as f:
        f.write('\n'.join(new_lines) + '\n')

    print(f"CMakeLists.txt 업데이트 완료: {len(obstacle_ids)}개 장애물 추가")
    return True

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    trajectory_dir = os.path.join(current_dir, "..", "trajectory")
    cmake_path = os.path.join(current_dir, "CMakeLists.txt")
    
    obstacle_ids = []
    for traj_file in glob.glob(os.path.join(trajectory_dir, "obstacle*.txt")):
        # 파일명에서 ID 추출 (예: obstacle1_1 → "1_1")
        match = re.search(r'obstacle([\d_]+)\.txt', os.path.basename(traj_file))
        if not match:
            continue
        
        obstacle_id = match.group(1)
        obstacle_ids.append(obstacle_id)
        
        # CC 파일 생성
        output_file = os.path.join(current_dir, f"obstacle{obstacle_id}.cc")
        with open(output_file, 'w') as f:
            f.write(generate_plugin_code(obstacle_id, traj_file))
        print(f"생성 완료: {output_file}")
    
    if obstacle_ids:
        update_cmake(obstacle_ids, cmake_path)

if __name__ == "__main__":
    main()