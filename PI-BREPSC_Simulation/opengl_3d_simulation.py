#!/usr/bin/env python3
"""
OpenGL 3D Traffic Simulation using Pygame + OpenGL
High-performance rendering with built-in Python libraries
"""

import pygame
import json
import os
import time
import math
import threading
import requests  # 新增
from pygame.locals import *

try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
    OPENGL_AVAILABLE = True
    print("✅ OpenGL available")
except ImportError:
    print("❌ OpenGL not available. Install with: pip install PyOpenGL")
    OPENGL_AVAILABLE = False

class OpenGL3DSimulation:
    """High-quality OpenGL 3D traffic simulation"""
    
    def __init__(self):
        if not OPENGL_AVAILABLE:
            raise ImportError("OpenGL not available")
        
        # Initialize pygame and OpenGL
        pygame.init()
        self.width, self.height = 1200, 800
        self.screen = pygame.display.set_mode((self.width, self.height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("PI-BREPSC 3D Traffic Simulation - OpenGL")
        
        # Camera settings
        self.camera_distance = 50
        self.camera_angle_x = 30
        self.camera_angle_y = 45
        self.mouse_pressed = False
        self.last_mouse_pos = (0, 0)
        
        # Simulation data
        self.sync_file = "3d_sync_data.json"
        self.running = False
        
        # Setup OpenGL
        self._setup_opengl()
        self._setup_lighting()
    
    def _setup_opengl(self):
        """Configure OpenGL settings"""
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # Set up perspective
        glMatrixMode(GL_PROJECTION)
        gluPerspective(45, (self.width / self.height), 0.1, 1000.0)
        glMatrixMode(GL_MODELVIEW)
        
        # Background color (sky blue)
        glClearColor(0.5, 0.8, 1.0, 1.0)
    
    def _setup_lighting(self):
        """Setup realistic lighting"""
        # Ambient light
        ambient = [0.3, 0.3, 0.3, 1.0]
        glLightfv(GL_LIGHT0, GL_AMBIENT, ambient)
        
        # Diffuse light (sun)
        diffuse = [1.0, 1.0, 0.9, 1.0]
        glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse)
        
        # Light position (sun)
        position = [50.0, 100.0, 50.0, 1.0]
        glLightfv(GL_LIGHT0, GL_POSITION, position)
    
    def _set_camera(self):
        """Set camera position and orientation"""
        glLoadIdentity()
        
        # Calculate camera position
        cam_x = self.camera_distance * math.cos(math.radians(self.camera_angle_y)) * math.cos(math.radians(self.camera_angle_x))
        cam_y = self.camera_distance * math.sin(math.radians(self.camera_angle_x))
        cam_z = self.camera_distance * math.sin(math.radians(self.camera_angle_y)) * math.cos(math.radians(self.camera_angle_x))
        
        gluLookAt(cam_x, cam_y, cam_z,  # Camera position
                  0, 0, 0,              # Look at center
                  0, 1, 0)              # Up vector
    
    def _draw_ground(self):
        """Draw ground plane"""
        glColor3f(0.4, 0.8, 0.4)  # Green grass
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0)
        glVertex3f(-100, -0.1, -100)
        glVertex3f(100, -0.1, -100)
        glVertex3f(100, -0.1, 100)
        glVertex3f(-100, -0.1, 100)
        glEnd()
    
    def _draw_road(self):
        """Draw road surfaces"""
        glColor3f(0.2, 0.2, 0.2)  # Dark gray
        
        # Horizontal road
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0)
        glVertex3f(-50, 0, -10)
        glVertex3f(50, 0, -10)
        glVertex3f(50, 0, 10)
        glVertex3f(-50, 0, 10)
        glEnd()
        
        # Vertical road
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0)
        glVertex3f(-10, 0, -50)
        glVertex3f(10, 0, -50)
        glVertex3f(10, 0, 50)
        glVertex3f(-10, 0, 50)
        glEnd()
    
    def _draw_crosswalk(self):
        """Draw zebra crossing"""
        glColor3f(1.0, 1.0, 1.0)  # White
        
        # Zebra stripes
        for i in range(-8, 9, 2):
            glBegin(GL_QUADS)
            glNormal3f(0, 1, 0)
            glVertex3f(i, 0.01, -10)
            glVertex3f(i + 1, 0.01, -10)
            glVertex3f(i + 1, 0.01, 10)
            glVertex3f(i, 0.01, 10)
            glEnd()
    
    def _draw_buildings(self):
        """Draw surrounding buildings"""
        buildings = [
            (-30, 20, -30, 0.6, 0.6, 0.6),  # x, height, z, r, g, b
            (30, 25, -30, 0.7, 0.7, 0.7),
            (-30, 15, 30, 0.8, 0.8, 0.8),
            (30, 30, 30, 0.5, 0.5, 0.5)
        ]
        
        for x, height, z, r, g, b in buildings:
            glColor3f(r, g, b)
            self._draw_cube(x, height/2, z, 12, height, 12)
    
    def _draw_cube(self, x, y, z, width, height, depth):
        """Draw a cube at specified position and size"""
        glPushMatrix()
        glTranslatef(x, y, z)
        glScalef(width, height, depth)
        
        # Define cube vertices
        vertices = [
            [-0.5, -0.5, -0.5], [0.5, -0.5, -0.5], [0.5, 0.5, -0.5], [-0.5, 0.5, -0.5],  # Back
            [-0.5, -0.5, 0.5], [0.5, -0.5, 0.5], [0.5, 0.5, 0.5], [-0.5, 0.5, 0.5]       # Front
        ]
        
        faces = [
            [0, 1, 2, 3], [4, 7, 6, 5], [0, 4, 5, 1],  # Back, Front, Bottom
            [2, 6, 7, 3], [0, 3, 7, 4], [1, 5, 6, 2]   # Top, Left, Right
        ]
        
        normals = [
            [0, 0, -1], [0, 0, 1], [0, -1, 0],
            [0, 1, 0], [-1, 0, 0], [1, 0, 0]
        ]
        
        glBegin(GL_QUADS)
        for i, face in enumerate(faces):
            glNormal3fv(normals[i])
            for vertex in face:
                glVertex3fv(vertices[vertex])
        glEnd()
        
        glPopMatrix()
    
    def _draw_sphere(self, x, y, z, radius):
        """Draw a sphere at specified position"""
        glPushMatrix()
        glTranslatef(x, y, z)
        
        # Simple sphere using quad strips
        slices = 16
        stacks = 16
        
        for i in range(stacks):
            lat0 = math.pi * (-0.5 + float(i) / stacks)
            z0 = radius * math.sin(lat0)
            zr0 = radius * math.cos(lat0)
            
            lat1 = math.pi * (-0.5 + float(i + 1) / stacks)
            z1 = radius * math.sin(lat1)
            zr1 = radius * math.cos(lat1)
            
            glBegin(GL_QUAD_STRIP)
            for j in range(slices + 1):
                lng = 2 * math.pi * float(j) / slices
                x_pos = math.cos(lng)
                y_pos = math.sin(lng)
                
                glNormal3f(x_pos * zr0, y_pos * zr0, z0)
                glVertex3f(x_pos * zr0, z0, y_pos * zr0)
                
                glNormal3f(x_pos * zr1, y_pos * zr1, z1)
                glVertex3f(x_pos * zr1, z1, y_pos * zr1)
            glEnd()
        
        glPopMatrix()
    
    def _draw_traffic_lights(self):
        """Draw traffic light poles and lights"""
        positions = [(15, 15), (-15, 15), (15, -15), (-15, -15)]
        
        for x, z in positions:
            # Pole
            glColor3f(0.3, 0.3, 0.3)
            self._draw_cube(x, 4, z, 0.5, 8, 0.5)
            
            # Light housing
            glColor3f(0.1, 0.1, 0.1)
            self._draw_cube(x, 7, z, 2, 1, 6)
            
            # Individual lights (red, yellow, green)
            colors = [(1.0, 0.0, 0.0), (1.0, 1.0, 0.0), (0.0, 1.0, 0.0)]
            for i, color in enumerate(colors):
                glColor3fv(color)
                self._draw_sphere(x, 7, z - 1.5 + i, 0.3)
    
    def _draw_pedestrian(self, x, y, intent_prob):
        """Draw a pedestrian figure"""
        # Scale coordinates
        x, y = x / 10, y / 10
        
        # Color based on intent
        if intent_prob > 0.7:
            glColor3f(1.0, 0.2, 0.2)  # Red - high intent
        elif intent_prob > 0.4:
            glColor3f(1.0, 0.8, 0.0)  # Yellow - medium intent
        else:
            glColor3f(0.2, 1.0, 0.2)  # Green - low intent
        
        # Body (cylinder approximation)
        self._draw_cube(x, 1, y, 0.6, 1.5, 0.4)
        
        # Head
        glColor3f(1.0, 0.8, 0.6)  # Skin color
        self._draw_sphere(x, 2, y, 0.3)
    
    def _draw_vehicle(self, x, y):
        """Draw a vehicle"""
        # Scale coordinates
        x, y = x / 10, y / 10
        
        # Car body
        glColor3f(0.2, 0.4, 0.8)  # Blue
        self._draw_cube(x, 1, y, 4, 1.5, 2)
        
        # Wheels
        glColor3f(0.1, 0.1, 0.1)  # Black
        wheel_positions = [(-1.5, 1), (1.5, 1), (-1.5, -1), (1.5, -1)]
        for wx, wy in wheel_positions:
            self._draw_sphere(x + wx, 0.3, y + wy, 0.4)
    
    def load_simulation_data(self):
        """Load current simulation data"""
        try:
            if os.path.exists(self.sync_file):
                with open(self.sync_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading data: {e}")
        return {}
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key in (pygame.K_s, pygame.K_d):
                    # S/D键触发行人按钮
                    threading.Thread(target=self.send_pedestrian_button).start()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    self.mouse_pressed = True
                    self.last_mouse_pos = pygame.mouse.get_pos()
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_pressed = False
            elif event.type == pygame.MOUSEMOTION:
                if self.mouse_pressed:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    dx = mouse_x - self.last_mouse_pos[0]
                    dy = mouse_y - self.last_mouse_pos[1]
                    self.camera_angle_y += dx * 0.5
                    self.camera_angle_x += dy * 0.5
                    self.camera_angle_x = max(-89, min(89, self.camera_angle_x))
                    self.last_mouse_pos = (mouse_x, mouse_y)
            elif event.type == pygame.MOUSEWHEEL:
                self.camera_distance += event.y * -2
                self.camera_distance = max(10, min(100, self.camera_distance))
        return True

    def send_pedestrian_button(self):
        """向本地API发送行人按钮请求"""
        try:
            requests.post("http://localhost:8000/api/pedestrian_button", timeout=1)
        except Exception as e:
            print(f"[API] Pedestrian button error: {e}")

    def render_frame(self):
        """Render a single frame"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self._set_camera()
        # Draw static environment
        self._draw_ground()
        self._draw_road()
        self._draw_crosswalk()
        self._draw_buildings()
        self._draw_traffic_lights()
        # Load and draw dynamic objects
        data = self.load_simulation_data()
        # Draw pedestrians
        if 'pedestrians' in data:
            for ped in data['pedestrians']:
                self._draw_pedestrian(ped['x'], ped['y'], ped.get('intent_prob', 0.5))
        # Draw vehicles
        if 'vehicles' in data:
            for vehicle in data['vehicles']:
                self._draw_vehicle(vehicle['x'], vehicle['y'])
        # --- 信息面板 ---
        self.draw_info_panel(data)
        pygame.display.flip()

    def draw_info_panel(self, data):
        """在左上角绘制信息面板"""
        font = pygame.font.SysFont('Arial', 20)
        lines = []
        # 行人
        if 'pedestrians' in data:
            lines.append(f"🚶 Pedestrians: {len(data['pedestrians'])}")
            for p in data['pedestrians']:
                lines.append(f"  {p.get('id','?')}: ({p.get('x','?'):.1f},{p.get('y','?'):.1f})  优先级:{p.get('priority','-')}  BLE:{'Y' if p.get('has_wearable_device') else 'N'}")
        # 车辆
        if 'vehicles' in data:
            lines.append(f"🚗 Vehicles: {len(data['vehicles'])}")
            for v in data['vehicles']:
                lines.append(f"  {v.get('id','?')}: ({v.get('x','?'):.1f},{v.get('y','?'):.1f})  速度:{v.get('speed','?')}")
        # 信号灯
        if 'traffic_lights' in data:
            lines.append(f"🚦 Traffic Light: {data['traffic_lights']}")
        if 'pedestrian_lights' in data:
            lines.append(f"🚶‍♂️ Pedestrian Light: {data['pedestrian_lights']}")
        # AI决策
        if 'ai_decisions' in data:
            ai = data['ai_decisions']
            lines.append(f"🧠 AI: 高优先:{ai.get('high_priority_count',0)}  中优先:{ai.get('medium_priority_count',0)}")
        # 系统
        if 'timestamp' in data:
            lines.append(f"⏰ {data['timestamp']}")
        # 绘制
        y = 10
        for line in lines:
            surf = font.render(line, True, (0,0,0), (255,255,255))
            self.screen.blit(surf, (10, y))
            y += 24

    def run(self):
        """Main simulation loop"""
        self.running = True
        clock = pygame.time.Clock()
        
        print("🎮 OpenGL 3D Simulation Controls:")
        print("   🖱️  Left mouse + drag: Rotate camera")
        print("   🖜  Mouse wheel: Zoom in/out")
        print("   ⌨️  ESC: Exit")
        
        while self.running:
            if not self.handle_events():
                break
            
            self.render_frame()
            clock.tick(60)  # 60 FPS
        
        pygame.quit()

def main():
    """Main function"""
    if not OPENGL_AVAILABLE:
        print("❌ OpenGL not available. Please install PyOpenGL:")
        print("   pip install PyOpenGL PyOpenGL_accelerate")
        return
    
    print("🎯 Starting OpenGL 3D Traffic Simulation...")
    
    try:
        sim = OpenGL3DSimulation()
        sim.run()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 