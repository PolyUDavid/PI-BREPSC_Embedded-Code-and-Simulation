#!/usr/bin/env python3
"""
Data Synchronization Module for 3D Simulation
Handles data exchange between main 2D simulation and 3D PyVista simulation
"""

import json
import time
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

@dataclass
class SyncPedestrian:
    """Pedestrian data for synchronization"""
    id: str
    x: float
    y: float
    intent_prob: float
    is_crossing: bool
    anomaly: bool
    priority: str

@dataclass
class SyncVehicle:
    """Vehicle data for synchronization"""
    id: str
    x: float
    y: float
    dx: float
    dy: float
    speed: float

@dataclass
class SyncTrafficLights:
    """Traffic light states for synchronization"""
    vehicle: str
    pedestrian: str

@dataclass
class SyncData:
    """Complete synchronization data structure"""
    timestamp: float
    traffic_lights: SyncTrafficLights
    pedestrians: List[SyncPedestrian]
    vehicles: List[SyncVehicle]
    ai_decisions: Dict[str, Any]

class DataSynchronizer:
    """Handles data synchronization between simulations"""
    
    def __init__(self, sync_file: str = "3d_sync_data.json"):
        self.sync_file = sync_file
        self.last_update = 0
        self.update_interval = 0.1  # Update every 100ms
    
    def should_update(self) -> bool:
        """Check if enough time has passed for an update"""
        current_time = time.time()
        return (current_time - self.last_update) >= self.update_interval
    
    def extract_pedestrian_data(self, pedestrians, rsu_unit=None) -> List[SyncPedestrian]:
        """Extract pedestrian data from main simulation with RSU data"""
        sync_pedestrians = []
        
        for ped in pedestrians:
            # Get RSU tracking data for this pedestrian
            rsu_data = {}
            if rsu_unit and hasattr(rsu_unit, 'pedestrian_tracking_data'):
                rsu_data = rsu_unit.pedestrian_tracking_data.get(ped.id, {})
            
            # Extract intent probability from RSU analysis
            intent_prob = rsu_data.get('intent_prob', 0.0)
            if intent_prob == 0.0:
                intent_prob = 0.5 if ped.is_requesting_button_press else 0.1
            
            # Determine if pedestrian is crossing
            is_crossing = False
            if hasattr(ped, 'target_wait_area_key'):
                # Check if pedestrian has switched wait areas (indicating crossing)
                is_crossing = (ped.target_wait_area_key == "WAIT_AREA_EAST" and 
                              ped.pos[0] > 500) or \
                             (ped.target_wait_area_key == "WAIT_AREA_WEST" and 
                              ped.pos[0] < 700)
            
            # Determine anomaly status from RSU
            anomaly = rsu_data.get('is_anomalous', ped.is_malicious)
            
            # Determine priority from intent and confidence
            confidence = rsu_data.get('confidence', 0.0)
            if confidence >= 0.75:
                priority = 'high'
            elif confidence >= 0.5:
                priority = 'medium'
            else:
                priority = 'normal'
            
            sync_ped = SyncPedestrian(
                id=ped.id,
                x=float(ped.pos[0]),
                y=float(ped.pos[1]),
                intent_prob=float(intent_prob),
                is_crossing=bool(is_crossing),
                anomaly=bool(anomaly),
                priority=str(priority)
            )
            sync_pedestrians.append(sync_ped)
        
        return sync_pedestrians
    
    def extract_vehicle_data(self, vehicles) -> List[SyncVehicle]:
        """Extract vehicle data from main simulation"""
        sync_vehicles = []
        
        for vehicle in vehicles:
            # Get direction vector based on vehicle's direction
            dx, dy = 0, 1  # Default vertical movement
            if hasattr(vehicle, 'direction'):
                if vehicle.direction == "horizontal":
                    dx, dy = 1, 0
                else:
                    dx, dy = 0, 1
            
            sync_vehicle = SyncVehicle(
                id=str(getattr(vehicle, 'id', f"V{id(vehicle)}")),
                x=float(vehicle.pos[0]),
                y=float(vehicle.pos[1]),
                dx=float(dx),
                dy=float(dy),
                speed=float(getattr(vehicle, 'speed', 5.0))
            )
            sync_vehicles.append(sync_vehicle)
        
        return sync_vehicles
    
    def extract_traffic_light_data(self, vehicle_light: str, pedestrian_light: str) -> SyncTrafficLights:
        """Extract traffic light data from main simulation"""
        return SyncTrafficLights(
            vehicle=str(vehicle_light).upper(),
            pedestrian=str(pedestrian_light).upper()
        )
    
    def extract_ai_decisions(self, ai_module, rsu_unit=None, pedestrians=None) -> Dict[str, Any]:
        """Extract AI decision data from Edge AI module and RSU"""
        ai_decisions = {}
        
        try:
            # Get AI module decisions
            if hasattr(ai_module, 'last_decisions'):
                ai_decisions.update(ai_module.last_decisions)
            elif hasattr(ai_module, 'get_latest_decisions'):
                ai_decisions.update(ai_module.get_latest_decisions())
            
            # Add RSU statistics
            if rsu_unit and hasattr(rsu_unit, 'pedestrian_tracking_data'):
                rsu_data = rsu_unit.pedestrian_tracking_data
                
                # Count high priority pedestrians based on RSU analysis
                high_priority_count = 0
                medium_priority_count = 0
                
                for ped_id, data in rsu_data.items():
                    confidence = data.get('confidence', 0.0)
                    if confidence >= 0.75:
                        high_priority_count += 1
                    elif confidence >= 0.5:
                        medium_priority_count += 1
                
                ai_decisions.update({
                    'system_status': 'active',
                    'rsu_detections': len(rsu_data),
                    'high_priority_count': high_priority_count,
                    'medium_priority_count': medium_priority_count,
                    'total_pedestrians': len(pedestrians) if pedestrians else 0,
                    'wearable_connected': high_priority_count + medium_priority_count,
                    'edge_processing': True
                })
            
            # Add system health info
            ai_decisions.setdefault('system_status', 'active')
            ai_decisions.setdefault('edge_processing', True)
            
        except Exception as e:
            print(f"Error extracting AI decisions: {e}")
            ai_decisions = {
                'system_status': 'error',
                'edge_processing': False,
                'error': str(e)
            }
            
        return ai_decisions
    
    def create_sync_data(self, pedestrians, vehicles, vehicle_light: str, 
                        pedestrian_light: str, ai_module=None, rsu_unit=None) -> SyncData:
        """Create complete synchronization data"""
        return SyncData(
            timestamp=time.time(),
            traffic_lights=self.extract_traffic_light_data(vehicle_light, pedestrian_light),
            pedestrians=self.extract_pedestrian_data(pedestrians, rsu_unit),
            vehicles=self.extract_vehicle_data(vehicles),
            ai_decisions=self.extract_ai_decisions(ai_module, rsu_unit, pedestrians)
        )
    
    def save_sync_data(self, sync_data: SyncData) -> bool:
        """Save synchronization data to file"""
        try:
            data_dict = asdict(sync_data)
            with open(self.sync_file, 'w', encoding='utf-8') as f:
                json.dump(data_dict, f, indent=2, ensure_ascii=False)
            self.last_update = time.time()
            return True
        except Exception as e:
            print(f"Error saving sync data: {e}")
            return False
    
    def update_3d_simulation(self, pedestrians, vehicles, vehicle_light: str, 
                           pedestrian_light: str, ai_module=None, rsu_unit=None) -> bool:
        """Update 3D simulation with current data"""
        if not self.should_update():
            return False
        
        sync_data = self.create_sync_data(
            pedestrians, vehicles, vehicle_light, pedestrian_light, ai_module, rsu_unit
        )
        
        return self.save_sync_data(sync_data)
    
    def load_sync_data(self) -> Dict[str, Any]:
        """Load synchronization data from file"""
        try:
            with open(self.sync_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading sync data: {e}")
            return {}

# Global synchronizer instance
synchronizer = DataSynchronizer()

def update_3d_sync(pedestrians, vehicles, vehicle_light: str, pedestrian_light: str, ai_module=None, rsu_unit=None):
    """Convenience function to update 3D simulation synchronization"""
    return synchronizer.update_3d_simulation(
        pedestrians, vehicles, vehicle_light, pedestrian_light, ai_module, rsu_unit
    ) 