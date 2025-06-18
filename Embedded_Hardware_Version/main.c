#include <stdio.h>
#include "config.h"
#include "pedestrian.h"
#include "rsu.h"
#include "traffic_light.h"

int main() {
    // Initialize traffic light controller
    TrafficLightController tlc = {VEHICLE_GREEN, PEDESTRIAN_DONT_WALK, MIN_VEHICLE_GREEN_TIME, false};

    // Example pedestrian
    Pedestrian ped1 = {"P1", 100, 100, PEDESTRIAN_RADIUS, 0, 1, 0, "moving", 0, false, 0, false};

    // Main loop (simulated)
    for (int i = 0; i < 1000; i++) {
        update_pedestrian_position(&ped1);

        // Simulate RSU processing
        process_pedestrian(&ped1, 200, 200); // Scanner at (200, 200)

        // Simulate pedestrian request (e.g., from button press)
        bool pedestrian_request = ped1.intent_to_cross;

        // Update traffic light state
        update_traffic_light(&tlc, pedestrian_request);

        // Print current traffic light state (for demonstration)
        printf("Vehicle Phase: %d, Pedestrian Phase: %d\n", tlc.vehicle_phase, tlc.pedestrian_phase);
    }

    return 0;
}