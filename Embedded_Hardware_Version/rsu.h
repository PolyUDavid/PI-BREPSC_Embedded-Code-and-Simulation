#ifndef RSU_H
#define RSU_H

#include "pedestrian.h"
#include <stdbool.h>

// Simplified RSSI simulation (replace with actual hardware readings)
int simulate_rssi(Pedestrian *ped, int scanner_x, int scanner_y);

// Basic anomaly detection (replace with ML model)
bool is_pedestrian_anomalous(Pedestrian *ped, int rssi);

// Basic intent inference (replace with ML model)
bool infer_pedestrian_intent(Pedestrian *ped, int rssi);

// Example function to process pedestrian data
void process_pedestrian(Pedestrian *ped, int scanner_x, int scanner_y);

#endif