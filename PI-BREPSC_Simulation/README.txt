# PI-BREPSC Simulation Platform

## Overview

The PI-BREPSC (Physically Informed BREmermann PEdestrian Signal Control) simulation is a comprehensive, multi-modal platform designed for advanced analysis of pedestrian behavior and optimization of traffic signal control strategies. This sophisticated simulation suite combines detailed pedestrian and vehicle dynamics with realistic Roadside Unit (RSU) modeling, responsive Traffic Light Controllers (TLC), and cutting-edge Edge AI systems.

The platform offers multiple visualization modes including 2D simulation, immersive 3D visualization, web-based interfaces, and embedded system integration, making it suitable for research, education, demonstration, and real-world deployment scenarios.

## Requirements

### Core Dependencies
```bash
pip install pygame numpy scikit-learn
```

### 3D Visualization Dependencies
```bash
pip install pyvista vtk meshio panda3d PyOpenGL PyOpenGL_accelerate
```

### Web Dependencies
Built-in with included Three.js library

## Installation

1. **Create and activate virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Complete File Structure and Components

### 🎯 Main Simulation Engine
- **`main_simulation.py`** - Primary 2D simulation orchestrating all components including pedestrians, vehicles, RSU scanners, traffic lights, and Edge AI systems. Main entry point for standard simulation.
- **`config.py`** - Central configuration hub containing all simulation parameters: screen dimensions, road geometry, RSU positions, timing constants, AI thresholds, and visual settings.

### 🚶 Individual Component Simulators
- **`pedestrian_simulator.py`** - Advanced pedestrian agent behavior system with pathfinding, button pressing logic, malicious behavior modeling, and crosswalk signal interaction.
- **`vehicle_simulator.py`** - Vehicle movement engine with traffic light compliance, speed control, and pedestrian crossing interactions.
- **`rsu_simulator.py`** - Roadside Unit implementation with RSSI-based detection, multi-scanner arrays, signal modeling, and data fusion for pedestrian tracking.
- **`traffic_light_controller.py`** - Intelligent traffic signal management processing pedestrian requests, RSU data, Edge AI recommendations, and safety-prioritized timing strategies.

### 🧠 Edge AI and Intelligence Systems
- **`edge_ai_module.py`** - Research-grade Edge AI featuring multi-modal time-series fusion, statistical/temporal feature extraction, intent inference, anomaly detection, and intelligent priority suggestions.
- **`edge_logic_module.py`** - Alternative Edge AI implementation with different algorithmic approaches for comparative analysis and research.
- **`edge_traffic_controller.c`** - Embedded C real-time traffic controller reading AI suggestions for hardware deployment scenarios.

### 🎨 3D Visualization Suite
- **`3d_simulation.py`** - Primary PyVista-based 3D visualization with realistic lighting, materials, complex geometries, and real-time synchronization.
- **`panda3d_simulation.py`** - Panda3D game engine implementation offering advanced rendering and interactive features for education/demonstration.
- **`opengl_3d_simulation.py`** - Direct OpenGL implementation providing low-level graphics control for specialized research applications.
- **`simple_3d_simulation.py`** - Lightweight 3D option for resource-constrained systems while maintaining essential visual feedback.

### 🌐 Web-Based Visualization
- **`web_3d_simulation.py`** - Browser-based 3D simulation using Three.js for remote access and collaborative analysis.
- **`web_3d_simulation_fixed.py`** - Enhanced web simulation with improved coordinate mapping, error handling, and optimized performance for stable browser visualization.
- **`index.html`** - Complete web interface with HTML structure, CSS styling, and JavaScript integration for Three.js visualization.
- **`three_inlined.js`** - Inlined Three.js library for offline capability without external CDN dependencies.

### 🔄 Data Management and Synchronization
- **`sync_3d_data.py`** - Real-time data exchange handler between 2D/3D simulations using JSON protocols for synchronized visualization.
- **`3d_sync_data.json`** - JSON data storage for simulation state transfer including pedestrian positions, vehicle states, traffic phases, and AI decisions.

### 🚀 Launcher and Utility Scripts
- **`run_simulation.py`** - Simple launcher for main 2D simulation with basic parameter handling and user-friendly interface.
- **`run_both_simulations.py`** - Advanced launcher for simultaneous 2D/3D simulations with dependency checking, menu interface, and threaded execution.
- **`final_review_gate.py`** - Quality assurance module performing system checks, parameter validation, and configuration verification.

### 📊 System Status and Communication Files
- **`ai_priority.txt`** - Real-time AI decision output communicating priority levels from Edge AI to traffic controller.
- **`system_priority.txt`** - System-level priority configuration for simulation behavior and resource allocation.
- **`pedestrian_button_pressed.flag`** - Event flag for pedestrian button presses enabling inter-process communication.

### 📚 Documentation and Resources
- **`requirements.txt`** - Python package dependencies for easy installation.
- **`modern_solutions.md`** - Technical documentation on modern approaches and architectural decisions.
- **`JL701N.pdf`** - Hardware specifications and embedded system reference materials.
- **`traffic_analysis_report.docx`** - Comprehensive analysis report with simulation results and research findings.

