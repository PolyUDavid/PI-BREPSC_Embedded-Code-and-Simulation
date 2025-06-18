# main_simulation.py
import pygame
import sys
import random
from config import *
from pedestrian_simulator import Pedestrian
from rsu_simulator import RSU
from traffic_light_controller import TrafficLightController
from edge_ai_module import EdgeAIModule
from vehicle_simulator import Vehicle
from sync_3d_data import update_3d_sync

# --- Pygame 初始化 ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("PI-BREPSC - Pedestrian Signal Simulation with Physical Information Fusion")
clock = pygame.time.Clock()
font_s = pygame.font.Font(DEFAULT_FONT_NAME, FONT_SIZE_SMALL)
font_m = pygame.font.Font(DEFAULT_FONT_NAME, FONT_SIZE_MEDIUM)
font_l = pygame.font.Font(DEFAULT_FONT_NAME, FONT_SIZE_LARGE)

# --- 仿真对象实例化 ---
rsu_unit = RSU(rsu_id="Intersection_RSU1", scanner_configs_dict=RSU_SCANNER_POSITIONS)
tlc_unit = TrafficLightController()
pedestrians_list = []
selected_pedestrian_id = None # 用于显示详细信息

# --- Edge AI 模块实例化 ---
ai_module = EdgeAIModule()

# --- 车辆对象初始化 ---
vehicles_list = []
vehicle_spawn_y = [V_ROAD_RECT.top + 50, V_ROAD_RECT.top + 150, V_ROAD_RECT.top + 250]
for i, y in enumerate(vehicle_spawn_y):
    v = Vehicle(id=f"V{i+1}", start_pos=(V_ROAD_RECT.centerx, y), speed=2, direction="vertical")
    v.allow_cross_on_yellow = False
    vehicles_list.append(v)
    print(f"🚗 车辆 {v.id} 初始化: 位置({V_ROAD_RECT.centerx}, {y}), 道路中央行驶")

yellow_flag = False  # <--- 全局变量定义，修复NameError

# --- 辅助函数 ---
def draw_text(surface, text, pos, font, color=DARK_GREY, center_aligned=False):
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect()
    if center_aligned:
        text_rect.center = pos
    else:
        text_rect.topleft = pos
    surface.blit(text_surf, text_rect)

def spawn_pedestrian(ped_id_counter, side="west", y_offset=0):
    """Spawns a pedestrian in the sidewalk area on the specified side and plans a path."""
    start_y = random.randint(int(H_CROSSWALK_RECT_NORTH.centery - ROAD_WIDTH*0.8), 
                             int(H_CROSSWALK_RECT_SOUTH.centery + ROAD_WIDTH*0.8)) + y_offset
    
    if side == "west":
        start_x = WAIT_AREA_WEST.left + PEDESTRIAN_RADIUS + 5
        target_wait_x = WAIT_AREA_WEST.right - PEDESTRIAN_RADIUS - 10
        target_wait_area_key = "WAIT_AREA_WEST"
        color = BLUE
    else: # east
        start_x = WAIT_AREA_EAST.right - PEDESTRIAN_RADIUS - 5
        target_wait_x = WAIT_AREA_EAST.left + PEDESTRIAN_RADIUS + 10
        target_wait_area_key = "WAIT_AREA_EAST"
        color = (0,100,200) # 深蓝

    ped = Pedestrian(id_num=ped_id_counter, start_pos=(start_x, start_y), color=color, target_wait_area_key=target_wait_area_key)
    # 确保每个行人都有可穿戴蓝牙设备
    ped.has_wearable_device = True
    ped.device_battery_level = random.uniform(0.3, 1.0)  # 30%-100%电量
    ped.device_signal_strength = random.uniform(0.7, 1.0)  # 70%-100%信号强度
    ped.ble_enabled = True
    print(f"✅ {ped.id} 配备可穿戴蓝牙设备 (电量: {ped.device_battery_level:.1%}, 信号: {ped.device_signal_strength:.1%})")
    
    ped.set_path_to_point((target_wait_x, start_y)) # 移动到等待区边缘
    pedestrians_list.append(ped)
    return ped_id_counter + 1

