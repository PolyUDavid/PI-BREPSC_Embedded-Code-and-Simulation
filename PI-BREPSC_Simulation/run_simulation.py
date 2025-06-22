#!/usr/bin/env python3
"""
Simple PI-BREPSC Simulation Launcher
Focuses on reliable 2D simulation with optional 3D text view
"""

import subprocess
import sys
import time
import threading
import os
import json

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ['pygame', 'numpy']
    optional_packages = ['sklearn']  # scikit-learn imports as sklearn
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    # Check optional packages
    for package in optional_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"⚠️  Optional package '{package}' not found, but simulation will still work")
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("📦 Please install them using:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def run_main_simulation():
    """Run the main 2D simulation"""
    print("🚦 Starting Main 2D Simulation...")
    try:
        subprocess.run([sys.executable, "main_simulation.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running main simulation: {e}")
    except KeyboardInterrupt:
        print("🛑 Main simulation interrupted by user")

def run_text_3d_viewer():
    """Run a simple text-based 3D viewer"""
    print("📱 Starting Text-Based 3D Viewer...")
    
    def display_3d_data():
        """Display 3D data in text format"""
        sync_file = "3d_sync_data.json"
        
        while True:
            try:
                os.system('clear' if os.name == 'posix' else 'cls')
                
                print("=" * 80)
                print("🎯 PI-BREPSC 3D Traffic View (Text Mode)")
                print("=" * 80)
                
                # Load data
                data = {}
                if os.path.exists(sync_file):
                    try:
                        with open(sync_file, 'r') as f:
                            data = json.load(f)
                    except Exception as e:
                        print(f"Error loading data: {e}")
                
                if not data:
                    print("⏳ Waiting for simulation data...")
                    print("💡 Start the main simulation (option 1) first")
                else:
                    # Traffic lights
                    if 'traffic_lights' in data:
                        tl = data['traffic_lights']
                        vehicle_light = "🟢" if tl.get('vehicle') == 'GREEN' else \
                                       "🟡" if tl.get('vehicle') == 'YELLOW' else "🔴"
                        ped_light = "🚶" if tl.get('pedestrian') == 'WALK' else "🛑"
                        print(f"🚦 Traffic Lights:")
                        print(f"   Vehicle: {vehicle_light} {tl.get('vehicle', 'RED')}")
                        print(f"   Pedestrian: {ped_light} {tl.get('pedestrian', 'DONT_WALK')}")
                    
                    print()
                    print("🏗️  3D Intersection:")
                    print("```")
                    print("     📍N")
                    print("      |")
                    print("   W--+--E  🚦")
                    print("      |")
                    print("     📍S")
                    print("```")
                    print()
                    
                    # Pedestrians
                    pedestrians = data.get('pedestrians', [])
                    print(f"🚶 Pedestrians ({len(pedestrians)}):")
                    if pedestrians:
                        for ped in pedestrians:
                            intent = ped.get('intent_prob', 0.5)
                            color = "🔴" if intent > 0.7 else "🟡" if intent > 0.4 else "🟢"
                            intent_desc = "High" if intent > 0.7 else "Medium" if intent > 0.4 else "Low"
                            status = "🚶‍♂️ Crossing" if ped.get('is_crossing', False) else "⏳ Waiting"
                            anomaly = "⚠️ ANOMALY" if ped.get('anomaly', False) else ""
                            priority = ped.get('priority', 'normal').upper()
                            
                            print(f"   {color} {ped['id']}: Pos({ped['x']:.1f}, {ped['y']:.1f}) | "
                                  f"Intent: {intent_desc}({intent:.2f}) | {status} | "
                                  f"Priority: {priority} {anomaly}")
                    else:
                        print("   No pedestrians detected")
                    
                    print()
                    
                    # Vehicles
                    vehicles = data.get('vehicles', [])
                    print(f"🚗 Vehicles ({len(vehicles)}):")
                    if vehicles:
                        for veh in vehicles:
                            print(f"   🚙 {veh['id']}: Pos({veh['x']:.1f}, {veh['y']:.1f}) | "
                                  f"Speed: {veh.get('speed', 0):.1f}")
                    else:
                        print("   No vehicles detected")
                    
                    # AI Decisions
                    ai_decisions = data.get('ai_decisions', {})
                    if ai_decisions:
                        print()
                        print("🤖 AI Decisions:")
                        for key, value in ai_decisions.items():
                            print(f"   {key}: {value}")
                
                print()
                print("💡 Instructions:")
                print("   - This shows real-time data from the 2D simulation")
                print("   - Start main simulation first for data")
                print("   - Updates every 2 seconds")
                print("   - Press Ctrl+C to quit")
                print("=" * 80)
                
                time.sleep(2)
                
            except KeyboardInterrupt:
                print("\n👋 3D Text Viewer stopped")
                break
            except Exception as e:
                print(f"Error in 3D viewer: {e}")
                time.sleep(2)
    
    try:
        display_3d_data()
    except KeyboardInterrupt:
        print("\n🛑 3D viewer interrupted by user")

def main():
    """Main launcher function"""
    print("=" * 60)
    print("🎮 PI-BREPSC Traffic Simulation")
    print("   Intelligent Traffic Management with Edge AI")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    print("\nChoose simulation mode:")
    print("1. Main 2D Simulation (recommended)")
    print("2. Text-Based 3D Viewer")
    print("3. Web-Based 3D Simulation (Three.js)")
    print("4. OpenGL 3D Simulation")
    print("5. Both (2D + 3D Text View)")
    print("6. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == "1":
                print("\n🚦 Running Main 2D Simulation...")
                print("💡 Use these controls:")
                print("   S/D = Spawn pedestrians")
                print("   B = Toggle button for selected pedestrian")
                print("   M = Toggle malicious for selected pedestrian")
                print("   Click = Select pedestrian")
                print("   ESC = Exit")
                run_main_simulation()
                break
                
            elif choice == "2":
                print("\n📱 Running Text-Based 3D Viewer...")
                print("⚠️  Note: Start the main simulation first for data")
                run_text_3d_viewer()
                break
                
            elif choice == "3":
                print("\n🌐 Starting Web-Based 3D Simulation...")
                print("📝 Instructions:")
                print("   - Web服务器将自动启动")
                print("   - Browser will open with 3D visualization")
                print("   - Start main simulation for live data")
                print("   - Use Ctrl+C to stop web server")
                try:
                    subprocess.run([sys.executable, "web_3d_simulation.py"], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"❌ Error running web 3D simulation: {e}")
                break
                
            elif choice == "4":
                print("\n🎮 Starting OpenGL 3D Simulation...")
                print("📝 Instructions:")
                print("   - High-performance OpenGL rendering")
                print("   - Interactive camera controls")
                print("   - Start main simulation for live data")
                try:
                    subprocess.run([sys.executable, "opengl_3d_simulation.py"], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"❌ Error running OpenGL simulation: {e}")
                    print("💡 Try installing OpenGL: pip install PyOpenGL")
                break
                
            elif choice == "5":
                print("\n🎮 Running Both Simulations...")
                print("📝 Instructions:")
                print("   - Main 2D simulation window will open first")
                print("   - 3D text viewer will run in this terminal")
                print("   - Use Ctrl+C to stop the 3D viewer")
                print("   - Close the 2D window to stop main simulation")
                
                # Start main simulation in thread
                main_thread = threading.Thread(target=run_main_simulation, daemon=True)
                main_thread.start()
                
                # Wait a bit then start 3D viewer in main thread
                time.sleep(2)
                run_text_3d_viewer()
                break
                
            elif choice == "6":
                print("👋 Goodbye!")
                sys.exit(0)
                
            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, 4, 5, or 6.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            sys.exit(0)
        except EOFError:
            print("\n👋 Goodbye!")
            sys.exit(0)

if __name__ == "__main__":
    main() 