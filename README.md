# Raspberry Pi Pico 2 Crash Detection System

A MicroPython-based embedded systems project for the Raspberry Pi Pico 2 that detects crashes and impacts using an accelerometer sensor (MPU6050) and sends alerts via multiple channels.

## Features

- **Real-time Impact Detection**: Monitors acceleration in real-time to detect impacts and crashes
- **Dual Threshold System**: Separate thresholds for moderate impacts and severe crashes
- **Multiple Alert Methods**:
  - LED visual alerts (built-in LED)
  - Buzzer audio alerts
  - UART serial messages for logging/communication
- **Configurable Parameters**: Easy-to-adjust thresholds and settings via config.py
- **Robust Error Handling**: Graceful degradation if sensors or outputs are unavailable

## Hardware Requirements

### Essential Components
- **Raspberry Pi Pico 2** (or Raspberry Pi Pico W)
- **MPU6050 Accelerometer/Gyroscope Module** (6-axis IMU)
- **Micro USB Cable** (for programming and power)

### Optional Components
- **Buzzer** (active or passive, 3.3V compatible)
- **Breadboard and Jumper Wires**
- **Power Supply** (battery pack for portable operation)

## Wiring Diagram

### MPU6050 to Raspberry Pi Pico 2

```
MPU6050          Raspberry Pi Pico 2
--------         -------------------
VCC      <--->   3.3V (Pin 36)
GND      <--->   GND (Pin 38)
SDA      <--->   GP0 (Pin 1)
SCL      <--->   GP1 (Pin 2)
```

### Optional: Buzzer Connection

```
Buzzer           Raspberry Pi Pico 2
--------         -------------------
Positive <--->   GP15 (Pin 20)
Negative <--->   GND (any GND pin)
```

### Pin Reference

| Component | GPIO Pin | Physical Pin | Description |
|-----------|----------|--------------|-------------|
| I2C SDA   | GP0      | Pin 1        | I2C Data Line |
| I2C SCL   | GP1      | Pin 2        | I2C Clock Line |
| Buzzer    | GP15     | Pin 20       | Buzzer Output |
| LED       | GP25     | Built-in     | Status LED (Built-in) |

## Software Setup

### 1. Install MicroPython on Raspberry Pi Pico 2

1. Download the latest MicroPython firmware for Raspberry Pi Pico 2:
   - Visit: https://micropython.org/download/RPI_PICO2/
   - Download the `.uf2` file

2. Flash MicroPython to your Pico:
   - Hold the BOOTSEL button on the Pico
   - Connect it to your computer via USB
   - Release BOOTSEL (Pico appears as a USB drive)
   - Copy the `.uf2` file to the Pico
   - The Pico will automatically reboot with MicroPython

### 2. Upload the Project Files

You can use any of these tools to upload files:
- **Thonny IDE** (recommended for beginners)
- **rshell**
- **ampy**
- **mpremote**

#### Using Thonny IDE:
1. Install Thonny: https://thonny.org/
2. Open Thonny and select "MicroPython (Raspberry Pi Pico)" as the interpreter
3. Open `main.py` and click "Save As" -> "Raspberry Pi Pico"
4. Repeat for `config.py`

#### Using mpremote:
```bash
# Install mpremote
pip install mpremote

# Upload files
mpremote fs cp main.py :main.py
mpremote fs cp config.py :config.py
```

### 3. Run the Project

The system will automatically start when the Pico is powered on if the file is named `main.py`.

To run manually:
```python
import main
```

## Configuration

Edit `config.py` to customize the behavior:

```python
# Adjust impact detection sensitivity
IMPACT_THRESHOLD = 2.5      # Moderate impact (in g-force)
CRASH_THRESHOLD = 3.5       # Severe crash (in g-force)

# Change sampling rate
SAMPLE_RATE_MS = 100        # Check every 100ms (10 Hz)

# Pin configuration
I2C_SDA_PIN = 0             # I2C data pin
I2C_SCL_PIN = 1             # I2C clock pin
BUZZER_PIN = 15             # Buzzer pin
```

## Usage

### Starting the System

1. Power on the Raspberry Pi Pico 2
2. The LED will blink 3 times to indicate the system is ready
3. The system continuously monitors for impacts
4. Serial messages are sent via UART (115200 baud)

### Alert Behavior

**Impact Detected (Moderate):**
- LED blinks rapidly 3 times
- Serial message: "IMPACT DETECTED! Magnitude: X.XXg"
- Impact counter increments

**Crash Detected (Severe):**
- LED stays on for 2 seconds
- Buzzer sounds 5 times (if connected)
- Serial message: "CRASH DETECTED! Magnitude: X.XXg"
- Crash counter increments

### Monitoring Serial Output