# --- 初始化一些行人 ---
ped_id_counter = 1
# West waiting area, top and bottom
ped_id_counter = spawn_pedestrian(ped_id_counter, "west", y_offset=-40)
ped_id_counter = spawn_pedestrian(ped_id_counter, "west", y_offset=40)
# East waiting area, top and bottom
ped_id_counter = spawn_pedestrian(ped_id_counter, "east", y_offset=-40)
ped_id_counter = spawn_pedestrian(ped_id_counter, "east", y_offset=40)

# 为所有行人确保蓝牙设备状态
for ped in pedestrians_list:
    if not hasattr(ped, 'has_wearable_device'):
        ped.has_wearable_device = True
        ped.device_battery_level = random.uniform(0.3, 1.0)
        ped.device_signal_strength = random.uniform(0.7, 1.0)
        ped.ble_enabled = True
        print(f"🔧 为现有行人 {ped.id} 补充可穿戴蓝牙设备")

if pedestrians_list:
    selected_pedestrian_id = pedestrians_list[0].id


# --- 主循环 ---
running = True
while running:
    # --- 事件处理 ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_s: # Spawn new pedestrian from West
                ped_id_counter = spawn_pedestrian(ped_id_counter, "west", y_offset=random.randint(-20, 20))
                if not selected_pedestrian_id and pedestrians_list: selected_pedestrian_id = pedestrians_list[-1].id
            if event.key == pygame.K_d: # Spawn new pedestrian from East
                ped_id_counter = spawn_pedestrian(ped_id_counter, "east", y_offset=random.randint(-20, 20))
                if not selected_pedestrian_id and pedestrians_list: selected_pedestrian_id = pedestrians_list[-1].id
            if event.key == pygame.K_b: # Selected pedestrian presses button
                if selected_pedestrian_id:
                    for p in pedestrians_list:
                        if p.id == selected_pedestrian_id:
                            p.is_requesting_button_press = not p.is_requesting_button_press
                            print(f"{p.id} button press: {p.is_requesting_button_press}")
                            break
            if event.key == pygame.K_m: # Toggle malicious for selected
                if selected_pedestrian_id:
                    for p in pedestrians_list:
                        if p.id == selected_pedestrian_id:
                            p.is_malicious = not p.is_malicious
                            print(f"{p.id} malicious: {p.is_malicious}")
                            break
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left click to select pedestrian
                mouse_pos = event.pos
                for p in pedestrians_list:
                    dist_sq = (mouse_pos[0] - p.pos[0])**2 + (mouse_pos[1] - p.pos[1])**2
                    if dist_sq < (p.radius * 2)**2 : # Click near pedestrian
                        selected_pedestrian_id = p.id
                        break

    # --- 更新逻辑 ---
    for ped in pedestrians_list[:]:  # 使用列表副本进行迭代
        ped.update()
        # 如果行人没进入等待区，继续向等待区移动
        if not ped.is_at_wait_area:
            if ped.target_wait_area_key == "WAIT_AREA_WEST":
                ped.set_path_to_point((WAIT_AREA_WEST.right - PEDESTRIAN_RADIUS - 10, ped.pos[1]))
            else:
                ped.set_path_to_point((WAIT_AREA_EAST.left + PEDESTRIAN_RADIUS + 10, ped.pos[1]))
        # 自动请求过马路
        if ped.is_at_wait_area and not ped.is_requesting_button_press:
            ped.is_requesting_button_press = True
            print(f"{ped.id} 按钮按下")
        
        # --- Edge AI 数据收集 ---
        # 这里motion_state转为数值: moving=1, stationary_short=0.5, stationary_long=0
        motion_val = 1 if ped.motion_state=="moving" else (0.5 if ped.motion_state=="stationary_short" else 0)
        ai_module.update_pedestrian(ped.id, rsu_unit.pedestrian_tracking_data.get(ped.id, {}).get('avg_rssi_stable', -90), motion_val, int(ped.is_requesting_button_press), int(ped.is_malicious))

    rsu_unit.scan_and_process_pedestrians(pedestrians_list)
    rsu_request_priority = rsu_unit.determine_signal_request_priority()
    tlc_unit.update(rsu_request_priority)

    # Pedestrian crossing logic (only the front pedestrian fully inside waiting area and at edge can cross)
    if tlc_unit.pedestrian_phase == "walk":
        # 找到每侧在等待区矩形范围内、且到达边缘的最前面行人
        front_west = None
        front_east = None
        min_dist_west = float('inf')
        min_dist_east = float('inf')
        for ped in pedestrians_list:
            # 只考虑x和y都在等待区范围内的行人
            if (
                ped.target_wait_area_key == "WAIT_AREA_WEST" and
                WAIT_AREA_WEST.left <= ped.pos[0] <= WAIT_AREA_WEST.right and
                WAIT_AREA_WEST.top <= ped.pos[1] <= WAIT_AREA_WEST.bottom
            ):
                dist = abs(ped.pos[0] - (WAIT_AREA_WEST.right - PEDESTRIAN_RADIUS - 10))
                if dist < min_dist_west:
                    min_dist_west = dist
                    front_west = ped
            elif (
                ped.target_wait_area_key == "WAIT_AREA_EAST" and
                WAIT_AREA_EAST.left <= ped.pos[0] <= WAIT_AREA_EAST.right and
                WAIT_AREA_EAST.top <= ped.pos[1] <= WAIT_AREA_EAST.bottom
            ):
                dist = abs(ped.pos[0] - (WAIT_AREA_EAST.left + PEDESTRIAN_RADIUS + 10))
                if dist < min_dist_east:
                    min_dist_east = dist
                    front_east = ped
        # 只允许在等待区边缘的最前面行人过马路
        if front_west and front_west.pos[0] >= WAIT_AREA_WEST.right - PEDESTRIAN_RADIUS - 10:
            target_y = H_CROSSWALK_RECT_NORTH.centery
            front_west.set_path_to_point((WAIT_AREA_EAST.left + PEDESTRIAN_RADIUS + 5, target_y))
            front_west.target_wait_area_key = "WAIT_AREA_EAST"
            front_west.is_requesting_button_press = False
        if front_east and front_east.pos[0] <= WAIT_AREA_EAST.left + PEDESTRIAN_RADIUS + 10:
            target_y = H_CROSSWALK_RECT_NORTH.centery
            front_east.set_path_to_point((WAIT_AREA_WEST.right - PEDESTRIAN_RADIUS - 5, target_y))
            front_east.target_wait_area_key = "WAIT_AREA_WEST"
            front_east.is_requesting_button_press = False

    # --- Edge AI 推理与优先级融合 ---
    ai_results = {}
    for ped in pedestrians_list:
        ai_results[ped.id] = ai_module.predict(ped.id)
    # 选出最高优先级建议
    ai_priority = 'low'
    for res in ai_results.values():
        if res['priority'] == 'high':
            ai_priority = 'high'
            break
    # 写入文件供C模块读取
    with open('ai_priority.txt', 'w') as f:
        f.write(ai_priority + '\n')

    # --- 车辆动态更新（黄灯只放行最前车，且可完全通过斑马线） ---
    v_colors, _, _ = tlc_unit.get_signal_display_info()
    stop_line_y = H_CROSSWALK_RECT_NORTH.top - 12  # 停车线在斑马线前
    crosswalk_end_y = H_CROSSWALK_RECT_SOUTH.bottom
    # 记录压着斑马线的车辆
    if not hasattr(globals(), 'crosswalk_blocking_vehicles'):
        crosswalk_blocking_vehicles = set()
    # 红灯/行人walk时，记录压着斑马线的车辆
    if v_colors["green"] != GREEN and v_colors["yellow"] != YELLOW:
        crosswalk_blocking_vehicles = set()
        for v in vehicles_list:
            if v.pos[1] + v.height > stop_line_y and v.pos[1] < crosswalk_end_y:
                crosswalk_blocking_vehicles.add(v)
    # 黄灯时允许这些车通过
    if v_colors["yellow"] == YELLOW:
        for v in vehicles_list:
            v.allow_cross_on_yellow = v in crosswalk_blocking_vehicles
    else:
        for v in vehicles_list:
            v.allow_cross_on_yellow = False
    min_gap = 10  # 车辆间最小距离
    # 车辆移动逻辑
    if v_colors["green"] == GREEN or v_colors["yellow"] == YELLOW:
        for idx, v in enumerate(vehicles_list):
            if v_colors["green"] == GREEN:
                v.update_position()
            elif v_colors["yellow"] == YELLOW:
                if v.allow_cross_on_yellow:
                    if v.pos[1] < crosswalk_end_y:
                        v.update_position()
            # 只重置驶出屏幕的那一辆车到队尾
            if v.pos[1] > SCREEN_HEIGHT:
                # 只补充一辆新车到队尾，其余车辆保持原有顺序
                # 队尾车辆y坐标最大，新车排在其后min_gap距离
                other_cars = [car for car in vehicles_list if car is not v]
                if other_cars:
                    max_y = max(car.pos[1] for car in other_cars)
                    v.pos[1] = max(max_y - v.height - min_gap, V_ROAD_RECT.top + 50)
                else:
                    v.pos[1] = V_ROAD_RECT.top + 50
                v.allow_cross_on_yellow = False
                if v in crosswalk_blocking_vehicles:
                    crosswalk_blocking_vehicles.remove(v)
    else:  # 红灯/行人通行
        # 先收集所有未进入斑马线的车辆索引
        queue_indices = [i for i, v in enumerate(vehicles_list) if v.pos[1] + v.height < stop_line_y]
        # 队首目标位置
        next_y = stop_line_y
        for idx in reversed(queue_indices):
            v = vehicles_list[idx]
            # 目标车尾位置
            target_y = next_y - v.height - min_gap
            if v.pos[1] > target_y:
                v.pos[1] = max(target_y, V_ROAD_RECT.top + 10)  # 防止超出屏幕上方
            else:
                v.update_position()
            next_y = v.pos[1]
        # 其它车（已进入斑马线或已过）
        for v in vehicles_list:
            # 只要车头已进入斑马线（即压线或已过），就让它继续走，直到完全驶出斑马线
            if v.pos[1] + v.height >= stop_line_y:
                v.update_position()
            if v.pos[1] > SCREEN_HEIGHT:
                # 只补充一辆新车到队尾，其余车辆保持原有顺序
                # 队尾车辆y坐标最大，新车排在其后min_gap距离
                other_cars = [car for car in vehicles_list if car is not v]
                if other_cars:
                    max_y = max(car.pos[1] for car in other_cars)
                    v.pos[1] = max(max_y - v.height - min_gap, V_ROAD_RECT.top + 50)
                else:
                    v.pos[1] = V_ROAD_RECT.top + 50
                v.allow_cross_on_yellow = False
                if v in crosswalk_blocking_vehicles:
                    crosswalk_blocking_vehicles.remove(v)

    # --- 绘图 ---
    screen.fill(LIGHT_BLUE) # Light blue background

    # --- 绘制道路和人行横道 ---
    pygame.draw.rect(screen, DARK_GREY, V_ROAD_RECT) # Main road

    # --- 绘制斑马线（覆盖W_Area右到E_Area右，均匀分布） ---
    crosswalk_line_width = 14
    crosswalk_spacing = 14
    crosswalk_area_left = WAIT_AREA_WEST.right
    crosswalk_area_right = WAIT_AREA_EAST.right
    crosswalk_area_top = H_CROSSWALK_RECT_NORTH.top
    crosswalk_area_bottom = H_CROSSWALK_RECT_SOUTH.bottom
    crosswalk_width = crosswalk_area_right - crosswalk_area_left
    num_lines = int((crosswalk_width + crosswalk_spacing) // (crosswalk_line_width + crosswalk_spacing))
    for i in range(num_lines):
        x = crosswalk_area_left + i * (crosswalk_line_width + crosswalk_spacing)
        pygame.draw.rect(screen, WHITE, (x, crosswalk_area_top, crosswalk_line_width, crosswalk_area_bottom - crosswalk_area_top))

    # Draw waiting area (schematic)
    pygame.draw.rect(screen, (230,230,250), WAIT_AREA_WEST) # Light purple
    pygame.draw.rect(screen, BLACK, WAIT_AREA_WEST,1)
    draw_text(screen, "W_Area", (WAIT_AREA_WEST.centerx, WAIT_AREA_WEST.top + 5), font_s, BLACK, center_aligned=True)
    pygame.draw.rect(screen, (230,250,230), WAIT_AREA_EAST) # Light green
    pygame.draw.rect(screen, BLACK, WAIT_AREA_EAST,1)
    draw_text(screen, "E_Area", (WAIT_AREA_EAST.centerx, WAIT_AREA_EAST.top + 5), font_s, BLACK, center_aligned=True)

    # --- 绘制斑马线旁的行人信号灯（分别放入E_Area和W_Area内，缩小比例） ---
    _, p_text, p_color = tlc_unit.get_signal_display_info()
    p_font = pygame.font.Font(DEFAULT_FONT_NAME, FONT_SIZE_SMALL)
    # West Area: 靠左1/3处
    p_w_x = WAIT_AREA_WEST.left + WAIT_AREA_WEST.width // 4
    p_w_y = WAIT_AREA_WEST.centery
    p_surface_w = p_font.render(p_text, True, p_color)
    p_rect_w = p_surface_w.get_rect(center=(p_w_x, p_w_y))
    p_box_w = p_rect_w.inflate(18, 8)
    pygame.draw.rect(screen, BLACK, p_box_w, border_radius=6)
    screen.blit(p_surface_w, p_rect_w)
    # East Area: 靠右1/3处
    p_e_x = WAIT_AREA_EAST.right - WAIT_AREA_EAST.width // 4
    p_e_y = WAIT_AREA_EAST.centery
    p_surface_e = p_font.render(p_text, True, p_color)
    p_rect_e = p_surface_e.get_rect(center=(p_e_x, p_e_y))
    p_box_e = p_rect_e.inflate(18, 8)
    pygame.draw.rect(screen, BLACK, p_box_e, border_radius=6)
    screen.blit(p_surface_e, p_rect_e)

    # --- 绘制车辆 ---
    for v in vehicles_list:
        v.draw(screen)

    # --- 绘制主路上的车辆信号灯（横向排列+灯箱包围） ---
    v_light_x = V_ROAD_RECT.centerx
    v_light_y = H_CROSSWALK_RECT_NORTH.top - 40
    box_w, box_h = 90, 38
    box_rect = pygame.Rect(v_light_x - box_w//2, v_light_y - box_h//2, box_w, box_h)
    pygame.draw.rect(screen, BLACK, box_rect, border_radius=14)
    light_radius = 14
    spacing = 28
    for i, color_key in enumerate(["red", "yellow", "green"]):
        cx = v_light_x - spacing + i*spacing
        cy = v_light_y
        pygame.draw.circle(screen, v_colors[color_key], (cx, cy), light_radius)
        pygame.draw.circle(screen, (60,60,60), (cx, cy), light_radius, 2)

    # --- 绘制行人 ---
    for ped in pedestrians_list:
        ped_rsu_data = rsu_unit.pedestrian_tracking_data.get(ped.id)
        ped.draw(screen, ped_rsu_data)

    # --- Draw debug info panel (左侧) ---
    info_panel_x = 10
    info_panel_y = 10
    draw_text(screen, "PI-BREPSC Simulation", (info_panel_x, info_panel_y), font_m, BLACK)
    info_panel_y += 30
    draw_text(screen, f"Vehicle Light: {tlc_unit.vehicle_phase.upper()}", (info_panel_x, info_panel_y), font_s)
    info_panel_y += 20
    draw_text(screen, f"Pedestrian Light: {tlc_unit.pedestrian_phase.upper()}", (info_panel_x, info_panel_y), font_s)
    info_panel_y += 20
    if tlc_unit.is_pedestrian_request_servicing:
         draw_text(screen, "Servicing Pedestrian Request...", (info_panel_x, info_panel_y), font_s, ORANGE)
    info_panel_y += 20
    info_panel_y += 10

    # --- Summary of all pedestrians ---
    draw_text(screen, f"Pedestrians: {len(pedestrians_list)}", (info_panel_x, info_panel_y), font_s, (0,120,0))
    info_panel_y += 20
    for ped in pedestrians_list:
        draw_text(screen, f"{ped.id}: ({int(ped.pos[0])},{int(ped.pos[1])}) Intent: {getattr(ped, 'intent_prob', 0):.2f}", (info_panel_x+10, info_panel_y), font_s)
        info_panel_y += 18
    info_panel_y += 10

    # --- Summary of all vehicles ---
    draw_text(screen, f"Vehicles: {len(vehicles_list)}", (info_panel_x, info_panel_y), font_s, (0,0,120))
    info_panel_y += 20
    for v in vehicles_list:
        draw_text(screen, f"{v.id}: ({int(v.pos[0])},{int(v.pos[1])}) Speed: {v.speed} Color: {v.color}", (info_panel_x+10, info_panel_y), font_s)
        info_panel_y += 18
    info_panel_y += 10

    # --- Selected pedestrian details (if any) ---
    if selected_pedestrian_id and selected_pedestrian_id in rsu_unit.pedestrian_tracking_data:
        data = rsu_unit.pedestrian_tracking_data[selected_pedestrian_id]
        ped_obj = next((p for p in pedestrians_list if p.id == selected_pedestrian_id), None)
        draw_text(screen, f"Selected Pedestrian: {selected_pedestrian_id}", (info_panel_x, info_panel_y), font_s, BLUE)
        info_panel_y += 20
        if ped_obj:
            draw_text(screen, f"  Position: ({int(ped_obj.pos[0])},{int(ped_obj.pos[1])})", (info_panel_x, info_panel_y), font_s)
            info_panel_y += 18
            draw_text(screen, f"  Motion State: {data['motion_state']}", (info_panel_x, info_panel_y), font_s)
            info_panel_y += 18
            draw_text(screen, f"  Button Pressed: {ped_obj.is_requesting_button_press}", (info_panel_x, info_panel_y), font_s)
            info_panel_y += 18
            draw_text(screen, f"  Is Malicious: {ped_obj.is_malicious}", (info_panel_x, info_panel_y), font_s)
            info_panel_y += 18
        draw_text(screen, f"  Avg RSSI: {data['avg_rssi_stable']:.1f} dBm (Std: {data['rssi_std_dev']:.1f})", (info_panel_x, info_panel_y), font_s)
        info_panel_y += 18
        draw_text(screen, f"  Is Anomalous: {data['is_anomalous']} ({data['anomaly_reason']})", (info_panel_x, info_panel_y), font_s, RED if data['is_anomalous'] else BLACK)
        info_panel_y += 18
        draw_text(screen, f"  Intent Prob: {data['intent_prob']:.2f}", (info_panel_x, info_panel_y), font_s, BLACK)
        info_panel_y += 18
        draw_text(screen, f"  Confidence: {data['confidence']:.2f}", (info_panel_x, info_panel_y), font_s, BLACK)
        info_panel_y += 18
        draw_text(screen, f"  High Conf Waiting: {data['time_waiting_high_conf_sec']:.1f}s", (info_panel_x, info_panel_y), font_s)
        info_panel_y += 25
        draw_text(screen, "  Scanner RSSI:",(info_panel_x, info_panel_y), font_s)
        info_panel_y +=18
        for sc_id, rssi_hist in data["rssi_per_scanner"].items():
            if rssi_hist:
                draw_text(screen, f"    {sc_id}: {rssi_hist[-1]:.1f} dBm", (info_panel_x, info_panel_y), font_s)
            info_panel_y += 18
    # Controls
        draw_text(screen, "Controls: S/D=Spawn Ped, B=Button(Sel), M=Malicious(Sel),", (10, SCREEN_HEIGHT - 90), font_s, DARK_GREY)
        draw_text(screen, "Click=Select, ESC=Exit", (10, SCREEN_HEIGHT - 70), font_s, DARK_GREY)

    # --- Draw Edge AI info panel (right side, improved layout) ---
    edge_panel_x = SCREEN_WIDTH - 410
    edge_panel_y = 20
    panel_width = 400
    panel_height = 370
    pygame.draw.rect(screen, (245,245,255), (edge_panel_x, edge_panel_y, panel_width, panel_height), border_radius=10)
    pygame.draw.rect(screen, DARK_GREY, (edge_panel_x, edge_panel_y, panel_width, panel_height), 2, border_radius=10)
    draw_text(screen, "Edge AI Module Info", (edge_panel_x + 20, edge_panel_y + 10), font_m, (30,30,120))
    y = edge_panel_y + 50
    draw_text(screen, "Function:", (edge_panel_x + 20, y), font_s)
    y += 20
    draw_text(screen, "- Multimodal time-series feature fusion", (edge_panel_x + 35, y), font_s)
    y += 18
    draw_text(screen, "- Pedestrian intent recognition", (edge_panel_x + 35, y), font_s)
    y += 18
    draw_text(screen, "- Anomaly detection", (edge_panel_x + 35, y), font_s)
    y += 24
    draw_text(screen, "Algorithm:", (edge_panel_x + 20, y), font_s)
    y += 20
    draw_text(screen, "- Statistical + temporal features", (edge_panel_x + 35, y), font_s)
    y += 18
    draw_text(screen, "- RandomForest (default)", (edge_panel_x + 35, y), font_s)
    y += 18
    draw_text(screen, "- Extensible: LSTM/GRU/Deep Learning", (edge_panel_x + 35, y), font_s)
    y += 24
    draw_text(screen, "Decision Flow:", (edge_panel_x + 20, y), font_s)
    y += 20
    draw_text(screen, "1. Collect RSSI/motion/button/malicious", (edge_panel_x + 35, y), font_s)
    y += 18
    draw_text(screen, "2. Feature fusion, AI infers intent", (edge_panel_x + 35, y), font_s)
    y += 18
    draw_text(screen, "3. Detect anomaly, output priority", (edge_panel_x + 35, y), font_s)
    y += 18
    draw_text(screen, "4. Write to ai_priority.txt for C module", (edge_panel_x + 35, y), font_s)
    y += 24
    draw_text(screen, "Collaboration:", (edge_panel_x + 20, y), font_s)
    y += 20
    draw_text(screen, "- Python: AI decision-making", (edge_panel_x + 35, y), font_s)
    y += 18
    draw_text(screen, "- C-side: Embedded controller reads priority", (edge_panel_x + 35, y), font_s)
    y += 24
    draw_text(screen, "Research Innovation:", (edge_panel_x + 20, y), font_s, (120,30,30))
    y += 20
    draw_text(screen, "- Multimodal fusion + HW/SW co-design", (edge_panel_x + 35, y), font_s, (120,30,30))
    y += 18
    draw_text(screen, "- Extensible to end-to-end deep models", (edge_panel_x + 35, y), font_s, (120,30,30))

    # --- Edge AI Decision Making (动态决策展示) ---
    y += 18
    draw_text(screen, "--- Real-time AI Decision ---", (edge_panel_x + 20, y), font_s, (30,30,120))
    y += 20
    for ped in pedestrians_list:
        ai_res = ai_results.get(ped.id, {})
        txt = f"{ped.id}: intent={ai_res.get('intent_prob',0):.2f}  anomaly={ai_res.get('is_anomalous',False)}  priority={ai_res.get('priority','-')}"
        draw_text(screen, txt, (edge_panel_x + 25, y), font_s)
        y += 18
    # 展示本帧AI建议切换红绿灯的理由
    ai_reason = ""
    for ped in pedestrians_list:
        ai_res = ai_results.get(ped.id, {})
        if ai_res.get('priority') == 'high':
            if ai_res.get('is_anomalous'):
                ai_reason = f"{ped.id}: High priority due to anomaly!"
            elif ai_res.get('intent_prob',0) > 0.6:
                ai_reason = f"{ped.id}: High intent ({ai_res.get('intent_prob',0):.2f}) triggers green for pedestrian."
            else:
                ai_reason = f"{ped.id}: Other high priority reason."
            break
    if not ai_reason:
        ai_reason = "No high-priority pedestrian, vehicle green."
    y += 10
    draw_text(screen, f"AI Reason: {ai_reason}", (edge_panel_x + 20, y), font_s, (120,30,30))

    # --- 在斑马线区域内用三角形标识RSU传感器 ---
    rsu_color = (50, 50, 150)
    tri_size = 16
    # 西侧
    tri_w = [
        (WAIT_AREA_WEST.right + 6, H_CROSSWALK_RECT_NORTH.centery),
        (WAIT_AREA_WEST.right + 6 + tri_size, H_CROSSWALK_RECT_NORTH.centery - tri_size//2),
        (WAIT_AREA_WEST.right + 6 + tri_size, H_CROSSWALK_RECT_NORTH.centery + tri_size//2)
    ]
    pygame.draw.polygon(screen, rsu_color, tri_w)
    # 东侧
    tri_e = [
        (WAIT_AREA_EAST.left - 6, H_CROSSWALK_RECT_NORTH.centery),
        (WAIT_AREA_EAST.left - 6 - tri_size, H_CROSSWALK_RECT_NORTH.centery - tri_size//2),
        (WAIT_AREA_EAST.left - 6 - tri_size, H_CROSSWALK_RECT_NORTH.centery + tri_size//2)
    ]
    pygame.draw.polygon(screen, rsu_color, tri_e)
    # 北侧
    tri_n = [
        (V_ROAD_RECT.centerx, H_CROSSWALK_RECT_NORTH.top + 6),
        (V_ROAD_RECT.centerx - tri_size//2, H_CROSSWALK_RECT_NORTH.top + 6 + tri_size),
        (V_ROAD_RECT.centerx + tri_size//2, H_CROSSWALK_RECT_NORTH.top + 6 + tri_size)
    ]
    pygame.draw.polygon(screen, rsu_color, tri_n)
    # 南侧
    tri_s = [
        (V_ROAD_RECT.centerx, H_CROSSWALK_RECT_SOUTH.bottom - 6),
        (V_ROAD_RECT.centerx - tri_size//2, H_CROSSWALK_RECT_SOUTH.bottom - 6 - tri_size),
        (V_ROAD_RECT.centerx + tri_size//2, H_CROSSWALK_RECT_SOUTH.bottom - 6 - tri_size)
    ]
    pygame.draw.polygon(screen, rsu_color, tri_s)

    # --- 左下角闪烁手表和AI识别数量 ---
    # 统计AI识别为有过马路意图的行人数
    ai_cross_count = 0
    for ped in pedestrians_list:
        ai_res = ai_results.get(ped.id, {})
        if ai_res.get('priority') == 'high' and ai_res.get('intent_prob', 0) > 0.6:
            ai_cross_count += 1
    # 手表闪烁（每30帧闪一次）
    blink = (pygame.time.get_ticks() // 300) % 2 == 0
    watch_x = 60
    watch_y = SCREEN_HEIGHT - 90 - 75  # 再向上移动约2cm（75像素）
    # 表盘
    pygame.draw.circle(screen, (80,80,80) if blink else (180,180,180), (watch_x, watch_y), 22)
    pygame.draw.circle(screen, (220,220,220), (watch_x, watch_y), 18)
    # 表带
    pygame.draw.rect(screen, (120,120,120), (watch_x-8, watch_y-32, 16, 18), border_radius=6)
    pygame.draw.rect(screen, (120,120,120), (watch_x-8, watch_y+14, 16, 18), border_radius=6)
    # 指针
    pygame.draw.line(screen, (60,60,60), (watch_x, watch_y), (watch_x, watch_y-12), 3)
    pygame.draw.line(screen, (60,60,60), (watch_x, watch_y), (watch_x+10, watch_y), 2)
    # 手表边框
    pygame.draw.circle(screen, (30,30,30), (watch_x, watch_y), 22, 2)
    # 数字
    draw_text(screen, f"{ai_cross_count}", (watch_x+32, watch_y-10), font_l, (30,30,120))
    draw_text(screen, "AI Intent", (watch_x+32, watch_y+12), font_s, (30,30,120))

    # --- RSU感应图标与数量 ---
    rsu_x = watch_x + 110
    rsu_y = watch_y
    # 画天线底座
    pygame.draw.rect(screen, (100,100,180), (rsu_x-8, rsu_y+10, 16, 8), border_radius=3)
    # 画天线杆
    pygame.draw.rect(screen, (80,80,160), (rsu_x-2, rsu_y-10, 4, 20), border_radius=2)
    # 画信号波
    for i, r in enumerate([16, 24, 32]):
        color = (120,120,220, 180)
        pygame.draw.arc(screen, color, (rsu_x-r, rsu_y-r, 2*r, 2*r), 3.7, 5.8, 2)
    # RSU感应人数
    rsu_count = len(rsu_unit.pedestrian_tracking_data)
    draw_text(screen, f"{rsu_count}", (rsu_x+32, rsu_y-10), font_l, (30,30,120))
    draw_text(screen, "RSU Sense", (rsu_x+32, rsu_y+12), font_s, (30,30,120))

    # --- AI决策图标与状态 ---
    ai_x = rsu_x + 110
    ai_y = watch_y
    # 画AI芯片（矩形+小圆点）
    pygame.draw.rect(screen, (60,180,120), (ai_x-18, ai_y-18, 36, 36), border_radius=8)
    for dx, dy in [(-10,-10),(10,-10),(-10,10),(10,10)]:
        pygame.draw.circle(screen, (30,120,80), (ai_x+dx, ai_y+dy), 4)
    # AI决策状态
    ai_decision = "Priority Pass" if ai_cross_count > 0 else "Normal"
    draw_text(screen, ai_decision, (ai_x+32, ai_y-10), font_l, (30,30,120))
    draw_text(screen, "AI Decision", (ai_x+32, ai_y+12), font_s, (30,30,120))

    # --- Update 3D Simulation Synchronization with RSU data ---
    update_3d_sync(pedestrians_list, vehicles_list, tlc_unit.vehicle_phase, tlc_unit.pedestrian_phase, ai_module, rsu_unit)

    pygame.display.flip() # 更新整个屏幕
    clock.tick(FPS) # 控制帧率

pygame.quit()
sys.exit()