# traffic_light_controller.py
import pygame
from config import *

class TrafficLightController:
    VALID_VEHICLE_PHASES = ["green", "yellow", "red"]
    VALID_PEDESTRIAN_PHASES = ["dont_walk", "walk", "flash"] # flash 是指 "请勿通行" 开始闪烁

    def __init__(self):
        self.vehicle_phase = "green"
        self.pedestrian_phase = "dont_walk"
        
        self.current_phase_timer = MIN_VEHICLE_GREEN_TIME # 当前相位已持续时间或剩余时间
        self.is_pedestrian_request_servicing = False # 是否正在服务一个行人请求

    def update(self, rsu_pedestrian_request_priority):
        """
        更新交通灯状态。
        rsu_pedestrian_request_priority: 0 (无), 1 (中), 2 (高)
        """
        self.current_phase_timer -= 1

        # --- 车辆绿灯阶段 ---
        if self.vehicle_phase == "green":
            # 条件1: 最小绿灯时间已到
            # 条件2: 有行人请求 (高或中优先级) 且当前未服务行人请求
            if self.current_phase_timer <= 0 and \
               rsu_pedestrian_request_priority > 0 and \
               not self.is_pedestrian_request_servicing:
                self._transition_to_vehicle_yellow()
            elif self.current_phase_timer < - (MIN_VEHICLE_GREEN_TIME // 2): # 如果空闲过久，重置绿灯计时器
                self.current_phase_timer = MIN_VEHICLE_GREEN_TIME


        # --- 车辆黄灯阶段 ---
        elif self.vehicle_phase == "yellow":
            if self.current_phase_timer <= 0:
                self._transition_to_all_red_before_ped_walk()
        
        # --- 全红阶段 (车辆红灯，准备行人通行) ---
        elif self.vehicle_phase == "red" and self.pedestrian_phase == "dont_walk" and self.is_pedestrian_request_servicing:
            if self.current_phase_timer <= 0: # 全红结束
                self._transition_to_pedestrian_walk()

        # --- 行人通行 (Walk) 阶段 ---
        elif self.pedestrian_phase == "walk":
            if self.current_phase_timer <= 0:
                self._transition_to_pedestrian_flash()

        # --- 行人闪烁 (Flash "Don't Walk") 阶段 ---
        elif self.pedestrian_phase == "flash":
            if self.current_phase_timer <= 0:
                self._transition_to_all_red_before_vehicle_green()
        
        # --- 全红阶段 (行人结束，准备车辆通行) ---
        elif self.vehicle_phase == "red" and self.pedestrian_phase == "dont_walk" and not self.is_pedestrian_request_servicing:
             if self.current_phase_timer <= 0:
                  self._transition_to_vehicle_green()


    def _transition_to_vehicle_yellow(self):
        self.vehicle_phase = "yellow"
        self.current_phase_timer = VEHICLE_YELLOW_TIME
        self.is_pedestrian_request_servicing = True # 标记开始服务一个请求周期
        print("TLC: V:Green -> V:Yellow (Ped request pending)")

    def _transition_to_all_red_before_ped_walk(self):
        self.vehicle_phase = "red"
        # self.pedestrian_phase 保持 "dont_walk"
        self.current_phase_timer = ALL_RED_TIME
        print("TLC: V:Yellow -> V:Red (All Red before Ped Walk)")

    def _transition_to_pedestrian_walk(self):
        self.pedestrian_phase = "walk"
        self.current_phase_timer = PEDESTRIAN_WALK_TIME
        print("TLC: P:Dont_Walk -> P:Walk")

    def _transition_to_pedestrian_flash(self):
        self.pedestrian_phase = "flash"
        self.current_phase_timer = PEDESTRIAN_FLASH_TIME
        print("TLC: P:Walk -> P:Flash (Dont Walk Flashing)")

    def _transition_to_all_red_before_vehicle_green(self):
        self.pedestrian_phase = "dont_walk"
        # self.vehicle_phase 保持 "red"
        self.current_phase_timer = ALL_RED_TIME
        self.is_pedestrian_request_servicing = False # 行人服务周期结束
        print("TLC: P:Flash -> P:Dont_Walk (All Red before Vehicle Green)")
    
    def _transition_to_vehicle_green(self):
        self.vehicle_phase = "green"
        self.current_phase_timer = MIN_VEHICLE_GREEN_TIME
        print("TLC: V:Red -> V:Green")


    def get_signal_display_info(self):
        v_light_colors = {"red": DARK_GREY, "yellow": DARK_GREY, "green": DARK_GREY}
        if self.vehicle_phase == "green": v_light_colors["green"] = GREEN
        elif self.vehicle_phase == "yellow": v_light_colors["yellow"] = YELLOW
        elif self.vehicle_phase == "red": v_light_colors["red"] = RED
        
        p_display_text = "DONT WALK"
        p_text_color = RED
        if self.pedestrian_phase == "walk":
            p_display_text = "WALK"
            p_text_color = GREEN
        elif self.pedestrian_phase == "flash":
            p_display_text = "DONT WALK"
            # 闪烁效果 (每半秒切换颜色)
            if (pygame.time.get_ticks() // 500) % 2 == 0:
                p_text_color = RED
            else:
                p_text_color = DARK_GREY # 或 ORANGE
        
        return v_light_colors, p_display_text, p_text_color

    def draw(self, screen):
        v_colors, p_text, p_color = self.get_signal_display_info()
        
        # 绘制车辆信号灯 (示例位置)
        v_light_base_x = V_ROAD_RECT.left - 30
        v_light_base_y = INTERSECTION_CENTER_Y
        pygame.draw.circle(screen, v_colors["red"], (v_light_base_x, v_light_base_y - 30), 12)
        pygame.draw.circle(screen, v_colors["yellow"], (v_light_base_x, v_light_base_y), 12)
        pygame.draw.circle(screen, v_colors["green"], (v_light_base_x, v_light_base_y + 30), 12)

        # 绘制行人信号文本 (示例位置)
        p_font = pygame.font.Font(DEFAULT_FONT_NAME, FONT_SIZE_MEDIUM)
        p_surface = p_font.render(p_text, True, p_color)
        p_rect = p_surface.get_rect(center=(V_ROAD_RECT.right + 50, INTERSECTION_CENTER_Y - 50))
        pygame.draw.rect(screen, BLACK, p_rect.inflate(10,5)) # 背景框
        screen.blit(p_surface, p_rect)