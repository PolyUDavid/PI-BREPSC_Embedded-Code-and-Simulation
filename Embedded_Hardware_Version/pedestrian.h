#ifndef PEDESTRIAN_H
#define PEDESTRIAN_H

#include <stdbool.h>
#include <string.h>

#define STATIONARY_THRESHOLD_FRAMES_SHORT 60
#define STATIONARY_THRESHOLD_FRAMES_LONG 180

typedef struct {
    char id[3];
    int x;
    int y;
    int radius;
    int color; // Placeholder, can be more complex
    int velocity_x;
    int velocity_y;
    char motion_state[20]; // "moving", "stationary_short", "stationary_long"
    int frames_stationary;
    bool intent_to_cross;
    int ble_transmit_power;
    bool is_malicious;
} Pedestrian;

void update_pedestrian_position(Pedestrian *ped);

#endif