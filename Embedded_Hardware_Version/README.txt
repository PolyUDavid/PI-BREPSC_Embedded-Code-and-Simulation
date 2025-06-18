Embedded Hardware Version

This folder contains the embedded-style C code for the PI-BREPSC simulation, designed to be implemented on embedded hardware for real-world deployment.

Folder Structure

*   pedestrian.c: Contains the code for simulating pedestrian behavior and state.
*   rsu.c: Contains the code for the Roadside Unit (RSU), including RSSI simulation, anomaly detection, and intent inference.
*   traffic_light.c: Contains the code for the traffic light controller, managing the traffic light phases based on pedestrian requests.
*   config.h: Contains the configuration parameters for the system, such as thresholds, timings, and radio parameters.
*   edge_ai.c: Contains a placeholder for the edge AI algorithm used for more advanced pedestrian behavior analysis.
*   main.c: Contains the main function and glue code to connect the different components.
*   pedestrian.h: Header file for pedestrian.c, defining the Pedestrian struct and function prototypes.
*   rsu.h: Header file for rsu.c, defining the RSU functions.
*   traffic_light.h: Header file for traffic_light.c, defining the TrafficLightController struct and function prototypes.

Dependencies

*   main.c includes config.h, pedestrian.h, rsu.h, and traffic_light.h.
*   pedestrian.c includes config.h and pedestrian.h.
*   rsu.c includes config.h and pedestrian.h.
*   traffic_light.c includes config.h and traffic_light.h.
*   edge_ai.c includes config.h and pedestrian.h.

Hardware Requirements

This code is designed to be deployed on an embedded system with the following components:

1.  Microcontroller: A microcontroller is the central processing unit of the embedded system. It executes the C code, manages the hardware components, and makes decisions about traffic light control.
    *   **Architecture:** ARM Cortex-M series (e.g., STM32, Nordic nRF52, Espressif ESP32) are commonly used due to their low power consumption and wide availability.
    *   **Clock Speed:** A clock speed of 64 MHz or higher is recommended for real-time processing.
    *   **Memory:** Sufficient Flash memory (e.g., 256 KB or more) to store the program code and RAM (e.g., 64 KB or more) for data storage.
    *   **Peripherals:** UART, SPI, I2C, GPIO pins for communication with the BLE scanner, traffic light actuators, and other components.
    *   **Real-Time Operating System (RTOS):** An RTOS (e.g., FreeRTOS, Zephyr) can be used to manage the tasks and resources of the embedded system.
2.  RSU (Roadside Unit): The RSU is responsible for detecting pedestrians and transmitting their data to the microcontroller.
    *   BLE Scanner: A Bluetooth Low Energy (BLE) scanner is essential for detecting signals from pedestrian devices.
        *   **Scanning Interval and Window:** The scanning interval (time between scans) and scanning window (duration of each scan) need to be carefully configured to balance detection probability and power consumption. Typical values are a scanning interval of 100ms and a scanning window of 50ms.
        *   **Advertising Channels:** The BLE scanner should be configured to scan all three advertising channels (37, 38, and 39) to maximize the chances of detecting pedestrian devices.
        *   **RSSI Calibration:** The RSSI values from the BLE scanner need to be calibrated to account for antenna gain, cable loss, and other factors. Calibration can be performed by measuring the RSSI at known distances from a BLE beacon.
        *   **Data Filtering:** The RSU should filter out invalid or unreliable RSSI readings. This can be done by implementing a moving average filter or a Kalman filter.
    *   Antenna: An antenna is required for the BLE scanner to receive signals.
        *   **Type:** Chip antenna, PCB trace antenna, or external antenna.
        *   **Gain:** 0 dBi to 3 dBi (higher gain may improve range but also increase directionality).
        *   **Impedance:** 50 Ohms
        *   **Polarization:** Linear
        *   **Connector (if external):** SMA, u.FL, or similar.
3.  Traffic Light Controller: The traffic light controller is responsible for switching the traffic light signals based on commands from the microcontroller.
    *   Actuators: Relays or other actuators are needed to control the traffic light signals.
        *   **Type:** Electromechanical relays, solid-state relays (SSRs), or TRIACs. SSRs are generally preferred due to their faster switching speed and longer lifespan.
        *   **Voltage Rating:** 120V/240V AC (depending on the traffic light voltage).
        *   **Current Rating:** Sufficient to handle the traffic light current (typically a few amps).
        *   **Isolation:** Optocoupled isolation for safety.
        *   **Switching Speed:** Fast switching speed for responsive traffic light control.
