# Raspberry Pi Pico W DS18B20 Temperature Sensor

A simple yet effective temperature monitoring project using the Raspberry Pi Pico W and a DS18B20 digital temperature sensor. This setup reads temperature data in Celsius (and optionally Fahrenheit) and is ready for integration into larger IoT or data logging projects.

## Hardware Requirements

- **Microcontroller**: Raspberry Pi Pico W
- **Sensor**: DS18B20 Waterproof Temperature Sensor (or similar)
- **Resistor**: 4.7kΩ (for the data line pull-up)
- **Breadboard & Jumper Wires**

## Wiring Diagram

The DS18B20 uses a 1-Wire protocol, requiring a pull-up resistor on the data line.

| DS18B20 Pin | Raspberry Pi Pico W Pin | Notes |
| :--- | :--- | :--- |
| **VDD (Red)** | **VSYS** | Power input (3.3V - 5V range) |
| **GND (Black)** | **GND** | Common ground |
| **DATA (Yellow)** | **GP22** | Data line |
| **Resistor** | **VSYS to GP22** | 4.7kΩ pull-up resistor |

> **Note**: Ensure the resistor is connected between the **VSYS** (power) rail and the **GP22** data pin.

## Software Setup

This project assumes you are using **MicroPython** on the Raspberry Pi Pico W.

### 1. Install MicroPython Firmware
Ensure your Pico W is flashed with the latest MicroPython firmware.

### 2. Required Libraries
The DS18B20 driver is not always included in the standard MicroPython build. You will likely need to load the `onewire` and `ds18x20` libraries.

If you are using the standard MicroPython build, you may need to upload the following files to your device:
- `onewire.py`
- `ds18x20.py`

*(These can be found in the MicroPython GitHub repository under `ports/rp2/modules`)*
