# Embedded Hardware Version

This folder contains the embedded-style C code for the PI-BREPSC simulation, designed to be implemented on embedded hardware for real-world deployment.

## Folder Structure

*   `pedestrian.c`: Contains the code for simulating pedestrian behavior and state.
*   `rsu.c`: Contains the code for the Roadside Unit (RSU), including RSSI simulation, anomaly detection, and intent inference.
*   `traffic_light.c`: Contains the code for the traffic light controller, managing the traffic light phases based on pedestrian requests.
*   `config.h`: Contains the configuration parameters for the system, such as thresholds, timings, and radio parameters.
*   `edge_ai.c`: Contains a placeholder for the edge AI algorithm used for more advanced pedestrian behavior analysis.
*   `main.c`: Contains the main function and glue code to connect the different components.
*   `pedestrian.h`: Header file for `pedestrian.c`, defining the `Pedestrian` struct and function prototypes.
*   `rsu.h`: Header file for `rsu.c`, defining the RSU functions.
*   `traffic_light.h`: Header file for `traffic_light.c`, defining the `TrafficLightController` struct and function prototypes.

## Dependencies

*   `main.c` includes `config.h`, `pedestrian.h`, `rsu.h`, and `traffic_light.h`.
*   `pedestrian.c` includes `config.h` and `pedestrian.h`.
*   `rsu.c` includes `config.h` and `pedestrian.h`.
*   `traffic_light.c` includes `config.h` and `traffic_light.h`.
*   `edge_ai.c` includes `config.h` and `pedestrian.h`.

## Hardware Requirements

This code is designed to be deployed on an embedded system with the following components:

1.  **Microcontroller:** A microcontroller with sufficient processing power and memory to run the C code. Examples include ARM Cortex-M series microcontrollers.
2.  **RSU (Roadside Unit):**
    *   **BLE Scanner:** A Bluetooth Low Energy (BLE) scanner to detect BLE signals from pedestrian devices (e.g., smartwatches, smartphones).
    *   **Antenna:** An antenna for the BLE scanner.
3.  **Traffic Light Controller:**
    *   **Actuators:** Relays or other actuators to control the traffic light signals (red, yellow, green).
4.  **Edge AI Accelerator (Optional):**
    *   If using a more sophisticated AI algorithm for pedestrian behavior analysis, an edge AI accelerator (e.g., a dedicated neural network accelerator) may be required.
5.  **Power Supply:** A suitable power supply for all components.
6.  **Communication Interface:** A communication interface (e.g., UART, SPI, I2C) for communication between the microcontroller and other components.

## Hardware Communication

The hardware components communicate as follows:

1.  **BLE Scanner to Microcontroller:** The BLE scanner detects BLE signals from pedestrian devices and transmits the Received Signal Strength Indicator (RSSI) values to the microcontroller via a communication interface (e.g., UART).
2.  **Microcontroller to Traffic Light Controller:** The microcontroller controls the traffic light signals by sending signals to the actuators.
3.  **Microcontroller to Edge AI Accelerator (Optional):** If an edge AI accelerator is used, the microcontroller sends pedestrian data to the accelerator and receives the results of the AI analysis.

## Software Implementation

1.  **Pedestrian Simulation:** The `pedestrian.c` file simulates pedestrian behavior, including position, velocity, and intent to cross. In a real-world implementation, this would be replaced by data from BLE scanners.
2.  **RSU Processing:** The `rsu.c` file processes the pedestrian data, performs anomaly detection, and infers pedestrian intent.
3.  **Traffic Light Control:** The `traffic_light.c` file controls the traffic light phases based on the RSU's requests and internal logic.
4.  **Edge AI (Optional):** The `edge_ai.c` file contains a placeholder for the edge AI algorithm, which can be used to improve the accuracy of pedestrian behavior analysis.
5.  **Main Loop:** The `main.c` file contains the main loop, which continuously updates the pedestrian positions, processes the RSU data, and updates the traffic light state.

## Edge AI Integration

The `edge_ai.c` file provides a placeholder for integrating an edge AI algorithm. This algorithm can be used to:

*   Improve the accuracy of pedestrian intent inference.
*   Detect anomalous pedestrian behavior.
*   Optimize traffic light control.

The specific AI algorithm used will depend on the available hardware resources and the desired level of accuracy.

This README provides a high-level overview of the embedded hardware version of the PI-BREPSC simulation. For more detailed information, please refer to the source code.