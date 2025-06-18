#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PI-BREPSC 3D 交通仿真系统 - 修正版
根据主仿真系统的布局和逻辑重新设计
"""

import http.server
import socketserver
import json
import webbrowser
import os
import sys
import pickle
import time
from datetime import datetime

class TrafficSimulationHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(create_html_page().encode('utf-8'))
        elif self.path == '/api/traffic_data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # 读取仿真数据
            data = load_simulation_data()
            self.wfile.write(json.dumps(data).encode())
        else:
            super().do_GET()

def load_simulation_data():
    """加载仿真数据 - 从JSON文件读取实时数据"""
    try:
        # 从正确的JSON文件读取数据
        if os.path.exists('3d_sync_data.json'):
            with open('3d_sync_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return format_json_data(data)
    except Exception as e:
        print(f"读取数据错误: {e}")
    
    # 返回默认数据结构（匹配main_simulation.py的初始状态）
    # 基于config.py的真实坐标系统：交集中心(600,400)
    return {
        'timestamp': time.time(),
        'traffic_light': {
            'vehicle_phase': 'green',  # green, yellow, red
            'pedestrian_phase': 'dont_walk',  # walk, dont_walk
            'time_remaining': 10
        },
        'vehicles': [
            # 车辆在垂直道路中心行驶，从北向南 (x=600为道路中心线)
            {'id': 'V1', 'x': 600, 'y': 50, 'speed': 2, 'direction': 'vertical', 'dx': 0, 'dy': 1},
            {'id': 'V2', 'x': 600, 'y': 150, 'speed': 2, 'direction': 'vertical', 'dx': 0, 'dy': 1},
            {'id': 'V3', 'x': 600, 'y': 250, 'speed': 2, 'direction': 'vertical', 'dx': 0, 'dy': 1}
        ],
        'pedestrians': [
            # 行人在等待区内 - 基于真实坐标
            # 西侧等待区: WAIT_AREA_WEST (x: 450-550, y: 330-470, center: 500,400)
            {'id': 'P1', 'x': 480, 'y': 380, 'target_area': 'WAIT_AREA_WEST', 'state': 'waiting', 'is_crossing': False, 'intent_prob': 0.3},
            {'id': 'P2', 'x': 520, 'y': 420, 'target_area': 'WAIT_AREA_WEST', 'state': 'waiting', 'is_crossing': False, 'intent_prob': 0.6},
            # 东侧等待区: WAIT_AREA_EAST (x: 650-750, y: 330-470, center: 700,400)
            {'id': 'P3', 'x': 680, 'y': 390, 'target_area': 'WAIT_AREA_EAST', 'state': 'waiting', 'is_crossing': False, 'intent_prob': 0.9},
            {'id': 'P4', 'x': 720, 'y': 410, 'target_area': 'WAIT_AREA_EAST', 'state': 'waiting', 'is_crossing': False, 'intent_prob': 0.7}
        ],
        'rsu_status': {
            'detections': 4,
            'high_priority': 2,
            'edge_processing': True
        },
        'ai_decisions': {
            'system_status': 'active',
            'total_pedestrians': 4
        }
    }

def format_json_data(json_data):
    """将JSON数据转换为3D系统需要的格式"""
    try:
        # 提取交通信号数据
        traffic_lights = json_data.get('traffic_lights', {})
        
        # 转换车辆数据
        vehicles = []
        for v_data in json_data.get('vehicles', []):
            vehicles.append({
                'id': v_data.get('id', 'Unknown'),
                'x': v_data.get('x', 600),
                'y': v_data.get('y', 100),
                'speed': v_data.get('speed', 2),
                'direction': 'vertical',
                'dx': v_data.get('dx', 0),
                'dy': v_data.get('dy', 1)
            })
        
        # 转换行人数据
        pedestrians = []
        for p_data in json_data.get('pedestrians', []):
            # 根据位置判断等待区域
            x_pos = p_data.get('x', 500)
            target_area = 'WAIT_AREA_WEST' if x_pos < 600 else 'WAIT_AREA_EAST'
            
            # 根据is_crossing判断状态
            is_crossing = p_data.get('is_crossing', False)
            state = 'crossing' if is_crossing else 'waiting'
            
            pedestrians.append({
                'id': p_data.get('id', 'Unknown'),
                'x': x_pos,
                'y': p_data.get('y', 400),
                'target_area': target_area,
                'state': state,
                'is_crossing': is_crossing,
                'intent_prob': p_data.get('intent_prob', 0.5),
                'anomaly': p_data.get('anomaly', False),
                'priority': p_data.get('priority', 'normal')
            })
        
        # 获取AI决策数据
        ai_decisions = json_data.get('ai_decisions', {})
        
        return {
            'timestamp': json_data.get('timestamp', time.time()),
            'traffic_light': {
                'vehicle_phase': traffic_lights.get('vehicle', 'green').lower(),
                'pedestrian_phase': traffic_lights.get('pedestrian', 'dont_walk').lower(),
                'time_remaining': 10
            },
            'vehicles': vehicles,
            'pedestrians': pedestrians,
            'rsu_status': {
                'detections': ai_decisions.get('rsu_detections', len(pedestrians)),
                'high_priority': ai_decisions.get('high_priority_count', 0),
                'edge_processing': ai_decisions.get('edge_processing', True)
            },
            'ai_decisions': ai_decisions
        }
    except Exception as e:
        print(f"格式化数据错误: {e}")
        return None

def create_html_page():
    """创建完整的HTML页面 - 匹配主仿真系统布局"""
    return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PI-BREPSC 3D 交通仿真系统</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Microsoft YaHei', 'SimSun', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            overflow: hidden;
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
            background: rgba(0,0,0,0.85);
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
            z-index: 100;
            min-width: 320px;
        }
        .title {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 15px;
            color: #00ff88;
            text-shadow: 0 0 10px rgba(0,255,136,0.5);
        }
        .section {
            margin-bottom: 15px;
            padding: 10px;
            background: rgba(255,255,255,0.1);
            border-radius: 8px;
            border-left: 4px solid #00ff88;
        }
        .section h4 {
            color: #88ff88;
            margin-bottom: 8px;
            font-size: 16px;
        }
        .status-item {
            display: flex;
            justify-content: space-between;
            margin: 5px 0;
            font-size: 14px;
        }
        .status-value {
            font-weight: bold;
            color: #ffff88;
        }
        .manual-controls {
            position: absolute;
            bottom: 20px;
            right: 20px;
            background: rgba(0,0,0,0.85);
            padding: 20px;
            border-radius: 15px;
            z-index: 100;
            color: white;
        }
        .btn {
            display: block;
            width: 100%;
            margin: 10px 0;
            padding: 12px 20px;
            background: linear-gradient(45deg, #00ff88, #00cc66);
            border: none;
            border-radius: 8px;
            color: white;
            font-size: 14px;
            pointer-events: auto;
            transition: all 0.3s ease;
            text-shadow: 0 1px 2px rgba(0,0,0,0.3);
        }
        .btn:hover {
            background: linear-gradient(45deg, #00cc66, #009944);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,255,136,0.3);
        }
        .ped-item {
            margin: 8px 0;
            padding: 8px;
            background: rgba(255,255,255,0.1);
            border-radius: 6px;
            border-left: 3px solid #4CAF50;
        }
        .vehicle-item {
            margin: 8px 0;
            padding: 8px;
            background: rgba(255,255,255,0.1);
            border-radius: 6px;
            border-left: 3px solid #2196F3;
        }
        .light-status {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: bold;
            text-transform: uppercase;
        }
        .light-green { background: #4CAF50; color: white; }
        .light-yellow { background: #FF9800; color: white; }
        .light-red { background: #F44336; color: white; }
        .light-walk { background: #4CAF50; color: white; }
        .light-dont-walk { background: #F44336; color: white; }
        .ped-item {
            pointer-events: auto;
        }
        .vehicle-item {
            pointer-events: auto;
        }
    </style>
</head>
<body>
    <div id="container"></div>
    
    <div id="info">
        <div class="title">❤️ PI-BREPSC 3D 交通仿真系统</div>
        
        <div class="section">
            <h4>🚦 交通灯状态</h4>
            <div class="status-item">
                <span>车辆信号:</span>
                <span id="vehicle-signal" class="status-value light-status">GREEN</span>
            </div>
            <div class="status-item">
                <span>行人信号:</span>
                <span id="pedestrian-signal" class="status-value light-status">DONT_WALK</span>
            </div>
        </div>

        <div class="section">
            <h4>🚶 行人检测</h4>
            <div class="status-item">
                <span>检测到:</span>
                <span id="pedestrian-count" class="status-value">4 名行人</span>
            </div>
            <div id="pedestrian-list"></div>
        </div>

        <div class="section">
            <h4>🚗 车辆状态</h4>
            <div class="status-item">
                <span>活跃车辆:</span>
                <span id="vehicle-count" class="status-value">3 辆</span>
            </div>
            <div id="vehicle-list"></div>
        </div>

        <div class="section">
            <h4>📡 RSU 数据</h4>
            <div class="status-item">
                <span>扫描状态:</span>
                <span id="rsu-scans" class="status-value">4 个传感器</span>
            </div>
            <div class="status-item">
                <span>信号请求:</span>
                <span id="signal-priority" class="status-value">medium</span>
            </div>
        </div>
    </div>

    <div class="manual-controls">
        <h4>🚶 手动控制</h4>
        <button class="btn" onclick="triggerPedestrianButton()">行人过街按钮</button>
        <button class="btn" onclick="resetView()">重置视角</button>
        <div id="debug-info" style="font-size: 12px; margin-top: 10px; opacity: 0.7;"></div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script type="module">
        import { OrbitControls } from 'https://cdn.skypack.dev/three@0.128.0/examples/jsm/controls/OrbitControls.js';

        // 全局变量
        let scene, camera, renderer, controls;
        let pedestrianObjs = {}, vehicleObjs = {}, lightObjs = {};
        let rsuSensors = [];
        let updateCount = 0;
        let currentData = null; // 存储当前仿真数据
        
        // 常量配置 - 完全匹配主仿真系统config.py
        const CONFIG = {
            SCREEN_WIDTH: 1200,
            SCREEN_HEIGHT: 800,
            INTERSECTION_CENTER_X: 600,  // SCREEN_WIDTH // 2
            INTERSECTION_CENTER_Y: 400,  // SCREEN_HEIGHT // 2
            ROAD_WIDTH: 100,
            CROSSWALK_WIDTH: 20,
            // 垂直主干道 - 匹配V_ROAD_RECT
            V_ROAD: {
                left: 550,    // INTERSECTION_CENTER_X - ROAD_WIDTH/2 = 600-50
                right: 650,   // INTERSECTION_CENTER_X + ROAD_WIDTH/2 = 600+50
                top: 0,
                bottom: 800,
                centerx: 600, // INTERSECTION_CENTER_X
                centery: 400  // INTERSECTION_CENTER_Y
            },
            // 水平人行横道（北）- 匹配H_CROSSWALK_RECT_NORTH
            H_CROSSWALK_NORTH: {
                left: 450,         // V_ROAD.left - ROAD_WIDTH = 550-100
                right: 750,        // V_ROAD.right + ROAD_WIDTH = 650+100
                top: 330,          // INTERSECTION_CENTER_Y - ROAD_WIDTH/2 - CROSSWALK_WIDTH = 400-50-20
                bottom: 350,       // top + CROSSWALK_WIDTH = 330+20
                centerx: 600,
                centery: 340
            },
            // 水平人行横道（南）- 匹配H_CROSSWALK_RECT_SOUTH
            H_CROSSWALK_SOUTH: {
                left: 450,
                right: 750,
                top: 450,          // INTERSECTION_CENTER_Y + ROAD_WIDTH/2 = 400+50
                bottom: 470,       // top + CROSSWALK_WIDTH = 450+20
                centerx: 600,
                centery: 460
            },
            // 西侧等待区 - 匹配WAIT_AREA_WEST
            WAIT_AREA_WEST: {
                left: 450,         // H_CROSSWALK_RECT_NORTH.left
                right: 550,        // left + ROAD_WIDTH = 450+100
                top: 330,          // H_CROSSWALK_RECT_NORTH.top
                bottom: 470,       // H_CROSSWALK_RECT_SOUTH.bottom
                centerx: 500,      // (450+550)/2
                centery: 400       // (330+470)/2
            },
            // 东侧等待区 - 匹配WAIT_AREA_EAST
            WAIT_AREA_EAST: {
                left: 650,         // V_ROAD.right
                right: 750,        // left + ROAD_WIDTH = 650+100
                top: 330,          // H_CROSSWALK_RECT_NORTH.top
                bottom: 470,       // H_CROSSWALK_RECT_SOUTH.bottom
                centerx: 700,      // (650+750)/2
                centery: 400       // (330+470)/2
            }
        };
        
        function init() {
            // Scene, camera, renderer setup
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x87CEEB); // Sky blue
            
            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 2000);
            camera.position.set(600, 300, -200);  // 相机位置对齐真实坐标系统
            camera.lookAt(600, 0, -400);  // 看向交集中心(600,0,-400)

            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;
            document.getElementById('container').appendChild(renderer.domElement);

            // Controls
            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.target.set(600, 0, -400);  // 控制中心对齐到交集中心(600,0,-400)
            controls.enableDamping = true;
            controls.dampingFactor = 0.1;

            // Lighting
            const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
            scene.add(ambientLight);

            const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
            directionalLight.position.set(200, 300, 200);
            directionalLight.castShadow = true;
            directionalLight.shadow.mapSize.width = 2048;
            directionalLight.shadow.mapSize.height = 2048;
            directionalLight.shadow.camera.near = 0.5;
            directionalLight.shadow.camera.far = 1000;
            directionalLight.shadow.camera.left = -500;
            directionalLight.shadow.camera.right = 500;
            directionalLight.shadow.camera.top = 500;
            directionalLight.shadow.camera.bottom = -500;
            scene.add(directionalLight);

            // 事件监听
            window.addEventListener('resize', onWindowResize, false);

            // 创建场景
            createIntersection();
            createTrafficLights();
            createRSUSensors();
            
            // 启动动画循环
            animate();
        }

        function createIntersection() {
            // === 关键修正：统一坐标系统 ===
            // 所有静态mesh必须使用与动态对象相同的坐标映射：
            // 2D坐标 (x,y) -> 3D坐标 (x, 0, -y)
            // 这样基础设施才能与车辆/行人在同一空间中对齐
            
            // 地面 - 扩大范围覆盖整个场景
            const groundGeometry = new THREE.PlaneGeometry(1200, 800);
            const groundMaterial = new THREE.MeshLambertMaterial({ 
                color: 0x90EE90,
                transparent: true,
                opacity: 0.8
            });
            const ground = new THREE.Mesh(groundGeometry, groundMaterial);
            ground.rotation.x = -Math.PI / 2;
            ground.position.set(600, -1, -400);  // 对应2D(600,400)中心
            ground.receiveShadow = true;
            scene.add(ground);

            // === 垂直道路（车辆行驶的主路）===
            // 2D坐标: x=550-650, y=0-800 (中心x=600)
            // 3D坐标: x=550-650, z=0到-800 (保持真实坐标)
            const verticalRoadGeometry = new THREE.PlaneGeometry(100, 800);
            const roadMaterial = new THREE.MeshLambertMaterial({ color: 0x404040 });
            const verticalRoad = new THREE.Mesh(verticalRoadGeometry, roadMaterial);
            verticalRoad.rotation.x = -Math.PI / 2;
            verticalRoad.position.set(600, 0, -400);  // 2D(600, 400) -> 3D(600, 0, -400)
            verticalRoad.receiveShadow = true;
            scene.add(verticalRoad);

            // 道路标线 - 中央分隔线
            const centerLineGeometry = new THREE.PlaneGeometry(4, 800);
            const centerLineMaterial = new THREE.MeshLambertMaterial({ 
                color: 0xFFFFFF,
                transparent: true,
                opacity: 0.9
            });
            const centerLine = new THREE.Mesh(centerLineGeometry, centerLineMaterial);
            centerLine.rotation.x = -Math.PI / 2;
            centerLine.position.set(600, 0.1, -400);  // 道路中央线
            scene.add(centerLine);

            // === 等待区域 ===
            // 西侧等待区: 2D=(450-550, 330-470, 中心500,400)
            // 3D坐标: 直接映射到(500, 0, -400)
            const waitAreaWestGeometry = new THREE.PlaneGeometry(100, 140);
            const waitAreaWestMaterial = new THREE.MeshLambertMaterial({ 
                color: 0xFFE4B5, 
                transparent: true, 
                opacity: 0.7 
            });
            const waitAreaWest = new THREE.Mesh(waitAreaWestGeometry, waitAreaWestMaterial);
            waitAreaWest.rotation.x = -Math.PI / 2;
            waitAreaWest.position.set(500, 0.2, -400);  // 2D(500,400) -> 3D(500,0,-400)
            scene.add(waitAreaWest);

            // 东侧等待区: 2D=(650-750, 330-470, 中心700,400)
            // 3D坐标: 直接映射到(700, 0, -400)
            const waitAreaEastGeometry = new THREE.PlaneGeometry(100, 140);
            const waitAreaEastMaterial = new THREE.MeshLambertMaterial({ 
                color: 0xFFE4B5, 
                transparent: true, 
                opacity: 0.7 
            });
            const waitAreaEast = new THREE.Mesh(waitAreaEastGeometry, waitAreaEastMaterial);
            waitAreaEast.rotation.x = -Math.PI / 2;
            waitAreaEast.position.set(700, 0.2, -400);  // 2D(700,400) -> 3D(700,0,-400)
            scene.add(waitAreaEast);

            // === 人行横道（斑马线）===
            // 2D坐标: x=450-750, y=380-420 (中心600,400)
            // 3D坐标: 直接映射到(600, 0, -400)
            const crosswalkWidth = 40;
            const crosswalkLength = 300;
            
            // 斑马线背景
            const crosswalkBgGeometry = new THREE.PlaneGeometry(crosswalkLength, crosswalkWidth);
            const crosswalkBgMaterial = new THREE.MeshLambertMaterial({ 
                color: 0x808080,
                transparent: true,
                opacity: 0.8
            });
            const crosswalkBg = new THREE.Mesh(crosswalkBgGeometry, crosswalkBgMaterial);
            crosswalkBg.rotation.x = -Math.PI / 2;
            crosswalkBg.position.set(600, 0.3, -400);  // 2D(600,400) -> 3D(600,0,-400)
            scene.add(crosswalkBg);

            // 斑马线条纹
            const stripeWidth = 14;
            const stripeSpacing = 14;
            const numStripes = Math.floor(crosswalkLength / (stripeWidth + stripeSpacing));
            
            for (let i = 0; i < numStripes; i++) {
                const stripeGeometry = new THREE.PlaneGeometry(stripeWidth, crosswalkWidth);
                const stripeMaterial = new THREE.MeshLambertMaterial({ 
                    color: 0xFFFFFF,
                    transparent: true,
                    opacity: 0.9
                });
                const stripe = new THREE.Mesh(stripeGeometry, stripeMaterial);
                stripe.rotation.x = -Math.PI / 2;
                // 条纹沿着人行横道分布 (x方向)
                const stripeX = 450 + i * (stripeWidth + stripeSpacing) + stripeWidth/2;
                stripe.position.set(stripeX, 0.4, -400);
                scene.add(stripe);
            }

            // === 道路边界线 ===
            // 道路左边界 (x=550)
            const leftBoundaryGeometry = new THREE.PlaneGeometry(2, 800);
            const boundaryMaterial = new THREE.MeshLambertMaterial({ color: 0xFFFFFF });
            const leftBoundary = new THREE.Mesh(leftBoundaryGeometry, boundaryMaterial);
            leftBoundary.rotation.x = -Math.PI / 2;
            leftBoundary.position.set(550, 0.1, -400);  // 2D(550,400) -> 3D(550,0,-400)
            scene.add(leftBoundary);

            // 道路右边界 (x=650)
            const rightBoundary = new THREE.Mesh(leftBoundaryGeometry, boundaryMaterial);
            rightBoundary.rotation.x = -Math.PI / 2;
            rightBoundary.position.set(650, 0.1, -400);  // 2D(650,400) -> 3D(650,0,-400)
            scene.add(rightBoundary);
        }

        function createTrafficLights() {
            // 初始化信号灯对象
            lightObjs = {
                vehicleLights: [],
                pedestrianLights: []
            };

            // === 车辆信号灯 ===
            // 位置：在人行横道北侧，道路右侧
            // 2D坐标: x=670, y=320 -> 3D坐标: (670, 5, -320)
            
            // 信号灯杆
            const poleGeometry = new THREE.CylinderGeometry(1, 1, 30);
            const poleMaterial = new THREE.MeshLambertMaterial({ color: 0x444444 });
            const pole = new THREE.Mesh(poleGeometry, poleMaterial);
            pole.position.set(670, 15, -320);  // 2D(670,320) -> 3D(670,15,-320)
            scene.add(pole);

            // 信号灯箱体
            const lightBoxGeometry = new THREE.BoxGeometry(15, 40, 8);
            const lightBoxMaterial = new THREE.MeshLambertMaterial({ color: 0x222222 });
            const lightBox = new THREE.Mesh(lightBoxGeometry, lightBoxMaterial);
            lightBox.position.set(670, 30, -320);
            scene.add(lightBox);

            // 红黄绿三色灯
            const lightColors = [0xFF0000, 0xFFFF00, 0x00FF00]; // 红、黄、绿
            for (let i = 0; i < 3; i++) {
                const lightGeometry = new THREE.CircleGeometry(4);
                const lightMaterial = new THREE.MeshLambertMaterial({
                    color: lightColors[i],
                    transparent: true,
                    opacity: 0.3
                });
                const light = new THREE.Mesh(lightGeometry, lightMaterial);
                light.position.set(665, 38 - i * 12, -320);  // 垂直排列
                light.rotation.y = -Math.PI / 2;  // 面向道路
                scene.add(light);
                lightObjs.vehicleLights.push(light);
            }

            // === 行人信号灯 ===
            lightObjs.pedestrianLights = [];
            
            // 西侧等待区行人信号灯
            // 2D坐标: x=460, y=400 -> 3D坐标: (460, 12.5, -400)
            const pedPoleGeometry = new THREE.CylinderGeometry(0.8, 0.8, 25);
            const pedPole1 = new THREE.Mesh(pedPoleGeometry, poleMaterial);
            pedPole1.position.set(460, 12.5, -400);  // 2D(460,400) -> 3D(460,12.5,-400)
            scene.add(pedPole1);

            const pedLightBox1Geometry = new THREE.BoxGeometry(8, 15, 4);
            const pedLightBox1 = new THREE.Mesh(pedLightBox1Geometry, lightBoxMaterial);
            pedLightBox1.position.set(460, 25, -400);
            scene.add(pedLightBox1);

            // WALK灯
            const walkLightGeometry = new THREE.CircleGeometry(3);
            const walkLightMaterial = new THREE.MeshLambertMaterial({ 
                color: 0x00FF00, 
                transparent: true, 
                opacity: 0.3 
            });
            const walkLight1 = new THREE.Mesh(walkLightGeometry, walkLightMaterial);
            walkLight1.position.set(465, 28, -400);
            walkLight1.rotation.y = Math.PI / 2;
            scene.add(walkLight1);

            // DON'T WALK灯
            const dontWalkLightGeometry = new THREE.CircleGeometry(3);
            const dontWalkLightMaterial = new THREE.MeshLambertMaterial({ 
                color: 0xFF0000, 
                transparent: true, 
                opacity: 1.0 
            });
            const dontWalkLight1 = new THREE.Mesh(dontWalkLightGeometry, dontWalkLightMaterial);
            dontWalkLight1.position.set(465, 22, -400);
            dontWalkLight1.rotation.y = Math.PI / 2;
            scene.add(dontWalkLight1);

            lightObjs.pedestrianLights.push({
                walk: walkLight1,
                dontWalk: dontWalkLight1
            });

            // 东侧等待区行人信号灯
            // 2D坐标: x=740, y=400 -> 3D坐标: (740, 12.5, -400)
            const pedPole2 = new THREE.Mesh(pedPoleGeometry, poleMaterial);
            pedPole2.position.set(740, 12.5, -400);  // 2D(740,400) -> 3D(740,12.5,-400)
            scene.add(pedPole2);

            const pedLightBox2 = new THREE.Mesh(pedLightBox1Geometry, lightBoxMaterial);
            pedLightBox2.position.set(740, 25, -400);
            scene.add(pedLightBox2);

            const walkLight2 = new THREE.Mesh(walkLightGeometry, walkLightMaterial);
            walkLight2.position.set(735, 28, -400);
            walkLight2.rotation.y = -Math.PI / 2;
            scene.add(walkLight2);

            const dontWalkLight2 = new THREE.Mesh(dontWalkLightGeometry, dontWalkLightMaterial);
            dontWalkLight2.position.set(735, 22, -400);
            dontWalkLight2.rotation.y = -Math.PI / 2;
            scene.add(dontWalkLight2);

            lightObjs.pedestrianLights.push({
                walk: walkLight2,
                dontWalk: dontWalkLight2
            });
        }

        function createRSUSensors() {
            // RSU传感器位置 - 统一坐标映射
            // 使用与动态对象相同的坐标转换: 2D(x,y) -> 3D(x,y,-y)
            const sensorPositions = [
                { name: 'N', x: 600, z: -300 },    // 北: 2D(600,300) -> 3D(600,8,-300)
                { name: 'S', x: 600, z: -500 },    // 南: 2D(600,500) -> 3D(600,8,-500)
                { name: 'W', x: 500, z: -400 },    // 西: 2D(500,400) -> 3D(500,8,-400)
                { name: 'E', x: 700, z: -400 }     // 东: 2D(700,400) -> 3D(700,8,-400)
            ];

            sensorPositions.forEach(pos => {
                // RSU地面标记（圆形地标）
                const sensorGeometry = new THREE.CylinderGeometry(8, 8, 1);
                const sensorMaterial = new THREE.MeshLambertMaterial({ 
                    color: 0x323296,
                    transparent: true,
                    opacity: 0.9
                });
                const sensor = new THREE.Mesh(sensorGeometry, sensorMaterial);
                sensor.position.set(pos.x, 0.5, pos.z);
                scene.add(sensor);

                // RSU标签
                const textGeometry = new THREE.RingGeometry(2, 4);
                const textMaterial = new THREE.MeshLambertMaterial({ 
                    color: 0xFFFFFF,
                    transparent: true,
                    opacity: 0.8
                });
                const textMesh = new THREE.Mesh(textGeometry, textMaterial);
                textMesh.position.set(pos.x, 1, pos.z);
                textMesh.rotation.x = -Math.PI / 2;
                scene.add(textMesh);

                rsuSensors.push(sensor);
            });
        }

        function updateTrafficLights(data) {
            if (!lightObjs.vehicleLights || !lightObjs.pedestrianLights) return;

            // 更新车辆信号灯
            const vehiclePhase = data.traffic_light.vehicle_phase;
            lightObjs.vehicleLights.forEach((light, index) => {
                const isActive = (vehiclePhase === 'red' && index === 0) ||
                                (vehiclePhase === 'yellow' && index === 1) ||
                                (vehiclePhase === 'green' && index === 2);
                light.material.opacity = isActive ? 1.0 : 0.3;
            });

            // 更新行人信号灯
            const pedPhase = data.traffic_light.pedestrian_phase;
            lightObjs.pedestrianLights.forEach(pedLight => {
                if (pedLight.walk && pedLight.dontWalk) {
                    if (pedPhase === 'walk') {
                        pedLight.walk.material.opacity = 1.0;
                        pedLight.dontWalk.material.opacity = 0.3;
                    } else {
                        pedLight.walk.material.opacity = 0.3;
                        pedLight.dontWalk.material.opacity = 1.0;
                    }
                }
            });

            // 更新UI显示
            const vehicleSignalEl = document.getElementById('vehicle-signal');
            if (vehicleSignalEl) {
                vehicleSignalEl.textContent = vehiclePhase.toUpperCase();
                vehicleSignalEl.className = `status-value light-status light-${vehiclePhase}`;
            }

            const pedSignalEl = document.getElementById('pedestrian-signal');
            if (pedSignalEl) {
                pedSignalEl.textContent = pedPhase.toUpperCase();
                pedSignalEl.className = `status-value light-status light-${pedPhase.replace('_', '-')}`;
            }
        }

        function updatePedestrians(pedestrians) {
            // 清理旧的行人对象
            Object.keys(pedestrianObjs).forEach(id => {
                if (!pedestrians.find(p => p.id === id)) {
                    scene.remove(pedestrianObjs[id]);
                    delete pedestrianObjs[id];
                }
            });

            // 更新行人位置
            pedestrians.forEach(ped => {
                if (!pedestrianObjs[ped.id]) {
                    // 创建新行人 - 更人性化的外观
                    const pedGroup = new THREE.Group();
                    
                    // 身体 - 根据等待区域设置不同颜色
                    const bodyGeometry = new THREE.CylinderGeometry(4, 4, 15, 8);
                    // 判断行人所在等待区：x < 600在西侧，x >= 600在东侧
                    const bodyColor = ped.x < 600 ? 0x0066ff : 0x006600;
                    const bodyMaterial = new THREE.MeshLambertMaterial({ color: bodyColor });
                    const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
                    body.position.y = 7.5;
                    pedGroup.add(body);
                    
                    // 头部
                    const headGeometry = new THREE.SphereGeometry(3, 8, 6);
                    const headMaterial = new THREE.MeshLambertMaterial({ color: 0xFFDBB3 });
                    const head = new THREE.Mesh(headGeometry, headMaterial);
                    head.position.y = 18;
                    pedGroup.add(head);
                    
                    // 帽子或头发
                    const hatGeometry = new THREE.SphereGeometry(3.2, 8, 6);
                    const hatMaterial = new THREE.MeshLambertMaterial({ color: 0x8B4513 });
                    const hat = new THREE.Mesh(hatGeometry, hatMaterial);
                    hat.position.y = 19;
                    hat.scale.y = 0.6;
                    pedGroup.add(hat);
                    
                    // 腿部（两条腿）
                    const legGeometry = new THREE.CylinderGeometry(1.5, 1.5, 8, 6);
                    const legMaterial = new THREE.MeshLambertMaterial({ color: 0x000080 });
                    
                    const leg1 = new THREE.Mesh(legGeometry, legMaterial);
                    leg1.position.set(-2, -4, 0);
                    pedGroup.add(leg1);
                    
                    const leg2 = new THREE.Mesh(legGeometry, legMaterial);
                    leg2.position.set(2, -4, 0);
                    pedGroup.add(leg2);
                    
                    // 手臂
                    const armGeometry = new THREE.CylinderGeometry(1, 1, 10, 6);
                    const armMaterial = new THREE.MeshLambertMaterial({ color: bodyColor });
                    
                    const arm1 = new THREE.Mesh(armGeometry, armMaterial);
                    arm1.position.set(-6, 10, 0);
                    arm1.rotation.z = Math.PI / 6;
                    pedGroup.add(arm1);
                    
                    const arm2 = new THREE.Mesh(armGeometry, armMaterial);
                    arm2.position.set(6, 10, 0);
                    arm2.rotation.z = -Math.PI / 6;
                    pedGroup.add(arm2);
                    
                    // 可穿戴设备指示器（如果有的话）
                    if (ped.intent_prob > 0.6) {
                        const deviceGeometry = new THREE.BoxGeometry(1, 1, 1);
                        const deviceMaterial = new THREE.MeshLambertMaterial({ 
                            color: 0x00FF00, 
                            emissive: 0x003300 
                        });
                        const device = new THREE.Mesh(deviceGeometry, deviceMaterial);
                        device.position.set(-6, 12, 0);
                        pedGroup.add(device);
                    }
                    
                    // 初始位置 - 统一坐标转换：2D(x,y) -> 3D(x-600, 0, -(y-400))
                    pedGroup.position.set(ped.x - 600, 0.5, -(ped.y - 400));
                    pedGroup.castShadow = true;
                    scene.add(pedGroup);
                    pedestrianObjs[ped.id] = pedGroup;
                    
                    // 初始化运动属性
                    pedGroup.realX = ped.x;
                    pedGroup.realY = ped.y;
                    pedGroup.targetX = ped.x;
                    pedGroup.targetY = ped.y;
                    pedGroup.state = ped.state || 'waiting';
                    pedGroup.crossingProgress = 0;
                } else {
                    // 更新现有行人 - 实现真正的行人运动
                    const pedGroup = pedestrianObjs[ped.id];
                    
                    // 更新行人状态
                    pedGroup.state = ped.state || 'waiting';
                    
                    // 根据状态和交通信号控制行人运动
                    if (currentData && currentData.traffic_light) {
                        if (currentData.traffic_light.pedestrian_phase === 'walk' || 
                            ped.state === 'crossing') {
                            // 行人绿灯或正在过马路
                            if (ped.is_crossing || ped.state === 'crossing') {
                                                            // 计算过马路的目标位置 - 基于真实2D坐标系统
                            if (ped.target_area === 'WAIT_AREA_WEST' || ped.x < 600) {
                                // 从西向东过马路 - 到东侧等待区中心
                                pedGroup.targetX = 700; // 东侧等待区中心X坐标
                            } else {
                                // 从东向西过马路 - 到西侧等待区中心
                                pedGroup.targetX = 500; // 西侧等待区中心X坐标
                            }
                                
                                // 平滑移动到目标位置
                                const moveSpeed = 1.5;
                                const deltaX = (pedGroup.targetX - pedGroup.realX) * 0.05;
                                if (Math.abs(deltaX) > 0.5) {
                                    pedGroup.realX += deltaX * moveSpeed;
                                }
                                
                                // 添加轻微的Y轴摆动（模拟走路）
                                const walkOscillation = Math.sin(Date.now() * 0.01) * 2;
                                pedGroup.realY = ped.y + walkOscillation;
                            }
                        } else {
                            // 行人红灯，在等待区等待
                            pedGroup.realX = ped.x;
                            pedGroup.realY = ped.y;
                            
                            // 添加轻微的等待动画（小幅度摆动）
                            const waitOscillation = Math.sin(Date.now() * 0.005) * 1;
                            pedGroup.realX = ped.x + waitOscillation;
                        }
                    }
                    
                    // 更新3D位置 - 统一坐标转换：2D(x,y) -> 3D(x-600, 0, -(y-400))
                    pedGroup.position.set(
                        pedGroup.realX - 600, 
                        0.5, 
                        -(pedGroup.realY - 400)
                    );
                    
                    // 根据意图概率更新可穿戴设备指示器
                    const deviceIndicator = pedGroup.children.find(child => 
                        child.material && child.material.color.getHex() === 0x00FF00
                    );
                    if (deviceIndicator) {
                        const intensity = ped.intent_prob || 0;
                        deviceIndicator.material.emissive.setHex(
                            intensity > 0.7 ? 0x006600 : 
                            intensity > 0.4 ? 0x003300 : 0x001100
                        );
                    }
                }
            });

            // 更新UI
            const pedCountEl = document.getElementById('pedestrian-count');
            if (pedCountEl) {
                pedCountEl.textContent = `${pedestrians.length} 名行人`;
            }

            const pedListEl = document.getElementById('pedestrian-list');
            if (pedListEl) {
                pedListEl.innerHTML = pedestrians.map(p => 
                    `<div class="ped-item">🚶 ${p.id}: (${Math.round(p.x)}, ${Math.round(p.y)}) 意图${Math.round((p.intent_prob||0)*100)}%, 状态: ${p.state}</div>`
                ).join('');
            }
        }

        function updateVehicles(vehicles) {
            // 清理旧的车辆对象
            Object.keys(vehicleObjs).forEach(id => {
                if (!vehicles.find(v => v.id === id)) {
                    scene.remove(vehicleObjs[id]);
                    delete vehicleObjs[id];
                }
            });

            // 更新车辆位置
            vehicles.forEach(vehicle => {
                if (!vehicleObjs[vehicle.id]) {
                    // 创建新车辆 - 完全重新设计，更逼真的外观
                    const carGroup = new THREE.Group();
                    
                    // 车身 - 更大更逼真
                    const bodyGeometry = new THREE.BoxGeometry(30, 12, 60);
                    const colors = [0x003366, 0x660033, 0x336600, 0x663300, 0x333366];
                    const bodyColor = colors[parseInt(vehicle.id.slice(1)) % colors.length];
                    const bodyMaterial = new THREE.MeshLambertMaterial({ color: bodyColor });
                    const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
                    body.position.y = 6;
                    carGroup.add(body);
                    
                    // 车顶
                    const roofGeometry = new THREE.BoxGeometry(25, 8, 35);
                    const roofMaterial = new THREE.MeshLambertMaterial({ color: bodyColor + 0x222222 });
                    const roof = new THREE.Mesh(roofGeometry, roofMaterial);
                    roof.position.y = 16;
                    carGroup.add(roof);
                    
                    // 前挡风玻璃
                    const windshieldGeometry = new THREE.BoxGeometry(22, 6, 2);
                    const windshieldMaterial = new THREE.MeshLambertMaterial({ 
                        color: 0x87CEEB, 
                        transparent: true, 
                        opacity: 0.7 
                    });
                    const windshield = new THREE.Mesh(windshieldGeometry, windshieldMaterial);
                    windshield.position.set(0, 14, 29);
                    carGroup.add(windshield);
                    
                    // 车轮 - 更大更逼真
                    const wheelGeometry = new THREE.CylinderGeometry(5, 5, 4);
                    const wheelMaterial = new THREE.MeshLambertMaterial({ color: 0x222222 });
                    
                    const wheelPositions = [
                        [-12, 2, 20],   // 前左
                        [12, 2, 20],    // 前右
                        [-12, 2, -20],  // 后左
                        [12, 2, -20]    // 后右
                    ];
                    
                    wheelPositions.forEach(pos => {
                        const wheel = new THREE.Mesh(wheelGeometry, wheelMaterial);
                        wheel.position.set(pos[0], pos[1], pos[2]);
                        wheel.rotation.z = Math.PI / 2;
                        carGroup.add(wheel);
                    });
                    
                    // 车灯
                    const headlightGeometry = new THREE.SphereGeometry(2, 8, 6);
                    const headlightMaterial = new THREE.MeshLambertMaterial({ 
                        color: 0xFFFFFF, 
                        emissive: 0x333333 
                    });
                    
                    const headlight1 = new THREE.Mesh(headlightGeometry, headlightMaterial);
                    headlight1.position.set(-8, 8, 30);
                    carGroup.add(headlight1);
                    
                    const headlight2 = new THREE.Mesh(headlightGeometry, headlightMaterial);
                    headlight2.position.set(8, 8, 30);
                    carGroup.add(headlight2);
                    
                    // 初始位置 - 统一坐标转换：2D(x,y) -> 3D(x-600, 0, -(y-400))
                    carGroup.position.set(vehicle.x - 600, 0.5, -(vehicle.y - 400));
                    carGroup.castShadow = true;
                    scene.add(carGroup);
                    vehicleObjs[vehicle.id] = carGroup;
                    
                    // 初始化运动属性
                    carGroup.realX = vehicle.x;
                    carGroup.realY = vehicle.y;
                    carGroup.speed = vehicle.speed || 2;
                    carGroup.dx = vehicle.dx || 0;
                    carGroup.dy = vehicle.dy || 1;
                    carGroup.isMoving = true;
                    carGroup.canMove = true;
                } else {
                    // 更新现有车辆 - 实现真正的动态运动
                    const carGroup = vehicleObjs[vehicle.id];
                    
                    // 更新车辆数据
                    carGroup.speed = vehicle.speed || 2;
                    carGroup.dx = vehicle.dx || 0;
                    carGroup.dy = vehicle.dy || 1;
                    
                    // 根据交通信号控制车辆运动
                    let shouldMove = true;
                    if (currentData && currentData.traffic_light) {
                        if (currentData.traffic_light.vehicle_phase === 'red') {
                            // 红灯：在人行横道前停车
                            const crosswalkStartY = 380; // 人行横道北边界 (2D坐标系统)
                            const stopLineY = crosswalkStartY - 20; // 停车线
                            if (carGroup.realY > stopLineY - 10 && carGroup.realY < crosswalkStartY + 40) {
                                shouldMove = false;
                            }
                        } else if (currentData.traffic_light.vehicle_phase === 'yellow') {
                            // 黄灯：如果接近人行横道则减速，否则继续
                            const crosswalkStartY = 380;
                            const slowDownZone = 80;
                            if (carGroup.realY > crosswalkStartY - slowDownZone && carGroup.realY < crosswalkStartY + 40) {
                                carGroup.speed = Math.max(0.5, carGroup.speed * 0.7);
                            }
                        }
                        // 绿灯：正常行驶
                    }
                    
                    // 执行运动 - 垂直道路从北向南移动
                    if (shouldMove) {
                        carGroup.realX += carGroup.dx * carGroup.speed * 0.8;
                        carGroup.realY += carGroup.dy * carGroup.speed * 0.8;
                        
                        // 边界检查和循环 - 基于真实道路范围
                        if (carGroup.realY > 700) {
                            // 车辆驶出南边界，重新从北边进入
                            carGroup.realY = 50;
                        } else if (carGroup.realY < 30) {
                            carGroup.realY = 50;
                        }
                        
                        // 保持车辆在道路中心线附近 (x=600)
                        if (carGroup.realX > 650) {
                            carGroup.realX = 600;
                        } else if (carGroup.realX < 550) {
                            carGroup.realX = 600;
                        }
                    }
                    
                    // 更新3D位置 - 统一坐标转换：2D(x,y) -> 3D(x-600, 0, -(y-400))
                    carGroup.position.set(
                        carGroup.realX - 600, 
                        0.5, 
                        -(carGroup.realY - 400)
                    );
                }
            });

            // 更新UI
            const vehicleCountEl = document.getElementById('vehicle-count');
            if (vehicleCountEl) {
                vehicleCountEl.textContent = `${vehicles.length} 辆`;
            }

            const vehicleListEl = document.getElementById('vehicle-list');
            if (vehicleListEl) {
                vehicleListEl.innerHTML = vehicles.map(v => 
                    `<div class="vehicle-item">🚗 ${v.id}: (${Math.round(v.x)}, ${Math.round(v.y)}) 速度${v.speed}m/s</div>`
                ).join('');
            }
        }

        function updateRSUStatus(rsuStatus) {
            const rsuScansEl = document.getElementById('rsu-scans');
            if (rsuScansEl) {
                rsuScansEl.textContent = `${rsuStatus.active_scans} 个传感器`;
            }

            const signalPriorityEl = document.getElementById('signal-priority');
            if (signalPriorityEl) {
                signalPriorityEl.textContent = rsuStatus.signal_request_priority;
            }
        }

        function updateSceneFromData(data) {
            // 存储当前数据供其他函数使用
            currentData = data;
            
            updateTrafficLights(data);
            updateVehicles(data.vehicles);
            updatePedestrians(data.pedestrians);
            updateRSUStatus(data.rsu_status);
            
            updateCount++;
            const debugInfo = document.getElementById('debug-info');
            if (debugInfo) {
                debugInfo.textContent = `更新#${updateCount}`;
            }
        }

        function animate() {
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        }

        function onWindowResize() {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
            controls.update();
        }

        // 手动控制函数
        window.triggerPedestrianButton = function() {
            console.log('🚶 触发行人过街按钮');
            // 这里可以发送请求到后端触发按钮事件
        };

        window.resetView = function() {
            camera.position.set(0, 300, 200);
            camera.lookAt(0, 0, 0);
            controls.target.set(0, 0, 0);
        };

        // 数据更新循环
        function fetchTrafficData() {
            fetch('/api/traffic_data')
                .then(response => response.json())
                .then(data => {
                    updateSceneFromData(data);
                })
                .catch(error => {
                    console.error('数据获取失败:', error);
                });
        }

        // 初始化
        init();
        
        // 开始数据更新循环
        setInterval(fetchTrafficData, 500); // 每0.5秒更新一次
        
    </script>
</body>
</html>'''

def start_web_server():
    """启动web服务器"""
    # 尝试多个端口
    PORTS = [8000, 8001, 8002, 8003, 8080, 8888, 9000]
    Handler = TrafficSimulationHandler
    
    for PORT in PORTS:
        try:
            print(f"🌐 启动3D仿真Web服务器: http://localhost:{PORT}")
            
            with socketserver.TCPServer(("", PORT), Handler) as httpd:
                print(f"✅ 服务器启动成功!")
                print("📊 实时数据同步中...")
                print("🔄 按 Ctrl+C 停止服务器")
                
                # 打开浏览器
                webbrowser.open(f'http://localhost:{PORT}')
                
                httpd.serve_forever()
                
        except OSError as e:
            if e.errno == 48:  # Address already in use
                print(f"⚠️ 端口 {PORT} 被占用，尝试下一个端口...")
                continue
            else:
                print(f"❌ 服务器启动失败: {e}")
                break
    else:
        print("❌ 所有端口都被占用，无法启动服务器")

if __name__ == "__main__":
    start_web_server()