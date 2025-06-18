# rsu_simulator.py
import math
import random
import numpy as np
from collections import deque
from config import *

class RSU:
    def __init__(self, rsu_id, scanner_configs_dict):
        self.id = rsu_id
        self.scanner_configs = scanner_configs_dict # {"scanner_id": (x,y_pos)}

        # 存储每个检测到的行人的详细数据
        # key: ped.id
        # value: dict {
        #   "rssi_per_scanner": {scanner_id: deque(maxlen=20)}, # RSSI历史
        #   "avg_rssi_stable": float, # 稳定的平均RSSI
        #   "rssi_std_dev": float,    # RSSI标准差 (稳定性指标)
        #   "last_pos": (x,y),
        #   "current_speed_mps": float,
        #   "motion_state": str,
        #   "is_at_wait_area": bool,
        #   "is_anomalous": bool,
        #   "anomaly_reason": str,
        #   "intent_prob": float,
        #   "confidence": float,
        #   "frames_high_intent": int, # 意图概率高于某个阈值的帧数
        #   "time_waiting_high_conf_sec": float # 高置信度等待时间
        # }
        self.pedestrian_tracking_data = {}

    def _simulate_rssi_value(self, ped_tx_power, ped_pos, ped_velocity_vec, scanner_pos):
        """模拟单个RSSI值，包含更丰富的物理效应"""
        dx_pixels = ped_pos[0] - scanner_pos[0]
        dy_pixels = ped_pos[1] - scanner_pos[1]
        distance_pixels = math.sqrt(dx_pixels**2 + dy_pixels**2)
        distance_meters = max(distance_pixels / PIXELS_PER_METER, 0.1) # 避免log(0)

        # 1. 路径损耗 (Log-Distance Model)
        if distance_meters <= PATH_LOSS_D0_METERS:
            path_loss_db = 0 # 简化处理非常近的情况
        else:
            path_loss_db = 10 * PATH_LOSS_EXPONENT_N * math.log10(distance_meters / PATH_LOSS_D0_METERS)

        # 2. 阴影衰落 (Shadow Fading)
        shadowing_db = random.gauss(0, SHADOW_FADING_SIGMA_DB)

        # 3. 人体遮挡 (Body Shadowing) - 概率性
        body_attenuation_db = 0
        # 简单模型：如果行人朝向远离扫描仪的方向移动，或者随机发生
        # 这里用随机模拟，更复杂的需要行人朝向数据
        if random.random() < 0.4: # 40% 概率发生遮挡
            body_attenuation_db = random.gauss(BODY_SHADOWING_ATTENUATION_DB_MEAN, BODY_SHADOWING_ATTENUATION_DB_STD)

        # 4. 简化的多普勒效应 (可选)
        # 如果行人速度分量指向或背离扫描仪，RSSI 可能略微增强或减弱
        doppler_shift_db = 0
        # TODO: 实现基于 ped_velocity_vec 和扫描仪方向的简单多普勒效应模拟
        # 例如，如果径向速度 > 阈值，则增加/减少 RSSI_DOPPLER_MAX_SHIFT_DB

        raw_rssi = ped_tx_power - path_loss_db + shadowing_db - body_attenuation_db + doppler_shift_db
        
        # 限制RSSI在合理范围
        return np.clip(raw_rssi, RSSI_VALID_RANGE_DBM[0], RSSI_VALID_RANGE_DBM[1])

    def _perform_physics_anomaly_detection(self, ped_id, ped_object, current_rssi_values):
        """执行基于物理规则的异常检测"""
        data = self.pedestrian_tracking_data[ped_id]
        data["is_anomalous"] = False # 先假设正常
        data["anomaly_reason"] = ""

        # A1. 恶意标记 (来自行人对象)
        if ped_object.is_malicious:
            data["is_anomalous"] = True
            data["anomaly_reason"] = "Marked Malicious"
            return

        # A2. RSSI 值异常跳变/不稳定
        # (需要比较当前RSSI均值和历史RSSI均值，或检查RSSI标准差)
        if data["rssi_std_dev"] > SHADOW_FADING_SIGMA_DB * 2.5: # 如果标准差远大于预期的阴影衰落
            # 进一步检查是否伴随不合理运动
            if data["motion_state"] != "moving" or data["current_speed_mps"] < 0.1:
                data["is_anomalous"] = True
                data["anomaly_reason"] = "High RSSI Variance while Stationary"
                return
        
        # A3. 运动学不一致性 (Kinematic Inconsistency)
        if data["current_speed_mps"] > MAX_SPEED_METERS_PER_SEC * 1.2: # 超过最大合理速度较多
            data["is_anomalous"] = True
            data["anomaly_reason"] = f"Implausible Speed: {data['current_speed_mps']:.1f} m/s"
            return

        # A4. RSSI 与运动状态严重不匹配
        # 例如：RSSI 持续很强但行人距离扫描仪很远，或 RSSI 变化与运动方向不符
        # 这个规则比较复杂，需要更精细的位置估计和历史分析，此处简化
        avg_current_rssi = np.mean(list(current_rssi_values.values())) if current_rssi_values else RSSI_VALID_RANGE_DBM[0]
        estimated_distance_m_avg = 0
        num_scanners = 0
        for sc_pos in self.scanner_configs.values():
            estimated_distance_m_avg += math.sqrt((ped_object.pos[0]-sc_pos[0])**2 + (ped_object.pos[1]-sc_pos[1])**2) / PIXELS_PER_METER
            num_scanners += 1
        if num_scanners > 0: estimated_distance_m_avg /= num_scanners

        if avg_current_rssi > -40 and estimated_distance_m_avg > 15: # 信号异常强但距离远
             data["is_anomalous"] = True
             data["anomaly_reason"] = "Strong RSSI at Far Distance"
             return


    def _infer_intent_and_confidence(self, ped_id, ped_object):
        """推断行人意图并评估置信度"""
        data = self.pedestrian_tracking_data[ped_id]
        if data["is_anomalous"]:
            data["intent_prob"] = 0.0
            data["confidence"] = 0.0
            data["frames_high_intent"] = 0
            return

        # 意图推断规则 (基于论文3.1.2节的特征)
        # 1. 路径损耗衍生的特征 (通过 avg_rssi_stable 和 is_at_wait_area 体现)
        # 2. 时间RSSI动态 (通过 motion_state 和 rssi_std_dev 体现)
        # 3. 多扫描仪RSSI模式 (简化为使用多个扫描仪的平均RSSI)
        # 4. 运动学一致性 (已在异常检测中初步过滤)
        
        is_waiting_behavior = (data["motion_state"] == "stationary_long" and \
                               data["is_at_wait_area"] and \
                               data["avg_rssi_stable"] > RSSI_WAITING_THRESHOLD_DBM)

        if is_waiting_behavior:
            data["intent_prob"] = min(1.0, data["intent_prob"] + INTENT_PROB_INCREMENT)
            if data["intent_prob"] >= CONFIDENCE_MEDIUM_THRESHOLD: # 意图较高时开始累积帧数
                data["frames_high_intent"] +=1
        else:
            data["intent_prob"] = max(0.0, data["intent_prob"] - INTENT_PROB_DECREMENT)
            data["frames_high_intent"] = 0 # 意图降低则重置

        # 置信度评估
        if data["intent_prob"] > 0.1: # 只有当有一定意图概率时才计算置信度
            # C1: 基于RSSI强度 (相对于等待阈值)
            conf_rssi = np.clip((data["avg_rssi_stable"] - RSSI_WAITING_THRESHOLD_DBM) * CONFIDENCE_FROM_RSSI_FACTOR, 0, 0.3)
            
            # C2: 基于RSSI稳定性 (标准差越小，稳定性越高)
            conf_stability = np.clip(CONFIDENCE_FROM_STABILITY_MAX * (1 - data["rssi_std_dev"] / (SHADOW_FADING_SIGMA_DB * 2)), 0, CONFIDENCE_FROM_STABILITY_MAX)

            # C3: 基于高意图持续时间
            conf_duration = np.clip((data["frames_high_intent"] / FPS) * 0.1, 0, CONFIDENCE_FROM_DURATION_MAX)
            
            data["confidence"] = np.clip(conf_rssi + conf_stability + conf_duration, 0, 1.0)

            # 如果行人按了按钮，直接给予较高置信度（如果意图也存在）
            if ped_object.is_requesting_button_press and data["intent_prob"] > 0.5:
                data["confidence"] = max(data["confidence"], 0.85) # 按钮请求给予较高基础置信度
        else:
            data["confidence"] = 0.0

        # 更新高置信度等待时间
        if data["confidence"] >= CONFIDENCE_HIGH_THRESHOLD:
            data["time_waiting_high_conf_sec"] += 1.0 / FPS
        elif data["confidence"] >= CONFIDENCE_MEDIUM_THRESHOLD and data["confidence"] < CONFIDENCE_HIGH_THRESHOLD:
            # 对于中等置信度，也可以累积，但可能用于不同的等待时间目标
             data["time_waiting_high_conf_sec"] += 1.0 / FPS # 简化：也累积到这个变量
        else:
            data["time_waiting_high_conf_sec"] = 0 # 置信度不足则重置

    def scan_and_process_pedestrians(self, all_pedestrians_list):
        """扫描所有行人，更新其追踪数据，执行PI-BPRV"""
        current_detected_ids = set()
        for ped_obj in all_pedestrians_list:
            current_detected_ids.add(ped_obj.id)
            if ped_obj.id not in self.pedestrian_tracking_data:
                self.pedestrian_tracking_data[ped_obj.id] = {
                    "rssi_per_scanner": {sc_id: deque(maxlen=int(FPS*2)) for sc_id in self.scanner_configs.keys()}, # 2秒RSSI历史
                    "avg_rssi_stable": RSSI_VALID_RANGE_DBM[0],
                    "rssi_std_dev": 0.0,
                    "last_pos": ped_obj.pos,
                    "current_speed_mps": 0.0,
                    "motion_state": "moving",
                    "is_at_wait_area": False,
                    "is_anomalous": False,
                    "anomaly_reason": "",
                    "intent_prob": 0.0,
                    "confidence": 0.0,
                    "frames_high_intent": 0,
                    "time_waiting_high_conf_sec": 0.0
                }
            
            data = self.pedestrian_tracking_data[ped_obj.id]
            data["last_pos"] = list(ped_obj.pos) # 存储副本
            data["motion_state"] = ped_obj.motion_state
            data["current_speed_mps"] = ped_obj.get_current_speed_mps()
            data["is_at_wait_area"] = ped_obj.is_at_wait_area

            current_rssi_this_frame = {}
            all_historical_rssi_for_std_calc = []

            for sc_id, sc_pos in self.scanner_configs.items():
                rssi = self._simulate_rssi_value(ped_obj.ble_tx_power, ped_obj.pos, ped_obj.current_velocity, sc_pos)
                data["rssi_per_scanner"][sc_id].append(rssi)
                current_rssi_this_frame[sc_id] = rssi
                all_historical_rssi_for_std_calc.extend(list(data["rssi_per_scanner"][sc_id]))
            
            if all_historical_rssi_for_std_calc:
                data["avg_rssi_stable"] = np.mean(all_historical_rssi_for_std_calc)
                data["rssi_std_dev"] = np.std(all_historical_rssi_for_std_calc)
            else: # 避免空列表的均值/标准差计算
                data["avg_rssi_stable"] = RSSI_VALID_RANGE_DBM[0]
                data["rssi_std_dev"] = 0.0


            self._perform_physics_anomaly_detection(ped_obj.id, ped_obj, current_rssi_this_frame)
            self._infer_intent_and_confidence(ped_obj.id, ped_obj)

        # 清理不再视野内的行人数据
        ids_to_remove = set(self.pedestrian_tracking_data.keys()) - current_detected_ids
        for id_rem in ids_to_remove:
            del self.pedestrian_tracking_data[id_rem]

    def determine_signal_request_priority(self):
        """
        根据 PSO-PSBF 原理确定信号请求优先级。
        返回一个优先级数字 (0: 无请求, 1: 中等请求, 2: 高请求)
        """
        highest_priority = 0
        request_reason = ""

        for ped_id, data in self.pedestrian_tracking_data.items():
            if data["is_anomalous"]: # 忽略异常行人
                continue

            ped_obj_ref = None # 需要一种方式获取原始ped_obj来检查按钮状态
            # (在实际应用中，按钮状态可能是单独的事件流，或通过ped_id关联)
            # 暂时简化：假设可以通过某种方式获取 is_requesting_button_press
            # 在当前代码中，ped_object 不直接在这里可用，需要修改主循环传递ped_obj或让RSU存一份引用

            # 检查按钮请求 (假设已同步)
            # if ped_obj_ref and ped_obj_ref.is_requesting_button_press:
            #    if data["time_waiting_high_conf_sec"] * FPS >= TARGET_WAITING_TIME_BUTTON: # 已等待足够时间
            #        highest_priority = 2 
            #        request_reason = f"Button Ped {ped_id} waited long"
            #        break # 按钮高优先级

            # 检查BLE用户
            if data["confidence"] >= CONFIDENCE_HIGH_THRESHOLD:
                if data["time_waiting_high_conf_sec"] >= TARGET_WAITING_TIME_BLE_HIGH_CONF:
                    highest_priority = 2
                    request_reason = f"BLE Ped {ped_id} (High Conf) waited {data['time_waiting_high_conf_sec']:.1f}s"
                    break # 高置信度用户达到等待上限
            elif data["confidence"] >= CONFIDENCE_MEDIUM_THRESHOLD:
                # 简化：中等置信度也用 time_waiting_high_conf_sec，但目标时间更长
                if data["time_waiting_high_conf_sec"] >= TARGET_WAITING_TIME_BLE_MEDIUM_CONF:
                    if highest_priority < 2: # 只有当没有更高优先级请求时才考虑
                        highest_priority = max(highest_priority, 1)
                        request_reason = f"BLE Ped {ped_id} (Med Conf) waited {data['time_waiting_high_conf_sec']:.1f}s"
        
        if highest_priority > 0:
             print(f"RSU: Signal request priority {highest_priority}. Reason: {request_reason}")
        return highest_priority