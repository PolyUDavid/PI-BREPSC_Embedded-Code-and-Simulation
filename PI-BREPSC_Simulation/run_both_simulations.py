#!/usr/bin/env python3
"""
Launcher Script for PI-BREPSC Simulations
Run both 2D main simulation and 3D PyVista simulation
"""

import subprocess
import sys
import time
import threading
import os

def run_main_simulation():
    """Run the main 2D simulation"""
    print("🚦 Starting Main 2D Simulation...")
    try:
        subprocess.run([sys.executable, "main_simulation.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running main simulation: {e}")
    except KeyboardInterrupt:
        print("🛑 Main simulation interrupted by user")

def run_3d_simulation():
    """Run the 3D PyVista simulation"""
    print("🎯 Starting 3D PyVista Simulation...")
    try:
        # Wait a bit for main simulation to start and create sync data
        time.sleep(2)
        subprocess.run([sys.executable, "3d_simulation.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running 3D simulation: {e}")
    except KeyboardInterrupt:
        print("🛑 3D simulation interrupted by user")

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ['pygame', 'pyvista', 'numpy', 'vtk']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("📦 Please install them using:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def main():
    """Main launcher function"""
    print("=" * 60)
    print("🎮 PI-BREPSC Traffic Simulation Launcher")
    print("   Intelligent Traffic Management with Edge AI")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    print("\nChoose simulation mode:")
    print("1. 2D Simulation Only (main_simulation.py)")
    print("2. 3D Simulation Only (3d_simulation.py)")
    print("3. Both Simulations (recommended)")
    print("4. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == "1":
                print("\n🚦 Running 2D Simulation Only...")
                run_main_simulation()
                break
                
            elif choice == "2":
                print("\n🎯 Running 3D Simulation Only...")
                print("⚠️  Note: 3D simulation works best with main simulation running")
                run_3d_simulation()
                break
                
            elif choice == "3":
                print("\n🎮 Running Both Simulations...")
                print("📝 Instructions:")
                print("   - Main 2D simulation will start first")
                print("   - 3D simulation will start after 2 seconds")
                print("   - Both windows will be interactive")
                print("   - Close either window to stop both simulations")
                print("   - Use Ctrl+C in terminal to force quit")
                
                # Create threads for both simulations
                main_thread = threading.Thread(target=run_main_simulation, daemon=True)
                sim_3d_thread = threading.Thread(target=run_3d_simulation, daemon=True)
                
                try:
                    # Start main simulation
                    main_thread.start()
                    
                    # Start 3D simulation
                    sim_3d_thread.start()
                    
                    # Wait for both to complete
                    main_thread.join()
                    sim_3d_thread.join()
                    
                except KeyboardInterrupt:
                    print("\n🛑 Stopping all simulations...")
                
                break
                
            elif choice == "4":
                print("👋 Goodbye!")
                sys.exit(0)
                
            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            sys.exit(0)
        except EOFError:
            print("\n👋 Goodbye!")
            sys.exit(0)

if __name__ == "__main__":
    main() 