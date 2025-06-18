#include "config.h"
#include "pedestrian.h"
#include <math.h>
#include <stdio.h> // For printf (debugging)

// Simplified RSSI simulation (replace with actual hardware readings)
int simulate_rssi(Pedestrian *ped, int scanner_x, int scanner_y) {
    int dx = ped->x - scanner_x;
    int dy = ped->y - scanner_y;
    float distance = sqrt(dx*dx + dy*dy);
    // Basic path loss model (replace with calibration data)
    return DEFAULT_TX_POWER_DBM - (int)(20 * log10(distance));
}

// Basic anomaly detection (replace with ML model)
bool is_pedestrian_anomalous(Pedestrian *ped, int rssi) {
    if (ped->is_malicious) return true;
    // Example: check if RSSI is unexpectedly high
    if (rssi > RSSI_WAITING_THRESHOLD_DBM) {
        return true;
    }
    return false;
}

// Basic intent inference (replace with ML model)
bool infer_pedestrian_intent(Pedestrian *ped, int rssi) {
    // Example: if pedestrian is stationary and RSSI is high, assume intent to cross
    if (strcmp(ped->motion_state, "stationary_long") == 0 && rssi > RSSI_WAITING_THRESHOLD_DBM) {
        return true;
    }
    return false;
}

// Example function to process pedestrian data
void process_pedestrian(Pedestrian *ped, int scanner_x, int scanner_y) {
    int rssi = simulate_rssi(ped, scanner_x, scanner_y);
    bool is_anomalous = is_pedestrian_anomalous(ped, rssi);
    bool intent_to_cross = infer_pedestrian_intent(ped, rssi);

    // For demonstration purposes, print some info
    printf("Pedestrian %s: RSSI=%d, Anomalous=%s, Intent=%s\n",
           ped->id, rssi, is_anomalous ? "true" : "false", intent_to_cross ? "true" : "false");

    // TODO: Add logic to request traffic light change based on intent
}