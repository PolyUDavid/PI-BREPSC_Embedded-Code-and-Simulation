#!/usr/bin/env python3
"""
3D Simulation Module using PyVista
Beautiful 3D visualization for pedestrian crossing simulation
"""

import pyvista as pv
import numpy as np
import time
import threading
import json
import os
from dataclasses import dataclass
from typing import List, Tuple, Dict
import random

@dataclass
class Pedestrian3D:
    """3D Pedestrian representation"""
    id: str
    position: np.ndarray
    target: np.ndarray
    speed: float
    intent_prob: float
    is_crossing: bool
    color: Tuple[float, float, float]
    mesh: pv.PolyData = None

@dataclass
class Vehicle3D:
    """3D Vehicle representation"""
    id: str
    position: np.ndarray
    direction: np.ndarray
    speed: float
    mesh: pv.PolyData = None

class TrafficLight3D:
    """3D Traffic Light representation"""
    def __init__(self, position: np.ndarray, light_type: str):
        self.position = position
        self.light_type = light_type  # 'vehicle' or 'pedestrian'
        self.state = 'red'
        self.mesh = None
        self.light_mesh = None

class Beautiful3DSimulation:
    """
    Beautiful 3D Traffic Simulation using PyVista
    Provides enhanced visualization for the main simulation
    """
    
    def __init__(self):
        # PyVista plotter setup
        self.plotter = pv.Plotter(title="PI-BREPSC 3D Traffic Simulation")
        self.plotter.set_background('lightblue')
        
        # Scene dimensions
        self.scene_width = 50
        self.scene_height = 50
        self.road_width = 8
        self.crosswalk_width = 4
        
        # Simulation objects
        self.pedestrians: List[Pedestrian3D] = []
        self.vehicles: List[Vehicle3D] = []
        self.traffic_lights: List[TrafficLight3D] = []
        
        # Animation control
        self.running = False
        self.animation_thread = None
        
        # Data sync with main simulation
        self.sync_file = "3d_sync_data.json"
        
        # Initialize scene
        self._setup_environment()
        self._setup_roads()
        self._setup_traffic_lights()
        self._setup_lighting()
        
    def _setup_environment(self):
        """Setup the 3D environment - ground, buildings, etc."""
        # Ground plane
        ground = pv.Plane(center=(0, 0, -0.1), 
                         direction=(0, 0, 1), 
                         i_size=self.scene_width, 
                         j_size=self.scene_height)
        ground.texture_map_to_plane(inplace=True)
        self.plotter.add_mesh(ground, color='lightgray', opacity=0.8)
        
        # Buildings around the intersection
        building_positions = [
            (-20, -20, 0), (20, -20, 0), (-20, 20, 0), (20, 20, 0)
        ]
        
        for i, pos in enumerate(building_positions):
            height = random.uniform(15, 25)
            building = pv.Cube(center=(pos[0], pos[1], height/2),
                              x_length=15, y_length=15, z_length=height)
            color = ['lightcoral', 'lightsteelblue', 'lightgreen', 'lightyellow'][i]
            self.plotter.add_mesh(building, color=color, opacity=0.7)
    
    def _setup_roads(self):
        """Setup road infrastructure"""
        # Main horizontal road
        road_h = pv.Cube(center=(0, 0, 0.05),
                        x_length=self.scene_width, 
                        y_length=self.road_width, 
                        z_length=0.1)
        self.plotter.add_mesh(road_h, color='dimgray')
        
        # Main vertical road
        road_v = pv.Cube(center=(0, 0, 0.05),
                        x_length=self.road_width, 
                        y_length=self.scene_height, 
                        z_length=0.1)
        self.plotter.add_mesh(road_v, color='dimgray')
        
        # Crosswalks
        crosswalk_positions = [
            (0, self.road_width/2 + self.crosswalk_width/2, 0.06),  # North crosswalk
            (0, -self.road_width/2 - self.crosswalk_width/2, 0.06), # South crosswalk
            (self.road_width/2 + self.crosswalk_width/2, 0, 0.06),  # East crosswalk
            (-self.road_width/2 - self.crosswalk_width/2, 0, 0.06)  # West crosswalk
        ]
        
        for pos in crosswalk_positions[:2]:  # Horizontal crosswalks
            crosswalk = pv.Cube(center=pos,
                               x_length=self.road_width,
                               y_length=self.crosswalk_width,
                               z_length=0.02)
            self.plotter.add_mesh(crosswalk, color='white', opacity=0.8)
            
        for pos in crosswalk_positions[2:]:  # Vertical crosswalks
            crosswalk = pv.Cube(center=pos,
                               x_length=self.crosswalk_width,
                               y_length=self.road_width,
                               z_length=0.02)
            self.plotter.add_mesh(crosswalk, color='white', opacity=0.8)
        
        # Crosswalk stripes
        self._add_crosswalk_stripes()
    
    def _add_crosswalk_stripes(self):
        """Add zebra crossing stripes"""
        stripe_width = 0.5
        stripe_spacing = 1.0
        
        # Horizontal crosswalk stripes
        for y_pos in [self.road_width/2 + self.crosswalk_width/2, 
                      -self.road_width/2 - self.crosswalk_width/2]:
            for x in np.arange(-self.road_width/2, self.road_width/2, stripe_spacing):
                stripe = pv.Cube(center=(x, y_pos, 0.07),
                               x_length=stripe_width,
                               y_length=self.crosswalk_width,
                               z_length=0.01)
                self.plotter.add_mesh(stripe, color='white')
        
        # Vertical crosswalk stripes
        for x_pos in [self.road_width/2 + self.crosswalk_width/2,
                      -self.road_width/2 - self.crosswalk_width/2]:
            for y in np.arange(-self.road_width/2, self.road_width/2, stripe_spacing):
                stripe = pv.Cube(center=(x_pos, y, 0.07),
                               x_length=self.crosswalk_width,
                               y_length=stripe_width,
                               z_length=0.01)
                self.plotter.add_mesh(stripe, color='white')
    
    def _setup_traffic_lights(self):
        """Setup 3D traffic lights"""
        # Traffic light positions
        light_positions = [
            (self.road_width/2 + 2, self.road_width/2 + 2, 0),     # NE vehicle
            (-self.road_width/2 - 2, self.road_width/2 + 2, 0),    # NW vehicle
            (self.road_width/2 + 2, -self.road_width/2 - 2, 0),    # SE vehicle
            (-self.road_width/2 - 2, -self.road_width/2 - 2, 0),   # SW vehicle
        ]
        
        for pos in light_positions:
            traffic_light = TrafficLight3D(np.array(pos), 'vehicle')
            self._create_traffic_light_mesh(traffic_light)
            self.traffic_lights.append(traffic_light)
        
        # Pedestrian signal positions
        ped_positions = [
            (0, self.road_width/2 + self.crosswalk_width + 1, 0),   # North ped
            (0, -self.road_width/2 - self.crosswalk_width - 1, 0),  # South ped
            (self.road_width/2 + self.crosswalk_width + 1, 0, 0),   # East ped
            (-self.road_width/2 - self.crosswalk_width - 1, 0, 0),  # West ped
        ]
        
        for pos in ped_positions:
            ped_light = TrafficLight3D(np.array(pos), 'pedestrian')
            self._create_pedestrian_signal_mesh(ped_light)
            self.traffic_lights.append(ped_light)
    
    def _create_traffic_light_mesh(self, traffic_light: TrafficLight3D):
        """Create 3D mesh for vehicle traffic light"""
        # Pole
        pole = pv.Cylinder(center=(traffic_light.position[0], 
                                  traffic_light.position[1], 
                                  2.5),
                          direction=(0, 0, 1),
                          radius=0.1, height=5)
        self.plotter.add_mesh(pole, color='darkgray')
        
        # Light housing
        housing = pv.Cube(center=(traffic_light.position[0], 
                                 traffic_light.position[1], 
                                 4.5),
                         x_length=0.8, y_length=0.3, z_length=2.0)
        self.plotter.add_mesh(housing, color='black')
        
        # Light elements
        light_colors = ['red', 'yellow', 'green']
        for i, color in enumerate(light_colors):
            light_pos = (traffic_light.position[0], 
                        traffic_light.position[1] - 0.2, 
                        5.0 - i * 0.6)
            light = pv.Sphere(center=light_pos, radius=0.15)
            
            # Set initial state (red)
            light_color = color if (color == 'red' and traffic_light.state == 'red') or \
                                  (color == 'yellow' and traffic_light.state == 'yellow') or \
                                  (color == 'green' and traffic_light.state == 'green') else 'darkgray'
            
            mesh_name = f"traffic_light_{id(traffic_light)}_{color}"
            self.plotter.add_mesh(light, color=light_color, name=mesh_name)
    
    def _create_pedestrian_signal_mesh(self, ped_light: TrafficLight3D):
        """Create 3D mesh for pedestrian signal"""
        # Signal box
        box = pv.Cube(center=(ped_light.position[0], 
                             ped_light.position[1], 
                             2.0),
                     x_length=0.4, y_length=0.1, z_length=0.6)
        self.plotter.add_mesh(box, color='black')
        
        # Walk/Don't Walk indicators
        walk_pos = (ped_light.position[0], ped_light.position[1] - 0.1, 2.2)
        dont_walk_pos = (ped_light.position[0], ped_light.position[1] - 0.1, 1.8)
        
        walk_light = pv.Cube(center=walk_pos, x_length=0.3, y_length=0.05, z_length=0.15)
        dont_walk_light = pv.Cube(center=dont_walk_pos, x_length=0.3, y_length=0.05, z_length=0.15)
        
        walk_color = 'green' if ped_light.state == 'walk' else 'darkgray'
        dont_walk_color = 'red' if ped_light.state == 'dont_walk' else 'darkgray'
        
        self.plotter.add_mesh(walk_light, color=walk_color, 
                             name=f"ped_walk_{id(ped_light)}")
        self.plotter.add_mesh(dont_walk_light, color=dont_walk_color, 
                             name=f"ped_dont_walk_{id(ped_light)}")
    
    def _setup_lighting(self):
        """Setup scene lighting"""
        self.plotter.add_light(pv.Light(position=(10, 10, 20), focal_point=(0, 0, 0)))
        self.plotter.add_light(pv.Light(position=(-10, -10, 20), focal_point=(0, 0, 0)))
    
    def create_pedestrian(self, ped_id: str, position: Tuple[float, float], 
                         intent_prob: float = 0.5) -> Pedestrian3D:
        """Create a new 3D pedestrian"""
        pos_3d = np.array([position[0], position[1], 0.5])
        target_3d = np.array([position[0], -position[1], 0.5])  # Opposite side
        
        # Color based on intent probability
        if intent_prob > 0.7:
            color = (1.0, 0.2, 0.2)  # Red - high intent
        elif intent_prob > 0.4:
            color = (1.0, 1.0, 0.0)  # Yellow - medium intent
        else:
            color = (0.2, 1.0, 0.2)  # Green - low intent
        
        pedestrian = Pedestrian3D(
            id=ped_id,
            position=pos_3d,
            target=target_3d,
            speed=1.5,
            intent_prob=intent_prob,
            is_crossing=False,
            color=color
        )
        
        # Create 3D mesh (simplified human figure)
        self._create_pedestrian_mesh(pedestrian)
        self.pedestrians.append(pedestrian)
        return pedestrian
    
    def _create_pedestrian_mesh(self, pedestrian: Pedestrian3D):
        """Create 3D mesh for pedestrian"""
        # Body (cylinder)
        body = pv.Cylinder(center=(pedestrian.position[0], 
                                  pedestrian.position[1], 
                                  0.8),
                          direction=(0, 0, 1),
                          radius=0.3, height=1.2)
        
        # Head (sphere)
        head = pv.Sphere(center=(pedestrian.position[0], 
                                pedestrian.position[1], 
                                1.6), radius=0.2)
        
        # Combine meshes
        pedestrian.mesh = body + head
        mesh_name = f"pedestrian_{pedestrian.id}"
        self.plotter.add_mesh(pedestrian.mesh, color=pedestrian.color, name=mesh_name)
    
    def create_vehicle(self, vehicle_id: str, position: Tuple[float, float], 
                      direction: Tuple[float, float]) -> Vehicle3D:
        """Create a new 3D vehicle"""
        pos_3d = np.array([position[0], position[1], 0.5])
        dir_3d = np.array([direction[0], direction[1], 0])
        
        vehicle = Vehicle3D(
            id=vehicle_id,
            position=pos_3d,
            direction=dir_3d,
            speed=8.0
        )
        
        self._create_vehicle_mesh(vehicle)
        self.vehicles.append(vehicle)
        return vehicle
    
    def _create_vehicle_mesh(self, vehicle: Vehicle3D):
        """Create 3D mesh for vehicle"""
        # Car body
        body = pv.Cube(center=(vehicle.position[0], 
                              vehicle.position[1], 
                              0.5),
                      x_length=4.0, y_length=1.8, z_length=1.0)
        
        # Car top
        top = pv.Cube(center=(vehicle.position[0], 
                             vehicle.position[1], 
                             1.2),
                     x_length=2.5, y_length=1.6, z_length=0.8)
        
        # Combine meshes
        vehicle.mesh = body + top
        mesh_name = f"vehicle_{vehicle.id}"
        self.plotter.add_mesh(vehicle.mesh, color='blue', name=mesh_name)
    
    def update_traffic_lights(self, vehicle_state: str, pedestrian_state: str):
        """Update traffic light states"""
        for light in self.traffic_lights:
            if light.light_type == 'vehicle':
                light.state = vehicle_state.lower()
                self._update_traffic_light_visual(light)
            else:
                light.state = pedestrian_state.lower().replace(' ', '_')
                self._update_pedestrian_signal_visual(light)
    
    def _update_traffic_light_visual(self, traffic_light: TrafficLight3D):
        """Update visual representation of traffic light"""
        light_colors = ['red', 'yellow', 'green']
        for color in light_colors:
            mesh_name = f"traffic_light_{id(traffic_light)}_{color}"
            if mesh_name in self.plotter.renderer.actors:
                if color == traffic_light.state:
                    new_color = color
                else:
                    new_color = 'darkgray'
                # Update mesh color
                actor = self.plotter.renderer.actors[mesh_name]
                if hasattr(actor, 'GetProperty'):
                    if new_color == 'red':
                        actor.GetProperty().SetColor(1, 0, 0)
                    elif new_color == 'yellow':
                        actor.GetProperty().SetColor(1, 1, 0)
                    elif new_color == 'green':
                        actor.GetProperty().SetColor(0, 1, 0)
                    else:
                        actor.GetProperty().SetColor(0.2, 0.2, 0.2)
    
    def _update_pedestrian_signal_visual(self, ped_light: TrafficLight3D):
        """Update visual representation of pedestrian signal"""
        walk_name = f"ped_walk_{id(ped_light)}"
        dont_walk_name = f"ped_dont_walk_{id(ped_light)}"
        
        if walk_name in self.plotter.renderer.actors:
            walk_actor = self.plotter.renderer.actors[walk_name]
            if ped_light.state == 'walk':
                walk_actor.GetProperty().SetColor(0, 1, 0)  # Green
            else:
                walk_actor.GetProperty().SetColor(0.2, 0.2, 0.2)  # Dark gray
        
        if dont_walk_name in self.plotter.renderer.actors:
            dont_walk_actor = self.plotter.renderer.actors[dont_walk_name]
            if ped_light.state == 'dont_walk':
                dont_walk_actor.GetProperty().SetColor(1, 0, 0)  # Red
            else:
                dont_walk_actor.GetProperty().SetColor(0.2, 0.2, 0.2)  # Dark gray
    
    def update_pedestrian_position(self, ped_id: str, new_position: Tuple[float, float]):
        """Update pedestrian position"""
        for pedestrian in self.pedestrians:
            if pedestrian.id == ped_id:
                pedestrian.position[0] = new_position[0]
                pedestrian.position[1] = new_position[1]
                
                # Update mesh position
                mesh_name = f"pedestrian_{ped_id}"
                if mesh_name in self.plotter.renderer.actors:
                    # Remove old mesh and create new one
                    self.plotter.remove_actor(mesh_name)
                    self._create_pedestrian_mesh(pedestrian)
                break
    
    def update_vehicle_position(self, vehicle_id: str, new_position: Tuple[float, float]):
        """Update vehicle position"""
        for vehicle in self.vehicles:
            if vehicle.id == vehicle_id:
                vehicle.position[0] = new_position[0]
                vehicle.position[1] = new_position[1]
                
                # Update mesh position
                mesh_name = f"vehicle_{vehicle_id}"
                if mesh_name in self.plotter.renderer.actors:
                    # Remove old mesh and create new one
                    self.plotter.remove_actor(mesh_name)
                    self._create_vehicle_mesh(vehicle)
                break
    
    def load_sync_data(self) -> Dict:
        """Load synchronization data from main simulation"""
        try:
            if os.path.exists(self.sync_file):
                with open(self.sync_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading sync data: {e}")
        return {}
    
    def animate_scene(self):
        """Animate the 3D scene"""
        frame_count = 0
        
        while self.running:
            # Load data from main simulation
            sync_data = self.load_sync_data()
            
            if sync_data:
                # Update traffic lights
                if 'traffic_lights' in sync_data:
                    tl_data = sync_data['traffic_lights']
                    self.update_traffic_lights(
                        tl_data.get('vehicle', 'red'),
                        tl_data.get('pedestrian', 'dont_walk')
                    )
                
                # Update pedestrian positions and create new ones
                if 'pedestrians' in sync_data:
                    for ped_data in sync_data['pedestrians']:
                        ped_id = ped_data['id']
                        position = (ped_data['x'], ped_data['y'])
                        intent = ped_data.get('intent_prob', 0.5)
                        
                        # Check if pedestrian exists
                        existing_ped = None
                        for p in self.pedestrians:
                            if p.id == ped_id:
                                existing_ped = p
                                break
                        
                        if existing_ped:
                            self.update_pedestrian_position(ped_id, position)
                            existing_ped.intent_prob = intent
                        else:
                            self.create_pedestrian(ped_id, position, intent)
                
                # Update vehicle positions
                if 'vehicles' in sync_data:
                    for vehicle_data in sync_data['vehicles']:
                        vehicle_id = vehicle_data['id']
                        position = (vehicle_data['x'], vehicle_data['y'])
                        
                        # Check if vehicle exists
                        existing_vehicle = None
                        for v in self.vehicles:
                            if v.id == vehicle_id:
                                existing_vehicle = v
                                break
                        
                        if existing_vehicle:
                            self.update_vehicle_position(vehicle_id, position)
                        else:
                            direction = (vehicle_data.get('dx', 0), vehicle_data.get('dy', 1))
                            self.create_vehicle(vehicle_id, position, direction)
            
            # Simple animation - move some objects
            frame_count += 1
            if frame_count % 30 == 0:  # Every 30 frames
                # Add some dynamic movement for demo
                for pedestrian in self.pedestrians:
                    if not pedestrian.is_crossing:
                        # Small random movement
                        pedestrian.position[0] += random.uniform(-0.1, 0.1)
                        pedestrian.position[1] += random.uniform(-0.1, 0.1)
            
            # Update the scene
            self.plotter.render()
            time.sleep(0.033)  # ~30 FPS
    
    def start_simulation(self):
        """Start the 3D simulation"""
        self.running = True
        
        # Create some initial objects for demo
        self.create_pedestrian("P1", (5, 8), 0.8)
        self.create_pedestrian("P2", (-3, -8), 0.3)
        self.create_vehicle("V1", (0, -15), (0, 1))
        self.create_vehicle("V2", (15, 0), (-1, 0))
        
        # Set up camera
        self.plotter.camera_position = [(30, 30, 25), (0, 0, 2), (0, 0, 1)]
        
        # Start animation thread
        self.animation_thread = threading.Thread(target=self.animate_scene)
        self.animation_thread.daemon = True
        self.animation_thread.start()
        
        # Show the plotter
        self.plotter.show()
    
    def stop_simulation(self):
        """Stop the 3D simulation"""
        self.running = False
        if self.animation_thread and self.animation_thread.is_alive():
            self.animation_thread.join(timeout=1.0)

def main():
    """Main function to run the 3D simulation"""
    print("Starting PI-BREPSC 3D Traffic Simulation...")
    print("This beautiful 3D visualization complements the main 2D simulation.")
    print("Press 'q' in the 3D window to quit.")
    
    # Create and start 3D simulation
    sim_3d = Beautiful3DSimulation()
    
    try:
        sim_3d.start_simulation()
    except KeyboardInterrupt:
        print("\nShutting down 3D simulation...")
    finally:
        sim_3d.stop_simulation()

if __name__ == "__main__":
    main() 