from ..common.settings import REWARD_FUNCTION, COLLISION_OBSTACLE, COLLISION_WALL, TUMBLE, SUCCESS, TIMEOUT
import numpy as np
import math

goal_dist_initial = 0
reward_function_internal = None

def get_reward(succeed, action_linear, action_angular, distance_to_goal, goal_angle, min_obstacle_distance):
    return reward_function_internal(
        succeed, action_linear, action_angular,
        distance_to_goal, goal_angle, min_obstacle_distance
    )

# --- 기본 예시 보상 함수 (참고용) ---
def get_reward_A(succeed, action_linear, action_angular, goal_dist, goal_angle, min_obstacle_dist):
    
    r_yaw = -1 * abs(goal_angle)
    r_vangular = -1 * (action_angular**2)
    r_distance = (2 * goal_dist_initial) / (goal_dist_initial + goal_dist) - 1
    r_obstacle = -20 if min_obstacle_dist < 0.22 else 0
    r_vlinear = -(4.84/100) * (((1.0 - action_linear) * 10) ** 2)
    reward = r_yaw + r_distance + r_obstacle + r_vlinear + r_vangular - 1

    if succeed == SUCCESS:
        reward += 2500
    elif succeed in [COLLISION_OBSTACLE, COLLISION_WALL, TUMBLE]:
        reward -= 2000
    return float(reward)

# --- 복잡 환경용 최적화 보상 함수 (직진 강화, 회전 억제, 목표/장애물 근접 감속, 목표 정렬) ---
def get_reward_B(succeed, action_linear, action_angular, goal_dist, goal_angle, min_obstacle_dist):

    # === 1. 회전 억제 ===
    # 회전 각속도 제곱에 비례한 강력한 페널티
    r_rotation = -(action_angular ** 2) * 5.0
    # 과도한 회전(>0.6rad/s) 더 강하게 억제
    if abs(action_angular) > 0.6:
        r_rotation -= 20.0

    # === 2. 전진 운동 장려 ===
    # 양의 선형 속도(전진)일 때 높은 보상
    r_forward = 0.0
    if action_linear > 0.5:
        r_forward += 2.0  # 고속 직진 보상
    if action_linear > 0:
        r_forward += action_linear * 3.0  # 전진 비례 보상

    # === 3. 목표 방향 정확히 향할 때 보상===
    # 목표 각도 0(직진)이면 추가 보상, 아니면 목표 선회 상태에 따라 페널티
    if abs(goal_angle) < 0.1:
        r_goal_align = 1.0
    else:
        r_goal_align = -abs(goal_angle) * 2.0

    # === 4. 목표/장애물 근접 감속 효과 ===
    # 목표 근처 감속
    if goal_dist < 1.0:
        max_goal_speed = 0.2
        if action_linear > max_goal_speed:
            r_goal_slow = -(action_linear - max_goal_speed) * 15.0
        else:
            r_goal_slow = 2.0
    else:
        r_goal_slow = 0.0

    # 장애물 근처 감속
    if min_obstacle_dist < 0.4:
        max_obs_speed = 0.2
        if action_linear > max_obs_speed:
            r_obstacle_slow = -(action_linear - max_obs_speed) * 12.0
        else:
            r_obstacle_slow = 1.0
    else:
        r_obstacle_slow = 0.0

    # === 5. 목표 거리와 위험 페널티 ===
    r_distance = (2 * goal_dist_initial) / (goal_dist_initial + goal_dist) - 1 if goal_dist_initial > 0 else 0.0
    r_safety = -25.0 if min_obstacle_dist < 0.30 else 0.0

    # === 6. 기본 시간 페널티 ===
    r_time = -1

    # === 7. 총 보상 합산 ===
    reward = (
        r_rotation +
        r_forward +
        r_goal_align +
        r_goal_slow +
        r_obstacle_slow +
        r_distance +
        r_safety +
        r_time
    )

    # === 8. 종료 상태(목표 성공/충돌) 보정 ===
    if succeed == SUCCESS:
        reward += 2500.0
    elif succeed in (COLLISION_OBSTACLE, COLLISION_WALL, TUMBLE):
        reward -= 2000.0

    return float(reward)

# 기존 연구에 있었던 보상함수 적용
def get_reward_C(succeed, action_linear, action_angular, goal_dist, goal_angle, min_obstacle_dist, prev_goal_dist=None):
    r_yaw = -1 * abs(goal_angle)
    r_vangular = -1 * (action_angular ** 2)
    r_distance = (2 * goal_dist_initial) / (goal_dist_initial + goal_dist) - 1
    r_obstacle = -20 if min_obstacle_dist < 0.22 else 0
    r_vlinear = -(4.84 / 100) * (((1.0 - action_linear) * 10) ** 2)

    reward = r_yaw + r_distance + r_obstacle + r_vlinear + r_vangular - 1

    # 거리 차분 보상 추가
    if prev_goal_dist is not None:
        eta_r = 10.0  # 거리 차분 보상 가중치
        reward += eta_r * (prev_goal_dist - goal_dist)

    # 방향 정렬 보상 강화
    if abs(goal_angle) < 0.1:
        reward += 1.0  # 목표 방향 정확도 보상
    else:
        reward -= abs(goal_angle) * 2.0

    if succeed == SUCCESS:
        reward += 2500
    elif succeed in [COLLISION_OBSTACLE, COLLISION_WALL, TUMBLE, TIMEOUT]:
        reward -= 2000

    return float(reward)


# Define your own reward function by defining a new function: 'get_reward_X'
# Replace X with your reward function name and configure it in settings.py

def reward_initalize(init_distance_to_goal):
    global goal_dist_initial
    goal_dist_initial = init_distance_to_goal

function_name = "get_reward_" + REWARD_FUNCTION
reward_function_internal = globals()[function_name]
if reward_function_internal == None:
    quit(f"Error: reward function {function_name} does not exist")