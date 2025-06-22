#include "config.h"
#include <stdbool.h>

typedef enum {
    VEHICLE_GREEN,
    VEHICLE_YELLOW,
    VEHICLE_RED
} VehiclePhase;

typedef enum {
    PEDESTRIAN_DONT_WALK,
    PEDESTRIAN_WALK,
    PEDESTRIAN_FLASH
} PedestrianPhase;

typedef struct {
    VehiclePhase vehicle_phase;
    PedestrianPhase pedestrian_phase;
    int current_phase_timer;
    bool is_pedestrian_request_servicing;
} TrafficLightController;

void update_traffic_light(TrafficLightController *tlc, bool pedestrian_request) {
    tlc->current_phase_timer--;

    if (tlc->vehicle_phase == VEHICLE_GREEN) {
        if (tlc->current_phase_timer <= 0 && pedestrian_request && !tlc->is_pedestrian_request_servicing) {
            tlc->vehicle_phase = VEHICLE_YELLOW;
            tlc->current_phase_timer = VEHICLE_YELLOW_TIME;
            tlc->is_pedestrian_request_servicing = true;
        } else if (tlc->current_phase_timer < -MIN_VEHICLE_GREEN_TIME*2) {
            tlc->current_phase_timer = MIN_VEHICLE_GREEN_TIME;
        }
    } else if (tlc->vehicle_phase == VEHICLE_YELLOW) {
        if (tlc->current_phase_timer <= 0) {
            tlc->vehicle_phase = VEHICLE_RED;
            tlc->pedestrian_phase = PEDESTRIAN_WALK;
            tlc->current_phase_timer = PEDESTRIAN_WALK_TIME;
        }
    } else if (tlc->vehicle_phase == VEHICLE_RED) {
        if (tlc->pedestrian_phase == PEDESTRIAN_DONT_WALK && tlc->current_phase_timer <= 0 && !pedestrian_request) {
            tlc->vehicle_phase = VEHICLE_GREEN;
            tlc->current_phase_timer = MIN_VEHICLE_GREEN_TIME;
            tlc->is_pedestrian_request_servicing = false;
        }
    }

    if (tlc->pedestrian_phase == PEDESTRIAN_WALK) {
        if (tlc->current_phase_timer <= 0) {
            tlc->pedestrian_phase = PEDESTRIAN_FLASH;
            tlc->current_phase_timer = PEDESTRIAN_FLASH_TIME;
        }
    } else if (tlc->pedestrian_phase == PEDESTRIAN_FLASH) {
        if (tlc->current_phase_timer <= 0) {
            tlc->pedestrian_phase = PEDESTRIAN_DONT_WALK;
        }
    }
}