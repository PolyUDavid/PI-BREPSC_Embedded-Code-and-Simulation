#!/usr/bin/env python3
"""
Web-based 3D Traffic Simulation using Three.js
High-quality realistic rendering for traffic intersection
"""

import json
import time
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver
import webbrowser
import os

class TrafficSimulationHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler for serving simulation data"""
    
    def do_GET(self):
        print(f"Received GET request for: {self.path}")
        if self.path == '/api/traffic_data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Load current simulation data
            data = self.load_simulation_data()
            self.wfile.write(json.dumps(data).encode())
        elif self.path == '/api/pedestrian_cross':
            # This endpoint can be used to signal a pedestrian cross event
            # For now, just acknowledge and print
            print("Received pedestrian cross signal!")
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "message": "Pedestrian cross signal received"}).encode())
        else:
            super().do_GET()
    
    def do_POST(self):
        print(f"Received POST request for: {self.path}")
        if self.path == '/api/pedestrian_cross':
            # Handle pedestrian crossing signal
            print("Received pedestrian cross signal via POST!")
            # Create pedestrian button pressed flag file
            try:
                with open('pedestrian_button_pressed.flag', 'w') as f:
                    f.write(str(time.time()))
                print("Created pedestrian button flag file")
            except Exception as e:
                print(f"Error creating flag file: {e}")
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "message": "Pedestrian cross signal received"}).encode())
        
        elif self.path == '/api/generate_pedestrians':
            # 处理生成行人请求
            print("收到生成行人请求!")
            try:
                # 通过调用主仿真系统生成行人
                import subprocess
                import sys
                
                # 运行快速命令向仿真添加更多行人
                # 这将触发主仿真添加更多行人
                result = subprocess.run([
                    sys.executable, '-c', 
                    '''
import random
import json
import time
import os

# 生成新的行人数据
new_pedestrians = []
for i in range(random.randint(2, 5)):  # 生成2-5个新行人
    ped_id = f"web_gen_{int(time.time())}_{i}"
    new_ped = {
        "id": ped_id,
        "x": random.randint(550, 650),
        "y": random.randint(350, 470),
        "intent_prob": random.uniform(0.3, 0.9),
        "is_crossing": False,
        "anomaly": random.random() < 0.1,
        "priority": random.choice(["normal", "medium", "high"])
    }
    new_pedestrians.append(new_ped)

# 尝试追加到现有数据或创建新数据
try:
    if os.path.exists("3d_sync_data.json"):
        with open("3d_sync_data.json", "r") as f:
            data = json.load(f)
    else:
        data = {"pedestrians": [], "vehicles": [], "traffic_lights": {"vehicle": "RED", "pedestrian": "DONT_WALK"}}
    
    # 添加新行人
    existing_ids = {p["id"] for p in data.get("pedestrians", [])}
    for ped in new_pedestrians:
        if ped["id"] not in existing_ids:
            data["pedestrians"].append(ped)
    
    # 更新时间戳
    data["timestamp"] = time.time()
    
    with open("3d_sync_data.json", "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"生成了 {len(new_pedestrians)} 个新行人")
except Exception as e:
    print(f"生成行人时出错: {e}")
                    '''
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    print("成功生成新行人")
                    response_data = {"status": "success", "message": "新行人已生成"}
                else:
                    print(f"生成行人时出错: {result.stderr}")
                    response_data = {"status": "error", "message": "生成行人失败"}
                    
            except Exception as e:
                print(f"generate_pedestrians出错: {e}")
                response_data = {"status": "error", "message": str(e)}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode())
        
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": "Endpoint not found"}).encode())

    def load_simulation_data(self):
        """Load current simulation data"""
        try:
            if os.path.exists('3d_sync_data.json'):
                with open('3d_sync_data.json', 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading data: {e}")
        
        return {
            "timestamp": time.time(),
            "traffic_lights": {"vehicle": "RED", "pedestrian": "DONT_WALK"},
            "pedestrians": [],
            "vehicles": [],
            "ai_decisions": {}
        }

def create_html_page():
    """Create the HTML page with Three.js simulation"""
    html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PI-BREPSC 3D Traffic Simulation</title>
    <link rel="icon" href="data:," type="image/x-icon">
    <style>
        body {
            margin: 0;
            padding: 0;
            overflow: hidden;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: 'Arial', sans-serif;
        }
        #container {
            position: relative;
            width: 100vw;
            height: 100vh;
        }
        #info {
            position: absolute;
            top: 20px;
            left: 20px;
            color: white;
            background: rgba(0,0,0,0.8);
            padding: 20px;
            border-radius: 10px;
            font-size: 14px;
            z-index: 100;
            max-width: 350px;
            max-height: 80vh;
            overflow-y: auto;
            line-height: 1.4;
        }
        #controls {
            position: absolute;
            top: 20px;
            right: 20px;
            color: white;
            background: rgba(0,0,0,0.8);
            padding: 15px;
            border-radius: 10px;
            z-index: 100;
            max-width: 200px;
        }
        .status {
            margin: 5px 0;
        }
        .high-intent { color: #ff4444; }
        .medium-intent { color: #ffaa00; }
        .low-intent { color: #44ff44; }
    </style>
</head>
<body>
    <div id="container">
        <div id="info">
            <h3>❤️ PI-BREPSC 3D 交通仿真系统</h3>
            <div id="traffic-lights"></div>
            <div id="selected-pedestrian"></div>
            <div id="vehicle-count"></div>
        </div>
        <div id="controls">
            <h4>🚶 手动控制</h4>
            <button id="pedestrian-cross-button" style="background-color: #4CAF50; color: white; padding: 10px 15px; border: none; border-radius: 5px; pointer-events: auto; margin-bottom: 10px; width: 100%;">行人过街按钮</button>
            <button id="reset-view-button" style="background-color: #4CAF50; color: white; padding: 10px 15px; border: none; border-radius: 5px; pointer-events: auto; width: 100%;">重置视角</button>
            <p style="font-size: 12px; margin-top: 10px;">更新#51</p>
        </div>
    </div>

    <!-- Three.js CDN -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        console.log('PI-BREPSC 3D仿真系统启动中...');
        // 手动实现轨道控制器以提高兼容性
        THREE.OrbitControls = function(camera, domElement) {
            this.camera = camera;
            this.domElement = domElement || document;
            this.enableDamping = true;
            this.dampingFactor = 0.05;
            this.enableZoom = true;
            this.enableRotate = true;
            this.enablePan = true;
            
            var scope = this;
            var rotateSpeed = 1.0;
            var zoomSpeed = 1.0;
            
            var spherical = new THREE.Spherical();
            var sphericalDelta = new THREE.Spherical();
            var scale = 1;
            
            var rotateStart = new THREE.Vector2();
            var rotateEnd = new THREE.Vector2();
            var rotateDelta = new THREE.Vector2();
            
            var panStart = new THREE.Vector2();
            var panEnd = new THREE.Vector2();
            var panDelta = new THREE.Vector2();
            
            var offset = new THREE.Vector3();
            var target = new THREE.Vector3();
            
            function onMouseDown(event) {
                if (event.button === 0) {
                    rotateStart.set(event.clientX, event.clientY);
                    document.addEventListener('mousemove', onMouseMove);
                    document.addEventListener('mouseup', onMouseUp);
                }
            }
            
            function onMouseMove(event) {
                rotateEnd.set(event.clientX, event.clientY);
                rotateDelta.subVectors(rotateEnd, rotateStart).multiplyScalar(rotateSpeed);
                
                var element = scope.domElement;
                sphericalDelta.theta -= 2 * Math.PI * rotateDelta.x / element.clientWidth;
                sphericalDelta.phi -= 2 * Math.PI * rotateDelta.y / element.clientHeight;
                
                rotateStart.copy(rotateEnd);
                scope.update();
            }
            
            function onMouseUp() {
                document.removeEventListener('mousemove', onMouseMove);
                document.removeEventListener('mouseup', onMouseUp);
            }
            
            function onMouseWheel(event) {
                if (event.deltaY < 0) {
                    scale /= Math.pow(0.95, zoomSpeed);
                } else if (event.deltaY > 0) {
                    scale *= Math.pow(0.95, zoomSpeed);
                }
                scope.update();
            }
            
            this.update = function() {
                offset.copy(camera.position).sub(target);
                spherical.setFromVector3(offset);
                
                spherical.theta += sphericalDelta.theta;
                spherical.phi += sphericalDelta.phi;
                spherical.radius *= scale;
                
                spherical.phi = Math.max(0.1, Math.min(Math.PI - 0.1, spherical.phi));
                spherical.radius = Math.max(1, Math.min(200, spherical.radius));
                
                offset.setFromSpherical(spherical);
                camera.position.copy(target).add(offset);
                camera.lookAt(target);
                
                if (scope.enableDamping) {
                    sphericalDelta.theta *= (1 - scope.dampingFactor);
                    sphericalDelta.phi *= (1 - scope.dampingFactor);
                } else {
                    sphericalDelta.set(0, 0, 0);
                }
                scale = 1;
            };
            
            this.dispose = function() {
                scope.domElement.removeEventListener('mousedown', onMouseDown);
                scope.domElement.removeEventListener('wheel', onMouseWheel);
            };
            
            // Add event listeners
            scope.domElement.addEventListener('mousedown', onMouseDown);
            scope.domElement.addEventListener('wheel', onMouseWheel);
            
            // Initialize
            offset.copy(camera.position);
            spherical.setFromVector3(offset);
        };
    </script>
    
    <script>
        console.log('Main JavaScript block started.');
        // Global variables
        let scene, camera, renderer, controls;
        let trafficLights = [];
        let rsuSensors = [];
        let pedestrians = [];
        let vehicles = [];
        
        // Initialize Three.js
        function initThreeJS() {
            console.log('Initializing Three.js...');
            
            // Scene setup
            scene = new THREE.Scene();
            scene.fog = new THREE.Fog(0xcccccc, 10, 500);
            
            // Camera setup
            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(30, 40, 30);
            
            // Renderer setup
            renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setClearColor(0x87CEEB, 1); // Sky blue background
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;
            
            // 添加到容器
            const container = document.getElementById('container');
            if (container) {
                container.appendChild(renderer.domElement);
                console.log('渲染器已添加到容器');
            } else {
                console.error('未找到容器!');
                return false;
            }
            
            return true;
        }

        // Initialize scene components
        function initScene() {
            console.log('Setting up scene...');
            
            // Camera controls
            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
            controls.target.set(0, 0, 0);

            // Lighting
            const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
            scene.add(ambientLight);

            const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
            directionalLight.position.set(50, 100, 50);
            directionalLight.castShadow = true;
            directionalLight.shadow.mapSize.width = 2048;
            directionalLight.shadow.mapSize.height = 2048;
            directionalLight.shadow.camera.near = 0.5;
            directionalLight.shadow.camera.far = 500;
            directionalLight.shadow.camera.left = -100;
            directionalLight.shadow.camera.right = 100;
            directionalLight.shadow.camera.top = 100;
            directionalLight.shadow.camera.bottom = -100;
            scene.add(directionalLight);
            
            console.log('Scene lighting set up');
        }

                 // Create environment
         function createEnvironment() {
             // Ground - realistic asphalt and grass texture
             const groundGeometry = new THREE.PlaneGeometry(200, 200);
             const groundMaterial = new THREE.MeshLambertMaterial({ color: 0x90EE90 });
             const ground = new THREE.Mesh(groundGeometry, groundMaterial);
             ground.rotation.x = -Math.PI / 2;
             ground.receiveShadow = true;
             scene.add(ground);

             // Roads with lane markings
             const roadMaterial = new THREE.MeshLambertMaterial({ color: 0x333333 });
             
             // Horizontal road
             const hRoadGeometry = new THREE.PlaneGeometry(100, 20);
             const hRoad = new THREE.Mesh(hRoadGeometry, roadMaterial);
             hRoad.rotation.x = -Math.PI / 2;
             hRoad.position.y = 0.01;
             scene.add(hRoad);

             // Vertical road
             const vRoadGeometry = new THREE.PlaneGeometry(20, 100);
             const vRoad = new THREE.Mesh(vRoadGeometry, roadMaterial);
             vRoad.rotation.x = -Math.PI / 2;
             vRoad.position.y = 0.01;
             scene.add(vRoad);

             // Lane markings
             const laneMarkingMaterial = new THREE.MeshLambertMaterial({ color: 0xffff00 });
             // Horizontal road center line
             for (let i = -40; i <= 40; i += 4) {
                 const marking = new THREE.Mesh(
                     new THREE.PlaneGeometry(2, 0.3),
                     laneMarkingMaterial
                 );
                 marking.rotation.x = -Math.PI / 2;
                 marking.position.set(i, 0.02, 0);
                 scene.add(marking);
             }
             // Vertical road center line
             for (let i = -40; i <= 40; i += 4) {
                 const marking = new THREE.Mesh(
                     new THREE.PlaneGeometry(0.3, 2),
                     laneMarkingMaterial
                 );
                 marking.rotation.x = -Math.PI / 2;
                 marking.position.set(0, 0.02, i);
                 scene.add(marking);
             }

             // Crosswalks with zebra stripes
             const crosswalkMaterial = new THREE.MeshLambertMaterial({ color: 0xffffff });
             
             // Horizontal crosswalk zebra stripes
             for (let i = -8; i <= 8; i += 2) {
                 const stripe = new THREE.Mesh(
                     new THREE.PlaneGeometry(1.5, 20),
                     crosswalkMaterial
                 );
                 stripe.rotation.x = -Math.PI / 2;
                 stripe.position.set(i, 0.02, 0);
                 scene.add(stripe);
             }
             
             // Vertical crosswalk zebra stripes  
             for (let i = -8; i <= 8; i += 2) {
                 const stripe = new THREE.Mesh(
                     new THREE.PlaneGeometry(20, 1.5),
                     crosswalkMaterial
                 );
                 stripe.rotation.x = -Math.PI / 2;
                 stripe.position.set(0, 0.02, i);
                 scene.add(stripe);
             }

             // Sidewalks
             const sidewalkMaterial = new THREE.MeshLambertMaterial({ color: 0x888888 });
             // North sidewalk
             const nSidewalk = new THREE.Mesh(
                 new THREE.PlaneGeometry(60, 5),
                 sidewalkMaterial
             );
             nSidewalk.rotation.x = -Math.PI / 2;
             nSidewalk.position.set(0, 0.05, 15);
             scene.add(nSidewalk);
             
             // South sidewalk
             const sSidewalk = new THREE.Mesh(
                 new THREE.PlaneGeometry(60, 5),
                 sidewalkMaterial
             );
             sSidewalk.rotation.x = -Math.PI / 2;
             sSidewalk.position.set(0, 0.05, -15);
             scene.add(sSidewalk);
             
             // East sidewalk
             const eSidewalk = new THREE.Mesh(
                 new THREE.PlaneGeometry(5, 60),
                 sidewalkMaterial
             );
             eSidewalk.rotation.x = -Math.PI / 2;
             eSidewalk.position.set(15, 0.05, 0);
             scene.add(eSidewalk);
             
             // West sidewalk
             const wSidewalk = new THREE.Mesh(
                 new THREE.PlaneGeometry(5, 60),
                 sidewalkMaterial
             );
             wSidewalk.rotation.x = -Math.PI / 2;
             wSidewalk.position.set(-15, 0.05, 0);
             scene.add(wSidewalk);

             // Buildings with more detail
             const buildingPositions = [
                 { x: -40, z: -40, height: 25, color: 0x888899, windows: true },
                 { x: 40, z: -40, height: 30, color: 0x999988, windows: true },
                 { x: -40, z: 40, height: 20, color: 0x889988, windows: true },
                 { x: 40, z: 40, height: 35, color: 0x998899, windows: true }
             ];

             buildingPositions.forEach(pos => {
                 const geometry = new THREE.BoxGeometry(15, pos.height, 15);
                 const material = new THREE.MeshLambertMaterial({ color: pos.color });
                 const building = new THREE.Mesh(geometry, material);
                 building.position.set(pos.x, pos.height / 2, pos.z);
                 building.castShadow = true;
                 scene.add(building);
                 
                 // Add windows
                 if (pos.windows) {
                     const windowMaterial = new THREE.MeshLambertMaterial({ color: 0x4444ff });
                     for (let floor = 2; floor < pos.height; floor += 3) {
                         for (let i = -5; i <= 5; i += 3) {
                             // Front windows
                             const window1 = new THREE.Mesh(
                                 new THREE.PlaneGeometry(1, 1.5),
                                 windowMaterial
                             );
                             window1.position.set(pos.x + i, floor, pos.z + 7.6);
                             scene.add(window1);
                             
                             // Side windows
                             const window2 = new THREE.Mesh(
                                 new THREE.PlaneGeometry(1, 1.5),
                                 windowMaterial
                             );
                             window2.position.set(pos.x + 7.6, floor, pos.z + i);
                             window2.rotation.y = Math.PI / 2;
                             scene.add(window2);
                         }
                     }
                 }
             });

             // Traffic lights and RSU sensors
             createTrafficLights();
             createRSUSensors();
         }

        function createTrafficLights() {
            const positions = [
                { x: 12, z: 12, rotation: Math.PI * 1.25 },      // NE corner
                { x: -12, z: 12, rotation: Math.PI * 0.75 },     // NW corner  
                { x: 12, z: -12, rotation: Math.PI * 1.75 },     // SE corner
                { x: -12, z: -12, rotation: Math.PI * 0.25 }     // SW corner
            ];

            positions.forEach((pos, index) => {
                // Base foundation
                const baseGeometry = new THREE.CylinderGeometry(1, 1, 0.3);
                const baseMaterial = new THREE.MeshLambertMaterial({ color: 0x555555 });
                const base = new THREE.Mesh(baseGeometry, baseMaterial);
                base.position.set(pos.x, 0.15, pos.z);
                scene.add(base);

                // Pole
                const poleGeometry = new THREE.CylinderGeometry(0.15, 0.15, 6);
                const poleMaterial = new THREE.MeshLambertMaterial({ color: 0x444444 });
                const pole = new THREE.Mesh(poleGeometry, poleMaterial);
                pole.position.set(pos.x, 3.3, pos.z);
                pole.castShadow = true;
                scene.add(pole);

                // Horizontal arm
                const armGeometry = new THREE.CylinderGeometry(0.08, 0.08, 4);
                const armMaterial = new THREE.MeshLambertMaterial({ color: 0x444444 });
                const arm = new THREE.Mesh(armGeometry, armMaterial);
                arm.position.set(pos.x - 2 * Math.cos(pos.rotation), 6, pos.z - 2 * Math.sin(pos.rotation));
                arm.rotation.z = Math.PI / 2;
                arm.rotation.y = pos.rotation;
                scene.add(arm);

                // Light housing - main traffic light
                const housingGeometry = new THREE.BoxGeometry(0.8, 2.4, 0.4);
                const housingMaterial = new THREE.MeshLambertMaterial({ color: 0x222222 });
                const housing = new THREE.Mesh(housingGeometry, housingMaterial);
                housing.position.set(
                    pos.x - 3.5 * Math.cos(pos.rotation),
                    5.5,
                    pos.z - 3.5 * Math.sin(pos.rotation)
                );
                housing.rotation.y = pos.rotation;
                housing.castShadow = true;
                scene.add(housing);

                // Traffic lights with proper positioning
                const lightPositions = [
                    { y: 6.3, color: 0xff0000, type: 'red' },
                    { y: 5.5, color: 0xffff00, type: 'yellow' },
                    { y: 4.7, color: 0x00ff00, type: 'green' }
                ];

                lightPositions.forEach(lightPos => {
                    // Light lens
                    const light = new THREE.Mesh(
                        new THREE.SphereGeometry(0.25),
                        new THREE.MeshLambertMaterial({
                            color: lightPos.type === 'red' ? lightPos.color : 0x333333,
                            emissive: lightPos.type === 'red' ? 0x330000 : 0x000000
                        })
                    );
                    light.position.set(
                        pos.x - 3.5 * Math.cos(pos.rotation) + 0.25 * Math.cos(pos.rotation),
                        lightPos.y,
                        pos.z - 3.5 * Math.sin(pos.rotation) + 0.25 * Math.sin(pos.rotation)
                    );
                    light.userData = { type: lightPos.type, id: index, corner: index };
                    light.name = 'traffic_light_' + lightPos.type + '_' + index;
                    scene.add(light);
                    trafficLights.push(light);

                    // Light glow effect
                    if (lightPos.type === 'red') {
                        const glowLight = new THREE.PointLight(lightPos.color, 0.5, 10);
                        glowLight.position.copy(light.position);
                        scene.add(glowLight);
                        light.userData.glowLight = glowLight;
                    }
                });

                // Pedestrian signal
                const pedHousingGeometry = new THREE.BoxGeometry(0.4, 0.6, 0.3);
                const pedHousing = new THREE.Mesh(pedHousingGeometry, housingMaterial);
                pedHousing.position.set(
                    pos.x - 1.5 * Math.cos(pos.rotation),
                    2.5,
                    pos.z - 1.5 * Math.sin(pos.rotation)
                );
                pedHousing.rotation.y = pos.rotation + Math.PI;
                scene.add(pedHousing);

                // Pedestrian walk/don't walk lights
                const walkLight = new THREE.Mesh(
                    new THREE.PlaneGeometry(0.2, 0.2),
                    new THREE.MeshLambertMaterial({ color: 0x00ff00, emissive: 0x003300 })
                );
                walkLight.position.set(
                    pos.x - 1.5 * Math.cos(pos.rotation) + 0.05,
                    2.6,
                    pos.z - 1.5 * Math.sin(pos.rotation) + 0.05
                );
                walkLight.rotation.y = pos.rotation + Math.PI;
                walkLight.userData = { type: 'walk', id: index, corner: index };
                walkLight.name = 'ped_light_walk_' + index;
                scene.add(walkLight);
                trafficLights.push(walkLight);

                const dontWalkLight = new THREE.Mesh(
                    new THREE.PlaneGeometry(0.2, 0.2),
                    new THREE.MeshLambertMaterial({ color: 0xff0000, emissive: 0x330000 })
                );
                dontWalkLight.position.set(
                    pos.x - 1.5 * Math.cos(pos.rotation) + 0.05,
                    2.4,
                    pos.z - 1.5 * Math.sin(pos.rotation) + 0.05
                );
                dontWalkLight.rotation.y = pos.rotation + Math.PI;
                dontWalkLight.userData = { type: 'dontwalk', id: index, corner: index };
                dontWalkLight.name = 'ped_light_dontwalk_' + index;
                scene.add(dontWalkLight);
                trafficLights.push(dontWalkLight);
            });
            console.log('Traffic lights created');
        }

        function createRSUSensors() {
            const rsuPositions = [
                { x: 10, z: 10, rotation: Math.PI * 1.25 },
                { x: -10, z: 10, rotation: Math.PI * 0.75 },
                { x: 10, z: -10, rotation: Math.PI * 1.75 },
                { x: -10, z: -10, rotation: Math.PI * 0.25 }
            ];

            rsuPositions.forEach((pos, index) => {
                const rsuGeometry = new THREE.BoxGeometry(0.5, 2, 0.5);
                const rsuMaterial = new THREE.MeshLambertMaterial({ color: 0x0000ff });
                const rsu = new THREE.Mesh(rsuGeometry, rsuMaterial);
                rsu.position.set(pos.x, 1, pos.z);
                rsu.userData = { id: index, type: 'rsu', active: false };
                rsu.name = 'rsu_sensor_' + index;
                scene.add(rsu);
                rsuSensors.push(rsu);
            });
            console.log('RSU sensors created');
        }

        // Create a simple vehicle mesh
        function createVehicleMesh(color) {
            const bodyGeometry = new THREE.BoxGeometry(1.5, 0.8, 3);
            const bodyMaterial = new THREE.MeshLambertMaterial({ color: color });
            const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
            body.castShadow = true;

            const cabinGeometry = new THREE.BoxGeometry(1, 0.7, 1.5);
            const cabinMaterial = new THREE.MeshLambertMaterial({ color: 0xaaaaaa });
            const cabin = new THREE.Mesh(cabinGeometry, cabinMaterial);
            cabin.position.set(0, 0.75, 0.5);
            cabin.castShadow = true;
            body.add(cabin);

            return body;
        }

        // Create a simple pedestrian mesh
        function createPedestrianMesh(color) {
            const bodyGeometry = new THREE.CylinderGeometry(0.3, 0.3, 1.8);
            const bodyMaterial = new THREE.MeshLambertMaterial({ color: color });
            const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
            body.castShadow = true;
            body.position.y = 0.9; // Half of height to sit on ground

            return body;
        }

        // Update simulation state based on data from Python backend
        async function updateSimulation() {
            try {
                const response = await fetch('/api/traffic_data');
                const data = await response.json();

                // Update traffic lights
                trafficLights.forEach(light => {
                    const lightState = data.traffic_lights[light.userData.type === 'red' || light.userData.type === 'yellow' || light.userData.type === 'green' ? 'vehicle' : 'pedestrian'];
                    
                    let isActive = false;
                    if (light.userData.type === 'red' && lightState === 'RED') isActive = true;
                    if (light.userData.type === 'yellow' && lightState === 'YELLOW') isActive = true;
                    if (light.userData.type === 'green' && lightState === 'GREEN') isActive = true;
                    if (light.userData.type === 'walk' && lightState === 'WALK') isActive = true;
                    if (light.userData.type === 'dontwalk' && lightState === 'DONT_WALK') isActive = true;

                    if (isActive) {
                        light.material.color.set(light.userData.color);
                        if (light.userData.glowLight) light.userData.glowLight.intensity = 0.5;
                    } else {
                        light.material.color.set(0x333333); // Dim color
                        if (light.userData.glowLight) light.userData.glowLight.intensity = 0;
                    }
                });

                // Update pedestrians
                const currentPedestrianIds = new Set(data.pedestrians.map(p => p.id));
                pedestrians = pedestrians.filter(p => {
                    if (!currentPedestrianIds.has(p.userData.id)) {
                        scene.remove(p);
                        return false;
                    }
                    return true;
                });

                data.pedestrians.forEach(pData => {
                    let pedestrian = pedestrians.find(p => p.userData.id === pData.id);
                    if (!pedestrian) {
                        pedestrian = createPedestrianMesh(pData.color || 0x00ff00);
                        pedestrian.userData = { id: pData.id, type: 'pedestrian', intent: pData.intent };
                        scene.add(pedestrian);
                        pedestrians.push(pedestrian);
                    }
                    pedestrian.position.set(pData.position[0], pData.position[1], pData.position[2]);
                    pedestrian.rotation.y = pData.rotation;
                    pedestrian.userData.intent = pData.intent;
                });

                // Update vehicles
                const currentVehicleIds = new Set(data.vehicles.map(v => v.id));
                vehicles = vehicles.filter(v => {
                    if (!currentVehicleIds.has(v.userData.id)) {
                        scene.remove(v);
                        return false;
                    }
                    return true;
                });

                data.vehicles.forEach(vData => {
                    let vehicle = vehicles.find(v => v.userData.id === vData.id);
                    if (!vehicle) {
                        vehicle = createVehicleMesh(vData.color || 0xff0000);
                        vehicle.userData = { id: vData.id, type: 'vehicle', intent: vData.intent };
                        scene.add(vehicle);
                        vehicles.push(vehicle);
                    }
                    vehicle.position.set(vData.position[0], vData.position[1], vData.position[2]);
                    vehicle.rotation.y = vData.rotation;
                    vehicle.userData.intent = vData.intent;
                });

                // Update RSU sensors (visualize active/inactive)
                rsuSensors.forEach(rsu => {
                    const rsuData = data.rsu_sensors.find(s => s.id === rsu.userData.id);
                    if (rsuData) {
                        rsu.userData.active = rsuData.active;
                        rsu.material.color.set(rsuData.active ? 0x00ff00 : 0x0000ff); // Green if active, blue if inactive
                    }
                });

                // Update info panel
                updateInfoPanel(data);

            } catch (error) {
                console.error('获取仿真数据失败:', error);
            }
        }

        function updateInfoPanel(data) {
            const infoPanel = document.getElementById('info');
            if (!infoPanel) return;

            let html = '<h3>❤️ PI-BREPSC 3D 交通仿真系统</h3>';

            // Traffic Lights
            html += '<h4>🚦 交通灯状态</h4>';
            html += `<div id="traffic-lights">车辆: ${data.traffic_lights.vehicle} | 行人: ${data.traffic_lights.pedestrian}</div>`;

            // Pedestrian Info
            html += '<h4>🚶 行人信息</h4>';
            if (data.pedestrians && data.pedestrians.length > 0) {
                data.pedestrians.forEach(p => {
                    const intentClass = p.intent === 'high' ? 'high-intent' : p.intent === 'medium' ? 'medium-intent' : 'low-intent';
                    html += `<div class="status">ID: ${p.id}, 意图: <span class="${intentClass}">${p.intent}</span>, 位置: (${p.position[0].toFixed(1)}, ${p.position[2].toFixed(1)})</div>`;
                });
            } else {
                html += '<div class="status">无行人</div>';
            }

            // Vehicle Count
            html += '<h4>🚗 车辆信息</h4>';
            html += `<div id="vehicle-count">当前车辆数: ${data.vehicles ? data.vehicles.length : 0}</div>`;
            if (data.vehicles && data.vehicles.length > 0) {
                data.vehicles.forEach(v => {
                    const intentClass = v.intent === 'high' ? 'high-intent' : v.intent === 'medium' ? 'medium-intent' : 'low-intent';
                    html += `<div class="status">ID: ${v.id}, 意图: <span class="${intentClass}">${v.intent}</span>, 位置: (${v.position[0].toFixed(1)}, ${v.position[2].toFixed(1)})</div>`;
                });
            }

            // AI Decisions
            html += '<h4>🧠 AI 决策</h4>';
            if (data.ai_decisions && Object.keys(data.ai_decisions).length > 0) {
                for (const [key, value] of Object.entries(data.ai_decisions)) {
                    html += `<div class="status">${key}: ${JSON.stringify(value)}</div>`;
                }
            } else {
                html += '<div class="status">无AI决策</div>';
            }

            infoPanel.innerHTML = html;
        }

        // Handle pedestrian cross button click
        document.getElementById('pedestrian-cross-button').addEventListener('click', async () => {
            console.log('Pedestrian cross button clicked!');
            try {
                const response = await fetch('/api/pedestrian_cross', { method: 'POST' });
                const result = await response.json();
                console.log('Pedestrian cross signal response:', result);
                // Optionally update UI based on response
            } catch (error) {
                console.error('Error sending pedestrian cross signal:', error);
            }
        });

        // Handle reset view button click
        document.getElementById('reset-view-button').addEventListener('click', () => {
            camera.position.set(30, 40, 30);
            controls.target.set(0, 0, 0);
            controls.update();
        });

        // Animation loop
        function animate() {
            requestAnimationFrame(animate);
            controls.update(); // 仅当启用阻尼或自动旋转时需要
            renderer.render(scene, camera);
        }

        // Main initialization
        window.onload = () => {
            if (initThreeJS()) {
                initScene();
                createEnvironment();
                animate();
                setInterval(updateSimulation, 1000); // Update simulation data every second
            } else {
                console.error('Three.js初始化失败。无法继续设置场景。');
            }
        };
    </script>
</body>
</html>
'''

class ThreadingHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

def run_server(handler_class, port=8001):
    server_address = ('', port)
    httpd = ThreadingHTTPServer(server_address, handler_class)
    print(f"Serving HTTP on port {port}...")
    webbrowser.open(f"http://localhost:{port}/index.html")
    httpd.serve_forever()

if __name__ == '__main__':
    # Ensure the HTML file is created/updated
    create_html_page()
    
    # Start the HTTP server in a separate thread
    server_thread = threading.Thread(target=run_server, args=(TrafficSimulationHandler,))
    server_thread.daemon = True
    server_thread.start()

    # Keep the main thread alive to prevent daemon threads from exiting
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Server stopped.")