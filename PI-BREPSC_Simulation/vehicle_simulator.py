import pygame
import random
from config import *

class Vehicle:
    def __init__(self, id, start_pos, speed, direction):
        self.id = id
        self.pos = list(start_pos)
        self.speed = speed
        self.direction = direction # "horizontal" or "vertical"
        # Use a fixed color palette for vehicle ids
        vehicle_color_map = {
            'V1': (68, 170, 255),   # Blue
            'V2': (255, 85, 85),    # Red
            'V3': (255, 221, 85),   # Yellow
            'V4': (85, 255, 170),   # Green
            'V5': (170, 85, 255),   # Purple
        }
        self.color = vehicle_color_map.get(self.id, (120, 120, 120))
        self.width = 28  # 更窄
        self.height = 56 # 更长，纵向

    def update_position(self):
        if self.direction == "horizontal":
            self.pos[0] += self.speed
            # Loop vehicle around the screen
            if self.pos[0] > SCREEN_WIDTH:
                self.pos[0] = -self.width
        else:
            self.pos[1] += self.speed
            # Loop vehicle around the screen
            if self.pos[1] > SCREEN_HEIGHT:
                self.pos[1] = -self.height

    def draw(self, screen):
        # 车身
        car_rect = pygame.Rect(int(self.pos[0]), int(self.pos[1]), self.width, self.height)
        pygame.draw.rect(screen, self.color, car_rect, border_radius=8)
        # 车头（椭圆）
        head_rect = pygame.Rect(int(self.pos[0]), int(self.pos[1]), self.width, self.width//2)
        pygame.draw.ellipse(screen, (200,200,200), head_rect)
        # 车窗
        window_rect = pygame.Rect(int(self.pos[0])+self.width//4, int(self.pos[1])+self.height//6, self.width//2, self.height//4)
        pygame.draw.rect(screen, (180,220,255), window_rect, border_radius=4)
        # 轮廓线
        pygame.draw.rect(screen, (60,60,60), car_rect, 2, border_radius=8)