4.  Edge AI Accelerator (Optional): If using a more sophisticated AI algorithm for pedestrian behavior analysis, an edge AI accelerator may be required.
    *   **Type:** Dedicated neural network accelerator (e.g., Google Edge TPU, Intel Movidius Myriad X), FPGA, or high-performance microcontroller with DSP capabilities.
        *   **Memory:** Sufficient on-chip memory to store the AI model and intermediate data. The amount of memory required will depend on the size and complexity of the AI model.
        *   **Processing Power:** Measured in TOPS (tera operations per second). A higher TOPS rating indicates greater processing power.
        *   **Power Consumption:** Low power consumption is crucial for embedded applications.
        *   **Framework Support:** TensorFlow Lite, Caffe, or other embedded AI frameworks.
5.  Power Supply: A suitable power supply for all components.
        *   **Voltage:** 3.3V, 5V, or other voltage depending on the components.
        *   **Current:** Sufficient current to power all components simultaneously. A power budget should be created to determine the current requirements of each component.
        *   **Regulation:** Stable voltage regulation to prevent damage to the components. Linear regulators or switching regulators can be used.
        *   **Battery (Optional):** For battery-powered operation, a suitable battery and charging circuit are required. Lithium-ion batteries are commonly used due to their high energy density.
6.  Communication Interface: A communication interface (e.g., UART, SPI, I2C) for communication between the microcontroller and other components.
        *   **UART:** Universal Asynchronous Receiver/Transmitter for serial communication. UART is commonly used for debugging and simple data transfer.
        *   **SPI:** Serial Peripheral Interface for high-speed communication with peripherals. SPI is suitable for communicating with sensors and other peripherals that require high data rates.
        *   **I2C:** Inter-Integrated Circuit for communication with multiple devices on a shared bus. I2C is suitable for communicating with sensors and other devices that do not require high data rates.
        *   **CAN:** Controller Area Network for robust communication in automotive and industrial applications. CAN is suitable for applications that require high reliability and noise immunity.
        *   **Ethernet:** For network connectivity and remote monitoring. Ethernet allows the embedded system to be connected to a local network or the internet.
        *   **Cellular (Optional):** For remote communication and data transmission over cellular networks. Cellular connectivity allows the embedded system to be deployed in remote locations without access to a wired network.

Hardware Communication

The hardware components communicate as follows:

1.  BLE Scanner to Microcontroller: The BLE scanner detects BLE signals from pedestrian devices and transmits the Received Signal Strength Indicator (RSSI) values to the microcontroller via a communication interface (e.g., UART). The data format and communication protocol should be well-defined.
2.  Microcontroller to Traffic Light Controller: The microcontroller controls the traffic light signals by sending signals to the actuators. The control signals should be carefully designed to ensure safe and reliable operation of the traffic lights.
3.  Microcontroller to Edge AI Accelerator (Optional): If an edge AI accelerator is used, the microcontroller sends pedestrian data to the accelerator and receives the results of the AI analysis. The data format and communication protocol should be optimized for performance.

Software Implementation

1.  Pedestrian Simulation: The pedestrian.c file simulates pedestrian behavior, including position, velocity, and intent to cross. In a real-world implementation, this would be replaced by data from BLE scanners.
2.  RSU Processing: The rsu.c file processes the pedestrian data, performs anomaly detection, and infers pedestrian intent.
3.  Traffic Light Control: The traffic_light.c file controls the traffic light phases based on the RSU's requests and internal logic.
4.  Edge AI (Optional): The edge_ai.c file contains a placeholder for the edge AI algorithm, which can be used to improve the accuracy of pedestrian behavior analysis.
5.  Main Loop: The main.c file contains the main loop, which continuously updates the pedestrian positions, processes the RSU data, and updates the traffic light state.

Edge AI Integration

The edge_ai.c file provides a placeholder for integrating an edge AI algorithm. This algorithm can be used to:

*   Improve the accuracy of pedestrian intent inference.
*   Detect anomalous pedestrian behavior.
*   Optimize traffic light control.

The specific AI algorithm used will depend on the available hardware resources and the desired level of accuracy.

This README provides a high-level overview of the embedded hardware version of the PI-BREPSC simulation. For more detailed information, please refer to the source code.