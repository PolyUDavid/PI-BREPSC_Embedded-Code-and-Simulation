# pedestrian_simulator.py
import pygame
import random
import math
from collections import deque # 用于高效地实现固定大小的历史记录
from config import *

class Pedestrian:
    def __init__(self, id_num, start_pos, color=BLUE, target_wait_area_key=None):
        self.id = f"P{id_num}"
        self.pos = list(start_pos)
        self.radius = PEDESTRIAN_RADIUS
        self.color = color
        self.initial_color = color # 保存初始颜色

        self.path = deque() # 存储 (x,y) 目标点
        self.current_velocity = [0,0] # 当前速度向量 [vx, vy] in pixels/frame

        # 运动状态相关
        self.position_history = deque(maxlen=PEDESTRIAN_HISTORY_SIZE) # 存储最近的位置
        self.frames_stationary = 0
        self.motion_state = "moving"  # "moving", "stationary_short", "stationary_long"

        # 交互与意图
        self.is_requesting_button_press = False # 是否模拟按钮按下
        self.is_malicious = False # 是否为恶意行为者

        # BLE 相关 (由 RSU 模拟接收，这里仅作为属性)
        self.ble_tx_power = DEFAULT_TX_POWER_DBM

        # 目标等待区域 (用于脚本化行为)
        self.target_wait_area_key = target_wait_area_key # e.g., "WAIT_AREA_WEST"
        self.is_at_wait_area = False

    def set_path_to_point(self, target_pos):
        """设置单个目标点，清除现有路径"""
        self.path.clear()
        self.path.append(target_pos)
        self._calculate_velocity_to_next_target()

    def add_point_to_path(self, target_pos):
        """向路径末尾添加一个目标点"""
        self.path.append(target_pos)
        if not self.current_velocity[0] and not self.current_velocity[1] and len(self.path) == 1:
             self._calculate_velocity_to_next_target() # 如果当前静止且这是第一个点

    def _calculate_velocity_to_next_target(self):
        if not self.path:
            self.current_velocity = [0, 0]
            return

        target_x, target_y = self.path[0] # 查看路径中的下一个目标
        dx = target_x - self.pos[0]
        dy = target_y - self.pos[1]
        distance_to_target = math.sqrt(dx**2 + dy**2)

        if distance_to_target < PEDESTRIAN_SPEED_PIXELS_PER_FRAME: # 已接近或到达目标
            self.pos[0] = target_x # 直接移动到目标点
            self.pos[1] = target_y
            self.path.popleft() # 移除已达到的目标点
            if not self.path: # 路径已空
                self.current_velocity = [0, 0]
                return
            else: # 计算到下一个目标点的速度
                self._calculate_velocity_to_next_target()
                return

        # 标准化速度向量并乘以速度
        self.current_velocity = [
            (dx / distance_to_target) * PEDESTRIAN_SPEED_PIXELS_PER_FRAME if distance_to_target != 0 else 0,
            (dy / distance_to_target) * PEDESTRIAN_SPEED_PIXELS_PER_FRAME if distance_to_target != 0 else 0
        ]

    def update(self):
        """更新行人位置和运动状态"""
        if self.path:
            self._calculate_velocity_to_next_target() # 确保速度指向当前路径目标

        self.pos[0] += self.current_velocity[0]
        self.pos[1] += self.current_velocity[1]

        # 更新位置历史
        self.position_history.append(tuple(self.pos))
        self._update_motion_state()

        # 检查是否在目标等待区域 (如果已定义)
        if self.target_wait_area_key:
            wait_area_rect = None
            if self.target_wait_area_key == "WAIT_AREA_WEST": wait_area_rect = pygame.Rect(WAIT_AREA_WEST)
            elif self.target_wait_area_key == "WAIT_AREA_EAST": wait_area_rect = pygame.Rect(WAIT_AREA_EAST)
            
            if wait_area_rect:
                ped_rect = pygame.Rect(self.pos[0]-self.radius, self.pos[1]-self.radius, self.radius*2, self.radius*2)
                self.is_at_wait_area = wait_area_rect.contains(ped_rect) # 完全在区域内


    def _update_motion_state(self):
        if len(self.position_history) < PEDESTRIAN_HISTORY_SIZE // 2: # 历史数据不足
            self.motion_state = "moving"
            self.frames_stationary = 0
            return

        # 计算最近一段时间内的总位移
        start_pos = self.position_history[0]
        current_pos = self.position_history[-1]
        displacement = math.sqrt((current_pos[0] - start_pos[0])**2 + (current_pos[1] - start_pos[1])**2)

        # 如果位移很小，则认为静止
        if displacement < self.radius: # 小于自身半径的移动视为静止
            self.frames_stationary += 1
        else:
            self.frames_stationary = 0
            self.motion_state = "moving" # 只要有显著移动就重置为 moving

        if self.frames_stationary >= STATIONARY_FRAMES_LONG:
            self.motion_state = "stationary_long"
        elif self.frames_stationary >= STATIONARY_FRAMES_SHORT:
            self.motion_state = "stationary_short"
        # else: motion_state 保持 "moving" 或之前的静止状态直到移动

    def get_current_speed_mps(self):
        """返回当前速度 (米/秒) - 用于运动学一致性检查"""
        speed_pixels_per_frame = math.sqrt(self.current_velocity[0]**2 + self.current_velocity[1]**2)
        speed_pixels_per_sec = speed_pixels_per_frame * FPS
        speed_meters_per_sec = speed_pixels_per_sec / PIXELS_PER_METER
        return speed_meters_per_sec

    def draw(self, screen, rsu_ped_data=None):
        # 头部
        head_radius = self.radius
        head_center = (int(self.pos[0]), int(self.pos[1]) - head_radius)
        pygame.draw.circle(screen, (255, 220, 180), head_center, head_radius)
        # 身体
        body_start = (int(self.pos[0]), int(self.pos[1]) - head_radius + 2)
        body_end = (int(self.pos[0]), int(self.pos[1]) + head_radius + 4)
        pygame.draw.line(screen, self.color, body_start, body_end, 3)
        # 手
        hand_y = int(self.pos[1]) - head_radius + 8
        pygame.draw.line(screen, self.color, (int(self.pos[0])-head_radius, hand_y), (int(self.pos[0])+head_radius, hand_y), 2)
        # 腿
        leg_y = int(self.pos[1]) + head_radius + 4
        pygame.draw.line(screen, self.color, body_end, (int(self.pos[0])-head_radius//2, leg_y+head_radius), 2)
        pygame.draw.line(screen, self.color, body_end, (int(self.pos[0])+head_radius//2, leg_y+head_radius), 2)
        # 恶意/异常/状态颜色叠加
        draw_color = self.initial_color
        if self.is_malicious:
            draw_color = RED
        elif rsu_ped_data and rsu_ped_data.get("is_anomalous"):
            draw_color = ORANGE
        elif self.motion_state == "stationary_long":
            draw_color = YELLOW
        elif self.motion_state == "stationary_short":
            draw_color = (200, 200, 0)
        # 头部外圈状态色
        pygame.draw.circle(screen, draw_color, head_center, head_radius, 2)
        # 按钮标记
        if self.is_requesting_button_press:
            pygame.draw.circle(screen, GREEN, head_center, head_radius + 3, 2)
        # 显示ID
        font_small = pygame.font.Font(DEFAULT_FONT_NAME, FONT_SIZE_SMALL)
        id_text = font_small.render(self.id, True, BLACK)
        screen.blit(id_text, (self.pos[0] - self.radius, self.pos[1] - self.radius - 25))