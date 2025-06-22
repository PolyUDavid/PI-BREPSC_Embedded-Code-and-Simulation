#!/usr/bin/env python3
"""
Simplified 3D Simulation Module
Avoids matplotlib encoding issues while providing 3D visualization
"""

import os
import sys
import time
import json
import threading
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any

# Try to import PyVista with error handling
try:
    # Set environment variables to avoid matplotlib issues
    os.environ['MPLBACKEND'] = 'Agg'
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    import pyvista as pv
    PYVISTA_AVAILABLE = True
    print("✅ PyVista loaded successfully")
except ImportError as e:
    print(f"❌ PyVista not available: {e}")
    print("🔧 Please install with: pip install pyvista vtk")
    PYVISTA_AVAILABLE = False
except Exception as e:
    print(f"⚠️  PyVista import error: {e}")
    print("🔧 Falling back to text-based 3D simulation")
    PYVISTA_AVAILABLE = False

@dataclass
class Pedestrian3D:
    """3D Pedestrian representation"""
    id: str
    x: float
    y: float
    z: float
    intent_prob: float
    is_crossing: bool
    color: str

@dataclass
class Vehicle3D:
    """3D Vehicle representation"""
    id: str
    x: float
    y: float
    z: float
    speed: float

class TextBased3DSimulation:
    """Text-based 3D simulation fallback"""
    
    def __init__(self):
        self.pedestrians: List[Pedestrian3D] = []
        self.vehicles: List[Vehicle3D] = []
        self.traffic_light_state = {"vehicle": "RED", "pedestrian": "DONT_WALK"}
        self.running = False
        self.sync_file = "3d_sync_data.json"
        
    def load_sync_data(self) -> Dict[str, Any]:
        """Load data from main simulation"""
        try:
            if os.path.exists(self.sync_file):
                with open(self.sync_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading sync data: {e}")
        return {}
    
    def update_from_sync_data(self):
        """Update simulation state from main simulation"""
        data = self.load_sync_data()
        
        if not data:
            return
        
        # Update traffic lights
        if 'traffic_lights' in data:
            self.traffic_light_state = data['traffic_lights']
        
        # Update pedestrians
        if 'pedestrians' in data:
            self.pedestrians.clear()
            for ped_data in data['pedestrians']:
                ped = Pedestrian3D(
                    id=ped_data['id'],
                    x=ped_data['x'],
                    y=ped_data['y'],
                    z=0.5,
                    intent_prob=ped_data.get('intent_prob', 0.5),
                    is_crossing=ped_data.get('is_crossing', False),
                    color="🔴" if ped_data.get('intent_prob', 0) > 0.7 else 
                          "🟡" if ped_data.get('intent_prob', 0) > 0.4 else "🟢"
                )
                self.pedestrians.append(ped)
        
        # Update vehicles
        if 'vehicles' in data:
            self.vehicles.clear()
            for veh_data in data['vehicles']:
                veh = Vehicle3D(
                    id=veh_data['id'],
                    x=veh_data['x'],
                    y=veh_data['y'],
                    z=0.5,
                    speed=veh_data.get('speed', 5.0)
                )
                self.vehicles.append(veh)
    
    def display_3d_scene(self):
        """Display 3D scene in text format"""
        os.system('clear' if os.name == 'posix' else 'cls')  # Clear screen
        
        print("=" * 80)
        print("🎯 PI-BREPSC 3D Traffic Simulation (Text Mode)")
        print("=" * 80)
        
        # Traffic lights
        print(f"🚦 Traffic Lights:")
        vehicle_light = "🟢" if self.traffic_light_state.get('vehicle') == 'GREEN' else \
                       "🟡" if self.traffic_light_state.get('vehicle') == 'YELLOW' else "🔴"
        ped_light = "🚶" if self.traffic_light_state.get('pedestrian') == 'WALK' else "🛑"
        print(f"   Vehicle: {vehicle_light} {self.traffic_light_state.get('vehicle', 'RED')}")
        print(f"   Pedestrian: {ped_light} {self.traffic_light_state.get('pedestrian', 'DONT_WALK')}")
        print()
        
        # Intersection visualization
        print("🏗️  3D Intersection View:")
        print("```")
        print("     📍N")
        print("      |")
        print("   W--+--E")
        print("      |")
        print("     📍S")
        print("```")
        print()
        
        # Pedestrians
        print(f"🚶 Pedestrians ({len(self.pedestrians)}):")
        if self.pedestrians:
            for ped in self.pedestrians:
                status = "🚶‍♂️ Crossing" if ped.is_crossing else "⏳ Waiting"
                intent_desc = "High" if ped.intent_prob > 0.7 else "Medium" if ped.intent_prob > 0.4 else "Low"
                print(f"   {ped.color} {ped.id}: Position({ped.x:.1f}, {ped.y:.1f}) | Intent: {intent_desc} ({ped.intent_prob:.2f}) | {status}")
        else:
            print("   No pedestrians detected")
        print()
        
        # Vehicles
        print(f"🚗 Vehicles ({len(self.vehicles)}):")
        if self.vehicles:
            for veh in self.vehicles:
                print(f"   🚙 {veh.id}: Position({veh.x:.1f}, {veh.y:.1f}) | Speed: {veh.speed:.1f}")
        else:
            print("   No vehicles detected")
        print()
        
        # Instructions
        print("💡 Instructions:")
        print("   - This is a text-based 3D simulation view")
        print("   - Run the main 2D simulation in another terminal")
        print("   - 数据每几秒自动同步")
        print("   - Press Ctrl+C to quit")
        print("=" * 80)
    
    def run(self):
        """Run the text-based simulation"""
        self.running = True
        print("🚀 Starting Text-Based 3D Simulation...")
        print("⚠️  Note: This is a fallback mode. Install PyVista for full 3D graphics.")
        print()
        
        try:
            while self.running:
                self.update_from_sync_data()
                self.display_3d_scene()
                time.sleep(2)  # Update every 2 seconds
        except KeyboardInterrupt:
            print("\n👋 3D Simulation stopped by user")
        finally:
            self.running = False

class PyVista3DSimulation:
    """Full PyVista 3D simulation"""
    
    def __init__(self):
        # Configure PyVista to avoid display issues
        pv.set_plot_theme("default")
        pv.global_theme.background = 'lightblue'
        
        self.plotter = pv.Plotter(title="PI-BREPSC 3D Traffic Simulation", 
                                 window_size=(1200, 800))
        self.sync_file = "3d_sync_data.json"
        self.running = False
        
        # Scene setup
        self._setup_scene()
    
    def _setup_scene(self):
        """Setup 3D scene"""
        # Ground plane
        ground = pv.Plane(center=(0, 0, -0.1), direction=(0, 0, 1), 
                         i_size=50, j_size=50)
        self.plotter.add_mesh(ground, color='lightgray', opacity=0.8)
        
        # Roads
        road_h = pv.Box(bounds=(-25, 25, -4, 4, 0, 0.1))
        road_v = pv.Box(bounds=(-4, 4, -25, 25, 0, 0.1))
        self.plotter.add_mesh(road_h, color='dimgray')
        self.plotter.add_mesh(road_v, color='dimgray')
        
        # Buildings
        building_positions = [(-20, -20, 10), (20, -20, 15), (-20, 20, 12), (20, 20, 18)]
        for i, (x, y, h) in enumerate(building_positions):
            building = pv.Box(bounds=(x-7, x+7, y-7, y+7, 0, h))
            colors = ['lightcoral', 'lightsteelblue', 'lightgreen', 'lightyellow']
            self.plotter.add_mesh(building, color=colors[i], opacity=0.7)
        
        # Set camera
        self.plotter.camera_position = [(40, 40, 30), (0, 0, 5), (0, 0, 1)]
    
    def load_sync_data(self) -> Dict[str, Any]:
        """Load data from main simulation"""
        try:
            if os.path.exists(self.sync_file):
                with open(self.sync_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def update_scene(self):
        """Update 3D scene with new data"""
        data = self.load_sync_data()
        
        if not data:
            return
        
        # Clear dynamic objects
        self.plotter.clear_actors()
        self._setup_scene()  # Re-setup static scene
        
        # Add pedestrians
        if 'pedestrians' in data:
            for ped_data in data['pedestrians']:
                x, y = ped_data['x'] / 10, ped_data['y'] / 10  # Scale down
                intent = ped_data.get('intent_prob', 0.5)
                
                # Create pedestrian (simple cylinder + sphere)
                body = pv.Cylinder(center=(x, y, 0.8), direction=(0, 0, 1),
                                  radius=0.3, height=1.2)
                head = pv.Sphere(center=(x, y, 1.6), radius=0.2)
                ped_mesh = body + head
                
                # Color based on intent
                color = 'red' if intent > 0.7 else 'yellow' if intent > 0.4 else 'green'
                self.plotter.add_mesh(ped_mesh, color=color, opacity=0.8)
        
        # Add vehicles
        if 'vehicles' in data:
            for veh_data in data['vehicles']:
                x, y = veh_data['x'] / 10, veh_data['y'] / 10  # Scale down
                
                # Create vehicle (box)
                vehicle = pv.Box(bounds=(x-2, x+2, y-0.9, y+0.9, 0, 1))
                self.plotter.add_mesh(vehicle, color='blue', opacity=0.9)
    
    def run(self):
        """Run PyVista simulation"""
        self.running = True
        
        def update_loop():
            while self.running:
                try:
                    self.update_scene()
                    time.sleep(1)
                except Exception as e:
                    print(f"Update error: {e}")
                    time.sleep(1)
        
        # Start update thread
        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()
        
        try:
            self.plotter.show()
        except Exception as e:
            print(f"Display error: {e}")
        finally:
            self.running = False

def main():
    """Main function"""
    print("🎯 PI-BREPSC 3D Traffic Simulation")
    print("=" * 50)
    
    if PYVISTA_AVAILABLE:
        print("🎮 Starting PyVista 3D Simulation...")
        try:
            sim = PyVista3DSimulation()
            sim.run()
        except Exception as e:
            print(f"❌ PyVista simulation failed: {e}")
            print("🔄 Falling back to text mode...")
            sim = TextBased3DSimulation()
            sim.run()
    else:
        print("📱 Starting Text-Based 3D Simulation...")
        sim = TextBased3DSimulation()
        sim.run()

if __name__ == "__main__":
    main() 