## Quick Start Guide

### Standard 2D Simulation
```bash
python main_simulation.py
```

### 3D Visualization (PyVista)
```bash
python 3d_simulation.py
```

### Web-Based 3D Simulation
```bash
python web_3d_simulation_fixed.py
# Open browser to http://localhost:8001
```

### Combined 2D + 3D Experience
```bash
python run_both_simulations.py
```

### Alternative 3D Options
```bash
python panda3d_simulation.py     # Panda3D engine
python opengl_3d_simulation.py   # Direct OpenGL
python simple_3d_simulation.py   # Lightweight version
```

## Controls

- **`S`** - Spawn pedestrian from West
- **`D`** - Spawn pedestrian from East  
- **`B`** - Selected pedestrian presses button
- **`M`** - Toggle malicious behavior for selected pedestrian
- **`Click`** - Select pedestrian
- **`ESC`** - Exit simulation

## Information Panel Features

Real-time display includes:
- Vehicle and pedestrian light phases
- Pedestrian request status and queue
- Selected pedestrian details (position, motion, button status, malicious flag, RSSI, anomaly detection, intent probability, confidence, waiting time)
- RSU scanner RSSI values and coverage
- **Edge AI results:** intent probabilities, anomaly flags, priority recommendations for each pedestrian

## 3D Visualization Features

### PyVista-Based 3D (3d_simulation.py)
- Photorealistic lighting and materials
- Complex geometric modeling
- Real-time synchronization with 2D simulation
- Interactive camera controls
- Professional-quality rendering for publications

### Web-Based 3D (web_3d_simulation_fixed.py)
- Browser compatibility across devices
- Remote access capability
- Mouse-based scene exploration
- Live data synchronization
- Collaborative analysis support

### Alternative 3D Engines
- **Panda3D:** Game engine features with advanced rendering
- **OpenGL:** Low-level graphics for research customization
- **Simple 3D:** Resource-efficient lightweight visualization

## Underlying Models and Algorithms

### Pedestrian Movement Model
Advanced agent-based system with pathfinding algorithms, traffic signal compliance, button pressing behavior, malicious action modeling, and social interaction capabilities.

### RSU Scanning Model
Multi-scanner array simulation with RSSI signal modeling, interference effects, coverage area optimization, and data fusion algorithms for accurate pedestrian detection and tracking.

### Traffic Light Control Logic
State machine implementation with pedestrian request processing, safety prioritization, adaptive timing strategies, and Edge AI integration for intelligent signal management.

### Edge AI System
- Multi-modal feature fusion (RSSI, motion, button, behavioral flags)
- Statistical and temporal feature extraction
- Intent probability inference using machine learning
- Anomaly detection with confidence evaluation
- Priority recommendation system for proactive traffic management

## Hardware Integration

### Embedded System Support
- **C-based controller** for real-time edge deployment
- **Hardware-software co-design** for smart intersection implementation
- **Serial/socket communication** interfaces for sensor integration
- **Real-world deployment** capabilities with embedded platforms

## Architecture Overview

**Modular Design:**
- Core simulation engine managing main loop and coordination
- Multiple visualization backends (2D/3D/Web)
- AI and intelligence modules for advanced decision-making
- Hardware integration interfaces for real-world deployment
- Data synchronization and communication systems
- Web interfaces for remote access and collaboration

## Research Applications

- **Traffic Control Strategy Evaluation:** Testing adaptive signals and timing optimization
- **Pedestrian Behavior Analysis:** Understanding movement patterns and decision-making
- **AI Algorithm Development:** Edge AI for traffic management and anomaly detection
- **Infrastructure Design:** Evaluating crosswalk layouts and RSU positioning
- **Safety Assessment:** Analyzing pedestrian-vehicle interaction scenarios
- **Educational Training:** Interactive learning for traffic engineering concepts

## Potential Extensions

- **Enhanced AI Models:** Deep learning, reinforcement learning, federated learning
- **V2X Communication:** Vehicle-to-everything protocols and smart city integration
- **Virtual Reality:** Immersive VR interfaces for training and demonstration
- **Cloud Deployment:** Large-scale simulations and distributed experimentation
- **Real-World Data Integration:** Live traffic feeds and sensor network connectivity
- **Advanced Visualization:** AR overlays, holographic displays, mobile interfaces

## Limitations and Considerations

- Simplified models compared to real-world complexity
- Computational constraints affecting simulation scale
- Requires validation against real-world deployment scenarios
- Performance varies based on hardware capabilities for 3D visualization

## Target Users

- **Researchers:** Traffic engineering, AI, smart city development
- **Engineers:** Traffic system design and optimization
- **Students:** Transportation engineering education and training
- **Planners:** Urban design and infrastructure development
- **Policymakers:** Traffic management strategy evaluation

## Support and Contributing

This platform is designed for extensibility and customization. Users can modify existing modules, integrate new data sources, or develop additional visualization modes to meet specific research requirements.

For technical support, documentation, or contribution guidelines, please refer to the project documentation and development team contacts.

---

*This comprehensive simulation platform represents a complete solution for pedestrian safety research, traffic management optimization, and intelligent transportation system development.* 