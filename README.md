# Raspberry Pi Pico 2 Crash Detection System

A MicroPython-based embedded systems project for the Raspberry Pi Pico 2W

- Detects and records impacts using an accelerometer sensor (MPU6050)
- Sounds alarm via buzzer when impact occurs
- Hosts a webpage that displays all recorded impacts in a table

Components used:
- Raspberry Pi Pico 2W
- MPU6050 Accelerometer/Gyroscope Module (6-axis IMU)
- "Keyes" passive Buzzer


## Wiring Diagram

### MPU6050 Connection

```
MPU6050          Raspberry Pi Pico 2
--------         -------------------
VCC      <--->   3.3V (Pin 36)
GND      <--->   any GND (e.g. Pin 33)
SDA      <--->   any I2C SDA (e.g. Pin 31)
SCL      <--->   any I2C SCL (e.g. Pin 32)
```

### Buzzer Connection

```
Buzzer           Raspberry Pi Pico 2
--------         -------------------
VCC      <--->   VBUS (Pin 40)
GND      <--->   any GND (e.g. Pin 38)
S        <--->   any unused GP Pin (e.g. Pin)
```

When configuring the Pin numbers in `main.py`, make sure to use the GP-Pin-Numbers instead of the absolute Pin-Numbers (e.g. Absoulte Pin 32 --> GP27)

By Datasheet, the buzzer should use 3.3V and VBUS provides 5V.
But since 3.3V is already taken by the MPU6050, we used VBUS.
No problems were observed, but it should be kept in mind.

## Setting up the access point

Add a secrets.py file in this directory and specify your WiFi credentials like this:

```
WIFI_SSID = "pico"
WIFI_PASS = "pass"
```

Then in VS Code, select All commands --> `Upload Project to Pico`

## Running the project

We used VS Code with the `Raspberry Pi Pico Project` extension to upload the project to the pico. Then it should run automatically once the pico connects to power.

## Accessing Webpage

Connect to the Pico WiFi network using the credentials specified above, then go to `http://192.168.4.1`