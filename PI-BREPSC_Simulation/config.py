# config.py
import pygame

# --- Pygame 显示设置 ---
SCREEN_WIDTH = 1200  # 适当增加宽度以显示更多信息
SCREEN_HEIGHT = 800
FPS = 60 # 帧率

# --- 颜色定义 ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
GREY = (200, 200, 200)
DARK_GREY = (100, 100, 100)
LIGHT_BLUE = (173, 216, 230)

# --- RSU (路边单元) 设置 ---
RSU_SCANNER_POSITIONS = { # 更明确的命名
    "scanner_N": (600, 300), # 假设十字路口中心为 (600, 400)
    "scanner_S": (600, 500),
    "scanner_W": (500, 400),
    "scanner_E": (700, 400),
}
PIXELS_PER_METER = 20 # 用于RSSI计算中距离的换算

# --- BLE 信号物理参数 ---
DEFAULT_TX_POWER_DBM = -10  # 默认发射功率 (dBm)
PATH_LOSS_EXPONENT_N = 2.7   # 路径损耗指数 (城市环境典型值)
PATH_LOSS_D0_METERS = 1.0    # 参考距离 (米)
SHADOW_FADING_SIGMA_DB = 4.0 # 阴影衰落标准差 (dB)
BODY_SHADOWING_ATTENUATION_DB_MEAN = 10.0 # 人体遮挡平均衰减 (dB)
BODY_SHADOWING_ATTENUATION_DB_STD = 3.0 # 人体遮挡衰减标准差 (dB)
# 简化的多普勒效应参数 (可选，如果行人朝向或背向扫描仪移动)
DOPPLER_MAX_RSSI_SHIFT_DB = 2.0 # 最大RSSI变化量

# --- 行人设置 ---
PEDESTRIAN_RADIUS = 8
PEDESTRIAN_SPEED_PIXELS_PER_FRAME = 1.5
# 运动状态判断阈值 (帧数)
STATIONARY_FRAMES_SHORT = int(FPS * 0.5) # 短时静止 (0.5秒)
STATIONARY_FRAMES_LONG = int(FPS * 2.0)  # 长时静止 (2秒)
PEDESTRIAN_HISTORY_SIZE = 10 # 用于判断运动状态的位置历史记录大小

# --- PI-BPRV (物理信息融合的感知与请求验证) 设置 ---
# RSSI 阈值
RSSI_VALID_RANGE_DBM = (-90, -20) # 有效RSSI范围
RSSI_WAITING_THRESHOLD_DBM = -75  # 判断为可能等待的RSSI下限
# 异常检测阈值
RSSI_JUMP_THRESHOLD_DB = 25      # RSSI异常跳变阈值 (dB)
MAX_SPEED_METERS_PER_SEC = 3.0   # 行人最大合理速度 (m/s) -> 用于运动学一致性
# 意图与置信度
INTENT_PROB_INCREMENT = 0.15
INTENT_PROB_DECREMENT = 0.08
CONFIDENCE_FROM_RSSI_FACTOR = 0.05 # (RSSI - RSSI_WAITING_THRESHOLD_DBM) * factor
CONFIDENCE_FROM_STABILITY_MAX = 0.3 # 基于RSSI稳定性的最大置信度加成
CONFIDENCE_FROM_DURATION_MAX = 0.4  # 基于等待时长的最大置信度加成 (每秒增加0.1，最多0.4)
CONFIDENCE_HIGH_THRESHOLD = 0.75
CONFIDENCE_MEDIUM_THRESHOLD = 0.5

# --- PSO-PSBF (基于物理感知的优先级服务屏障函数) 设置 ---
# 等待时间目标 (秒)
TARGET_WAITING_TIME_BLE_HIGH_CONF = 5.0 # 高置信度BLE用户
TARGET_WAITING_TIME_BLE_MEDIUM_CONF = 10.0 # 中置信度BLE用户
TARGET_WAITING_TIME_BUTTON = 8.0 # 按钮用户

# --- 交通灯控制器 (TLC) 时序设置 (帧数) ---
MIN_VEHICLE_GREEN_TIME = int(FPS * 7)
VEHICLE_YELLOW_TIME = int(FPS * 3)
PEDESTRIAN_WALK_TIME = int(FPS * 8)
PEDESTRIAN_FLASH_TIME = int(FPS * 5) # "请勿通行" 闪烁时间
ALL_RED_TIME = int(FPS * 2)

# --- 仿真界面元素位置/尺寸 ---
INTERSECTION_CENTER_X = SCREEN_WIDTH // 2
INTERSECTION_CENTER_Y = SCREEN_HEIGHT // 2
ROAD_WIDTH = 100
CROSSWALK_WIDTH = 20
# 主干道 (垂直)
V_ROAD_RECT = pygame.Rect(INTERSECTION_CENTER_X - ROAD_WIDTH // 2, 0, ROAD_WIDTH, SCREEN_HEIGHT)
# 人行横道 (东西向)
H_CROSSWALK_RECT_NORTH = pygame.Rect(V_ROAD_RECT.left - ROAD_WIDTH, INTERSECTION_CENTER_Y - ROAD_WIDTH // 2 - CROSSWALK_WIDTH, ROAD_WIDTH*2 + V_ROAD_RECT.width, CROSSWALK_WIDTH) # 上方人行道，延伸更宽
H_CROSSWALK_RECT_SOUTH = pygame.Rect(V_ROAD_RECT.left - ROAD_WIDTH, INTERSECTION_CENTER_Y + ROAD_WIDTH // 2, ROAD_WIDTH*2 + V_ROAD_RECT.width, CROSSWALK_WIDTH) # 下方人行道
# 示例等待区域 (矩形)
WAIT_AREA_WEST = pygame.Rect(H_CROSSWALK_RECT_NORTH.left, H_CROSSWALK_RECT_NORTH.top, ROAD_WIDTH, H_CROSSWALK_RECT_SOUTH.bottom - H_CROSSWALK_RECT_NORTH.top)
WAIT_AREA_EAST = pygame.Rect(V_ROAD_RECT.right, H_CROSSWALK_RECT_NORTH.top, ROAD_WIDTH, H_CROSSWALK_RECT_SOUTH.bottom - H_CROSSWALK_RECT_NORTH.top)


# 字体
FONT_SIZE_SMALL = 18
FONT_SIZE_MEDIUM = 24
FONT_SIZE_LARGE = 30
# 使用 Pygame 的默认字体或指定一个已安装的字体路径
try:
    DEFAULT_FONT_NAME = pygame.font.get_default_font()
except:
    DEFAULT_FONT_NAME = "arial" # 备用