Connect to the Pico's serial port to view messages:

**Using Thonny:**
- View output in the Shell window at the bottom

**Using screen (Linux/Mac):**
```bash
screen /dev/ttyACM0 115200
```

**Using PuTTY (Windows):**
- Select Serial connection
- Port: COM3 (or your Pico's port)
- Baud rate: 115200

## Calibration

To calibrate the sensor for your specific use case:

1. Place the sensor in a stable position
2. Monitor the baseline acceleration values
3. Perform test impacts of varying intensities
4. Adjust `IMPACT_THRESHOLD` and `CRASH_THRESHOLD` in `config.py`
5. Typical values:
   - Light tap: 1.5 - 2.0g
   - Moderate impact: 2.5 - 3.0g
   - Hard crash: 3.5 - 5.0g

## Troubleshooting

### MPU6050 Not Detected

**Problem:** `Could not initialize MPU6050` error

**Solutions:**
- Check wiring connections (SDA, SCL, VCC, GND)
- Verify MPU6050 is powered (3.3V)
- Try different I2C address (0x68 or 0x69)
- Check I2C bus: `i2c.scan()` should return `[104]` or `[105]`

### No Buzzer Sound

**Problem:** Buzzer doesn't make sound

**Solutions:**
- Verify buzzer is connected to GP15
- Check if buzzer is active (has internal oscillator) or passive
- For passive buzzers, you may need PWM instead of simple GPIO
- Ensure buzzer is 3.3V compatible

### False Positives

**Problem:** System detects impacts when there are none

**Solutions:**
- Increase `IMPACT_THRESHOLD` in config.py
- Check for loose connections causing vibrations
- Mount the sensor more securely
- Add `NOISE_THRESHOLD` filtering

### No LED Blink

**Problem:** LED doesn't light up

**Solution:**
- The built-in LED is on GP25 for Pico 2
- Check if your board has a different LED pin
- Try external LED on GP15 with resistor

## Project Structure

```
embedded-systems/
├── main.py              # Main application code
├── config.py            # Configuration parameters
├── README.md            # This file
└── .gitignore          # Git ignore rules
```

## Code Overview

### main.py

**MPU6050 Class:**
- Initializes the accelerometer
- Reads raw acceleration data
- Converts to g-force units
- Calculates total acceleration magnitude

**CrashDetector Class:**
- Manages all sensors and outputs
- Monitors acceleration continuously
- Triggers alerts based on thresholds
- Handles UART communication

### config.py

Contains all configurable parameters for easy customization without modifying the main code.

## Advanced Features

### Adding Additional Sensors

You can extend the system to include:
- GPS module for location tracking
- GSM module for SMS alerts
- SD card for data logging
- Temperature sensor for environmental monitoring

### Integration with IoT Platforms

Connect to IoT services:
- MQTT broker for remote monitoring
- Blynk for mobile app control
- ThingSpeak for data visualization

### Example: Extending for Data Logging

```python
# Add to main.py
import os

class CrashDetector:
    def __init__(self):
        # ... existing code ...
        self.log_file = "crash_log.txt"
    
    def log_event(self, event_type, magnitude):
        with open(self.log_file, 'a') as f:
            timestamp = time.time()
            f.write(f"{timestamp},{event_type},{magnitude:.2f}\n")
```

## Safety Considerations

⚠️ **Important Safety Notes:**

1. This is a **detection system**, not a prevention system
2. Do not rely solely on this system for critical safety applications
3. Always use proper protective equipment
4. The system has inherent latency and may not detect all impacts
5. Sensor accuracy can be affected by temperature and mounting

## Contributing

This is an open-source educational project. Feel free to:
- Report issues
- Suggest improvements
- Add new features
- Share your modifications

## License

This project is provided as-is for educational purposes.

## Resources

### Official Documentation
- [Raspberry Pi Pico Documentation](https://www.raspberrypi.com/documentation/microcontrollers/)
- [MicroPython Documentation](https://docs.micropython.org/)
- [MPU6050 Datasheet](https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6000-Datasheet1.pdf)

### Tutorials
- [Getting Started with Raspberry Pi Pico](https://projects.raspberrypi.org/en/projects/getting-started-with-the-pico)
- [MicroPython I2C Tutorial](https://docs.micropython.org/en/latest/library/machine.I2C.html)

### Community
- [Raspberry Pi Forums](https://forums.raspberrypi.com/)
- [MicroPython Forum](https://forum.micropython.org/)

## Support

For questions or issues:
1. Check the Troubleshooting section above
2. Review the MPU6050 datasheet
3. Consult the MicroPython documentation
4. Open an issue on the project repository

---

**Happy Making! 🚀**

Remember to test thoroughly and adjust thresholds for your specific application!