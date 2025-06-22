#ifndef TRAFFIC_LIGHT_H
#define TRAFFIC_LIGHT_H

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

void update_traffic_light(TrafficLightController *tlc, bool pedestrian_request);

#endif