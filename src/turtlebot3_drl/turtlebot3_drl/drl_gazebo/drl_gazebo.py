#!/usr/bin/env python3
#
# Copyright 2019 ROBOTIS CO., LTD.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Authors: Ryan Shim, Gilbert, Tomas

import os
import random
import math
import numpy
import time

from gazebo_msgs.srv import DeleteEntity, SpawnEntity
from std_srvs.srv import Empty
from geometry_msgs.msg import Pose

import rclpy
from rclpy.qos import QoSProfile
from rclpy.node import Node

from turtlebot3_msgs.srv import RingGoal
import xml.etree.ElementTree as ET
from ..drl_environment.drl_environment import ARENA_LENGTH, ARENA_WIDTH, ENABLE_DYNAMIC_GOALS
from ..common.settings import ENABLE_TRUE_RANDOM_GOALS

NO_GOAL_SPAWN_MARGIN = 0.3 # meters away from any wall

# # --- 후보 로봇 위치 리스트 ---
# ROBOT_START_POSITIONS = [
#     (2.5, 5.0, -1.57),
#     (4.0, -6.0, 3.14),
#     # 필요한 만큼 추가
# ]

class DRLGazebo(Node):
    def __init__(self):
        super().__init__('drl_gazebo')

        """************************************************************
        ** Initialise variables
        ************************************************************"""

        self.entity_dir_path = (os.path.dirname(os.path.realpath(__file__))).replace(
            'turtlebot3_drl/lib/python3.8/site-packages/turtlebot3_drl/drl_gazebo',
            'turtlebot3_gazebo/share/turtlebot3_gazebo/models/turtlebot3_drl_world/goal_box')
        self.entity_path = os.path.join(self.entity_dir_path, 'model.sdf')
        self.entity = open(self.entity_path, 'r').read()
        self.entity_name = 'goal'

        with open('/tmp/drlnav_current_stage.txt', 'r') as f:
            self.stage = int(f.read())
        print(f"running on stage: {self.stage}, dynamic goals enabled: {ENABLE_DYNAMIC_GOALS}")

        self.prev_x, self.prev_y = -1, -1
        self.goal_x, self.goal_y = 0.0, 1.0

        # # --- 로봇 모델 파일 경로 (환경에 맞게 수정) ---
        # self.robot_entity_name = 'turtlebot3'
        # self.robot_model_path = '/home/janggm/turtlebot3_drlnav/src/turtlebot3_simulations/turtlebot3_gazebo/models/turtlebot3_burger/model.sdf'
        # self.robot_entity = open(self.robot_model_path, 'r').read()

        self.robot_pose = Pose()

        """************************************************************
        ** Initialise ROS publishers, subscribers and clients
        ************************************************************"""
        # Initialise publishers
        self.goal_pose_pub = self.create_publisher(Pose, 'goal_pose', QoSProfile(depth=10))

        # Initialise client
        self.delete_entity_client       = self.create_client(DeleteEntity, 'delete_entity')
        self.spawn_entity_client        = self.create_client(SpawnEntity, 'spawn_entity')
        self.reset_simulation_client    = self.create_client(Empty, 'reset_simulation')
        self.gazebo_pause               = self.create_client(Empty, '/pause_physics')

        # Initialise servers
        self.task_succeed_server    = self.create_service(RingGoal, 'task_succeed', self.task_succeed_callback)
        self.task_fail_server       = self.create_service(RingGoal, 'task_fail', self.task_fail_callback)

        self.obstacle_coordinates   = self.get_obstacle_coordinates()
        self.init_callback()

    """*******************************************************************************
    ** Callback functions and relevant functions
    *******************************************************************************"""

    def init_callback(self):
        self.delete_entity()
        self.reset_simulation()
        self.publish_callback()
        print("Init, goal pose:", self.goal_x, self.goal_y)
        time.sleep(1)

    def publish_callback(self):
        # Publish goal pose
        goal_pose = Pose()
        goal_pose.position.x = self.goal_x
        goal_pose.position.y = self.goal_y
        self.goal_pose_pub.publish(goal_pose)
        self.spawn_entity()

    # # --- 로봇 위치 랜덤화 함수 ---
    # def reset_robot_position(self):
    #     x, y, yaw = random.choice(ROBOT_START_POSITIONS)
    #     # 1. 기존 로봇 삭제
    #     del_req = DeleteEntity.Request()
    #     del_req.name = self.robot_entity_name
    #     while not self.delete_entity_client.wait_for_service(timeout_sec=1):
    #         self.get_logger().info('delete_entity service not available, waiting...')
    #     self.delete_entity_client.call_async(del_req)
    #     time.sleep(1)  # 삭제가 완료될 때까지 대기

    #     # 2. 새로운 위치로 로봇 스폰
    #     spawn_req = SpawnEntity.Request()
    #     spawn_req.name = self.robot_entity_name
    #     spawn_req.xml = self.robot_entity
    #     pose = Pose()
    #     pose.position.x = x
    #     pose.position.y = y
    #     pose.position.z = 0.0
    #     pose.orientation.z = math.sin(yaw / 2)
    #     pose.orientation.w = math.cos(yaw / 2)
    #     spawn_req.initial_pose = pose
    #     while not self.spawn_entity_client.wait_for_service(timeout_sec=1):
    #         self.get_logger().info('spawn_entity service not available, waiting...')
    #     self.spawn_entity_client.call_async(spawn_req)
    #     time.sleep(1)  # 스폰 완료 대기

    def task_succeed_callback(self, request, response):
        self.delete_entity()
        if ENABLE_TRUE_RANDOM_GOALS:
            self.generate_random_goal()
            print(f"success: generate (random) a new goal, goal pose: {self.goal_x:.2f}, {self.goal_y:.2f}")
        elif ENABLE_DYNAMIC_GOALS:
            self.generate_dynamic_goal_pose(request.robot_pose_x, request.robot_pose_y, request.radius)
            print(f"success: generate a new goal, goal pose: {self.goal_x:.2f}, {self.goal_y:.2f}, radius: {request.radius:.2f}")
        else:
            self.generate_goal_pose()
            print(f"success: generate a new goal, goal pose: {self.goal_x:.2f}, {self.goal_y:.2f}")
        return response

    def task_fail_callback(self, request, response):
        self.delete_entity()
        self.reset_simulation()
        # self.reset_robot_position()  # --- 에피소드 실패 시 로봇 위치 랜덤화 --
        if ENABLE_TRUE_RANDOM_GOALS:
            self.generate_random_goal()
            print(f"fail: reset the environment, (random) goal pose: {self.goal_x:.2f}, {self.goal_y:.2f}")
        elif ENABLE_DYNAMIC_GOALS:
            self.generate_dynamic_goal_pose(request.robot_pose_x, request.robot_pose_y, request.radius)
            print(f"fail: reset the environment, goal pose: {self.goal_x:.2f}, {self.goal_y:.2f}, radius: {request.radius:.2f}")
        else:
            self.generate_goal_pose()
            print(f"fail: reset the environment, goal pose: {self.goal_x:.2f}, {self.goal_y:.2f}")
        return response

    def goal_is_valid(self, goal_x, goal_y):
        if goal_x > ARENA_LENGTH/2 or goal_x < -ARENA_LENGTH/2 or goal_y > ARENA_WIDTH/2 or goal_y < -ARENA_WIDTH/2:
            return False
        for obstacle in self.obstacle_coordinates:
            if goal_x < obstacle[0][0] and goal_x > obstacle[2][0]:
                if goal_y < obstacle[0][1] and goal_y > obstacle[2][1]:
                    return False
        return True

    def generate_random_goal(self):
        self.prev_x = self.goal_x
        self.prev_y = self.goal_y
        tries = 0
        while (((abs(self.prev_x - self.goal_x) + abs(self.prev_y - self.goal_y)) < 4) or (not self.goal_is_valid(self.goal_x, self.goal_y))):
            self.goal_x = random.randrange(-25, 25) / 10.0
            self.goal_y = random.randrange(-25, 25) / 10.0
            tries += 1
            if tries > 200:
                print("ERROR: cannot find valid new goal, resestting!")
                self.delete_entity()
                self.reset_simulation()
                self.generate_goal_pose()
                break
        self.publish_callback()

    def generate_dynamic_goal_pose(self, robot_pose_x, robot_pose_y, radius):
        tries = 0
        while(True):
            ring_position = random.uniform(0, 1)
            origin = radius + numpy.random.normal(0, 0.1) # in meters
            goal_offset_x = math.cos(2 * math.pi * ring_position) * origin
            goal_offset_y = math.sin(2 * math.pi * ring_position) * origin
            goal_x = robot_pose_x + goal_offset_x
            goal_y = robot_pose_y + goal_offset_y
            if self.goal_is_valid(goal_x, goal_y):
                self.goal_x = goal_x
                self.goal_y = goal_y
                break
            if tries > 100:
                print("Error! couldn't find valid goal position, resetting..")
                self.delete_entity()
                self.reset_simulation()
                self.generate_goal_pose()
                return
            tries += 1
        self.publish_callback()


    def generate_goal_pose(self):
        self.prev_x = self.goal_x
        self.prev_y = self.goal_y
        tries = 0

        while ((abs(self.prev_x - self.goal_x) + abs(self.prev_y - self.goal_y)) < 2):
            if self.stage == 1:
                # --- Hallway Partial: Define static goal positions here ---
                goal_pose_list = [[5.0, 4.0], [2.5, 4.0], [0.0, 4.0], [5.0, 2.0], [2.5, 2.0], [0.0, 2.0],
                                  [5.0, 0.0], [2.5, 0.0], [0.0, 0.0], [5.0, -2.0], [2.5, -2.0], [0.0, -2.0],
                                  [5.0, -4.0], [2.5, -4.0], [0.0, -4.0], [5.0, -6.0], [2.5, -6.0], [0.0, -6.0],
                                  [4.0, -8.0], [2.5, -8.0], [0.0, -8.0], [-2.0, -4.0], [-4.0, -4.0], [-2.0, -6.0], 
                                  [-4.0, -6.0], [-2.0, -8.0], [-4.0, -8.0]]
                index = random.randrange(0, len(goal_pose_list))
                self.goal_x = float(goal_pose_list[index][0])
                self.goal_y = float(goal_pose_list[index][1])

            elif self.stage == 2:
                # --- Hallway Anywhere : Define static goal positions here ---
                goal_pose_list = [[15.0, 0.0], [15.0, -1.0], [15.0, 8.0],
                                  [17.5, 0.0], [17.5, 1.0], [17.5, -5.0],
                                  [20.0, 0.0], [20.0, 2.0], [20.0, 9.0],
                                  [20.0, -1.0], [20.0, -3.0], [20.0, -5.0], [20.0, -7.0],
                                  [22.5, 0.0], [22.5, 1.0], [22.5, 3.0], [22.5, 5.0], [22.5, 7.0], [22.5, 9.0],
                                  [22.5, -1.0], [22.5, -3.0], [22.5, -5.0], [22.5, -7.0],
                                  [25.0, 0.0], [25.0, 1.0], [25.0, 3.0], [25.0, 5.0], [25.0, 7.0], [25.0, 9.0],
                                  [25.0, -1.0], [25.0, -3.0], [25.0, -5.0], [25.0, -7.0],
                                  [30.0, 0.0], [30.0, 2.0], [30.0, -2.0],
                                  ]
                index = random.randrange(0, len(goal_pose_list))
                self.goal_x = float(goal_pose_list[index][0])
                self.goal_y = float(goal_pose_list[index][1])

            elif self.stage == 3:
                # --- Lobby Anywhere : Define static goal positions here ---
                goal_pose_list = [[0.0, 0.0], [3.0, 0.0], [5.0, 0.0], [7.0, 0.0], [-2.0, 0.0], [-4.0, 0.0], [-6.0, 0.0],
                                  [0.0, 3.0], [2.0, 3.0], [5.0, 3.0], [8.0, 3.0], [-2.0, 3.0], [-4.0, 3.0],
                                  [0.0, 6.0], [3.0, 6.0], [6.0, 6.0], [10.0, 6.0], [-2.0, 6.0], [-4.0, 6.0], [-7.0, 6.0],
                                  [0.0, 8.0], [3.0, 8.0], [6.0, 8.0], [10.0, 8.0], [-3.0, 8.0], [-6.0, 8.0], [-10.0, 8.0],
                                  [4.0, 10.0], [7.0, 10.0], [10.0, 10.0], [-4.0, 10.0], [-7.0, 10.0], [-10.0, 10.0],
                                  [-7.0, 12.0], [6.0, 12.0],
                                  [3.0, -2.0], [5.0, -2.0], [7.0, -2.0], [10.0, -2.0], [-3.0, -2.0], [-5.0, -2.0], [-7.0, -2.0],
                                  [0.0, -5.0], [3.0, -5.0], [6.0, -5.0], [10.0, -5.0], [13.0, -5.0], [-3.0, -5.0], [-5.0, -5.0], [-7.0, -5.0],
                                  [0.0, -8.0], [2.0, -8.0], [-2.0, -8.0],
                                  [1.0, -10.0], [-1.0, -10.0],
                                  [1.0, -11.0],
                                 ]
                index = random.randrange(0, len(goal_pose_list))
                self.goal_x = float(goal_pose_list[index][0])
                self.goal_y = float(goal_pose_list[index][1])

            else:
                # --- Define static goal positions here ---
                goal_pose_list = [[1.0, 0.0], [2.0, -1.5], [0.0, -2.0], [2.0, 2.0], [0.8, 2.0],
                                  [-1.9, 1.9], [-1.9,  0.2], [-1.9, -0.5], [-2.0, -2.0], [-0.5, -1.0],
                                  [1.5, -1.0], [-0.5, 1.0], [-1.0, -2.0], [1.8, -0.2], [1.0, -1.9]]
                index = random.randrange(0, len(goal_pose_list))
                self.goal_x = float(goal_pose_list[index][0])
                self.goal_y = float(goal_pose_list[index][1])
            tries += 1
            if tries > 100:
                print("ERROR: distance between goals is small!")
                break
        self.publish_callback()

    def reset_simulation(self):
        req = Empty.Request()
        while not self.reset_simulation_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('reset service not available, waiting again...')
        self.reset_simulation_client.call_async(req)

    def delete_entity(self):
        req = DeleteEntity.Request()
        req.name = self.entity_name
        while not self.delete_entity_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')
        self.delete_entity_client.call_async(req)

    def spawn_entity(self):
        goal_pose = Pose()
        goal_pose.position.x = self.goal_x
        goal_pose.position.y = self.goal_y
        req = SpawnEntity.Request()
        req.name = self.entity_name
        req.xml = self.entity
        req.initial_pose = goal_pose
        while not self.spawn_entity_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')
        self.spawn_entity_client.call_async(req)

    def get_obstacle_coordinates(self):
        # map에 맞게 변경할 필요가 있음
        tree = ET.parse(os.getenv('DRLNAV_BASE_PATH') + '/src/turtlebot3_simulations/turtlebot3_gazebo/models/turtlebot3_new_world/Lobby/model.sdf')
        root = tree.getroot()
        obstacle_coordinates = []
        for wall in root.find('model').findall('link'):
            pose = wall.find('pose').text.split(" ")
            size = wall.find('collision').find('geometry').find('box').find('size').text.split()
            rotation = float(pose[-1])
            pose_x = float(pose[0])
            pose_y = float(pose[1])
            if rotation == 0:
                size_x = float(size[0]) + NO_GOAL_SPAWN_MARGIN * 2
                size_y = float(size[1]) + NO_GOAL_SPAWN_MARGIN * 2
            else:
                size_x = float(size[1]) + NO_GOAL_SPAWN_MARGIN * 2
                size_y = float(size[0]) + NO_GOAL_SPAWN_MARGIN * 2
            point_1 = [pose_x + size_x / 2, pose_y + size_y / 2]
            point_2 = [point_1[0], point_1[1] - size_y]
            point_3 = [point_1[0] - size_x, point_1[1] - size_y ]
            point_4 = [point_1[0] - size_x, point_1[1] ]
            wall_points = [point_1, point_2, point_3, point_4]
            obstacle_coordinates.append(wall_points)
        return obstacle_coordinates


def main():
    rclpy.init()
    drl_gazebo = DRLGazebo()
    rclpy.spin(drl_gazebo)

    drl_gazebo.destroy()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
