import numpy as np
from collections import deque
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os

class EdgeAIModule:
    """
    Edge AI module for pedestrian intent recognition and anomaly detection.
    - Uses time-series features (RSSI, motion, button, etc.)
    - Multi-modal fusion (statistical + temporal)
    - Outputs: intent probability, anomaly flag, signal priority suggestion
    """
    def __init__(self, window_size=20, model_path=None):
        self.window_size = window_size
        self.data_buffer = {}
        self.scaler = StandardScaler()
        self.model = None
        if model_path and os.path.exists(model_path):
            self.model = joblib.load(model_path)
        else:
            self.model = RandomForestClassifier(n_estimators=50)
            # For demo, not trained

    def update_pedestrian(self, ped_id, rssi, motion_state, button, is_malicious):
        if ped_id not in self.data_buffer:
            self.data_buffer[ped_id] = deque(maxlen=self.window_size)
        self.data_buffer[ped_id].append({
            'rssi': rssi,
            'motion': motion_state,
            'button': button,
            'malicious': is_malicious
        })

    def extract_features(self, ped_id):
        buf = self.data_buffer.get(ped_id, [])
        if not buf:
            return np.zeros(10)
        rssi_seq = [x['rssi'] for x in buf]
        motion_seq = [x['motion'] for x in buf]
        button_seq = [x['button'] for x in buf]
        malicious_seq = [x['malicious'] for x in buf]
        # Statistical features
        features = [
            np.mean(rssi_seq), np.std(rssi_seq),
            np.mean(motion_seq), np.std(motion_seq),
            np.mean(button_seq), np.sum(button_seq),
            np.mean(malicious_seq), np.sum(malicious_seq),
            rssi_seq[-1] if rssi_seq else 0,
            motion_seq[-1] if motion_seq else 0
        ]
        return np.array(features)

    def predict(self, ped_id):
        X = self.extract_features(ped_id).reshape(1, -1)
        X_scaled = self.scaler.fit_transform(X)
        # For demo, random output
        intent_prob = np.clip(np.random.normal(0.7, 0.2), 0, 1)
        is_anomalous = bool(np.random.rand() > 0.85)
        priority = 'high' if intent_prob > 0.6 and not is_anomalous else 'low'
        return {
            'intent_prob': float(intent_prob),
            'is_anomalous': is_anomalous,
            'priority': priority
        }

# Example usage:
# ai = EdgeAIModule()
# ai.update_pedestrian(1, -65, 1, 1, 0)
# result = ai.predict(1) 