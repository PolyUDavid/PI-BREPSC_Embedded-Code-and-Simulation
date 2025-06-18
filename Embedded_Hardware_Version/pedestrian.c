#include "config.h"
#include <stdbool.h>

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

void update_pedestrian_position(Pedestrian *ped) {
    ped->x += ped->velocity_x;
    ped->y += ped->velocity_y;

    // Basic stationarity check (replace with more sophisticated logic)
    if (ped->velocity_x == 0 && ped->velocity_y == 0) {
        ped->frames_stationary++;
    } else {
        ped->frames_stationary = 0;
    }

    if (ped->frames_stationary >= STATIONARY_THRESHOLD_FRAMES_LONG) {
        strcpy(ped->motion_state, "stationary_long");
    } else if (ped->frames_stationary >= STATIONARY_THRESHOLD_FRAMES_SHORT) {
        strcpy(ped->motion_state, "stationary_short");
    } else {
        strcpy(ped->motion_state, "moving");
    }
}