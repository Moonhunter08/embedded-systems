# Installation and Deployment Guide

This guide provides step-by-step instructions for setting up the crash detection system on your Raspberry Pi Pico 2.

## Quick Start

### Prerequisites

1. **Hardware:**
   - Raspberry Pi Pico 2 or Pico W
   - MPU6050 accelerometer module
   - Micro USB cable
   - Optional: Buzzer (3.3V compatible)
   - Breadboard and jumper wires

2. **Software:**
   - Python 3.7 or higher (for uploading files)
   - MicroPython firmware for Pico 2
   - File transfer tool (Thonny, mpremote, or rshell)

## Step-by-Step Installation

### Step 1: Flash MicroPython Firmware

1. **Download MicroPython:**
   ```
   Visit: https://micropython.org/download/RPI_PICO2/
   Download: rp2-pico2-latest.uf2
   ```

2. **Enter BOOTSEL Mode:**
   - Disconnect the Pico from USB
   - Hold down the BOOTSEL button on the Pico
   - Connect Pico to computer while holding BOOTSEL
   - Release BOOTSEL button
   - Pico appears as a USB mass storage device (RPI-RP2)

3. **Flash Firmware:**
   - Drag and drop the `.uf2` file onto the RPI-RP2 drive
   - The Pico will automatically reboot
   - The drive will disconnect and reconnect as a MicroPython device

### Step 2: Wire the Hardware

**MPU6050 Connections:**
```
MPU6050 VCC  → Pico 3.3V (Pin 36)
MPU6050 GND  → Pico GND (Pin 38)
MPU6050 SDA  → Pico GP0 (Pin 1)
MPU6050 SCL  → Pico GP1 (Pin 2)
```

**Optional Buzzer:**
```
Buzzer +     → Pico GP15 (Pin 20)
Buzzer -     → Pico GND (any GND pin)
```

### Step 3: Upload Project Files

#### Option A: Using Thonny IDE (Recommended for Beginners)

1. **Install Thonny:**
   - Download from https://thonny.org/
   - Install and launch Thonny

2. **Configure Thonny:**
   - Click "Tools" → "Options" → "Interpreter"
   - Select "MicroPython (Raspberry Pi Pico)"
   - Select the correct COM/USB port

3. **Upload Files:**
   - Open `main.py` in Thonny
   - Click "File" → "Save As..."
   - Select "Raspberry Pi Pico"
   - Save as `main.py`
   - Repeat for `config.py`
   - Optional: Upload `test_hardware.py`

#### Option B: Using mpremote (Command Line)

1. **Install mpremote:**
   ```bash
   pip install mpremote
   ```

2. **Upload files:**
   ```bash
   # Navigate to project directory
   cd /path/to/embedded-systems

   # Upload main files
   mpremote fs cp main.py :main.py
   mpremote fs cp config.py :config.py
   
   # Optional: Upload test file
   mpremote fs cp test_hardware.py :test_hardware.py
   ```

#### Option C: Using rshell

1. **Install rshell:**
   ```bash
   pip install rshell
   ```

2. **Connect and upload:**
   ```bash
   # Connect to Pico
   rshell -p /dev/ttyACM0  # Linux
   rshell -p COM3          # Windows
   
   # In rshell:
   cp main.py /pyboard/
   cp config.py /pyboard/
   cp test_hardware.py /pyboard/
   ```

### Step 4: Test the Hardware

Before running the main program, test individual components:

1. **Connect to Pico REPL:**
   - In Thonny: Use the Shell window
   - Or use: `screen /dev/ttyACM0 115200` (Linux/Mac)
   - Or use PuTTY (Windows)

2. **Run Hardware Tests:**
   ```python
   import test_hardware
   test_hardware.run_all_tests()
   ```

3. **Expected Output:**
   ```
   === I2C Scan ===
   I2C devices found: ['0x68']
   
   === LED Test ===
   LED ON/OFF cycles...
   
   === Buzzer Test ===
   Buzzer beeps...
   
   === MPU6050 Test ===
   Reading accelerometer data...
   ```

### Step 5: Configure Settings

Edit `config.py` to customize for your application:

```python
# Sensitivity settings
IMPACT_THRESHOLD = 2.5      # Adjust based on testing
CRASH_THRESHOLD = 3.5       # Adjust based on testing

# Sampling rate
SAMPLE_RATE_MS = 100        # 100ms = 10 samples/second
```

### Step 6: Run the Main Program

1. **Manual Start:**
   ```python
   import main
   ```

2. **Automatic Start on Boot:**
   - The file is already named `main.py`
   - It will run automatically when Pico powers on
   - To prevent auto-start, rename to something else

3. **Stop the Program:**
   - Press Ctrl+C in the REPL/terminal

### Step 7: Monitor Output

1. **Serial Monitor:**
   - Baud rate: 115200
   - Watch for messages like:
     ```
     Crash Detection System Starting...
     System Ready - Monitoring for impacts...
     IMPACT DETECTED! Magnitude: 2.8g
     CRASH DETECTED! Magnitude: 4.2g
     ```

2. **LED Indicators:**
   - 3 blinks at startup = System ready
   - 3 rapid blinks = Impact detected
   - Solid for 2 seconds = Crash detected

## Calibration Guide

### Finding the Right Thresholds

1. **Baseline Testing:**
   ```python
   # In REPL, monitor normal acceleration
   import main
   detector = main.CrashDetector()
   
   # Read current values
   magnitude = detector.sensor.get_total_acceleration()
   print(f"Current: {magnitude:.2f}g")
   ```

2. **Impact Testing:**
   - Gently tap the device
   - Note the magnitude values
   - Set IMPACT_THRESHOLD slightly below these values

3. **Crash Testing:**
   - Perform harder impacts (safely!)
   - Note the magnitude values
   - Set CRASH_THRESHOLD appropriately

### Typical Calibration Values

| Event Type | Typical Range | Recommended Threshold |
|------------|---------------|----------------------|
| At rest    | 0.9 - 1.1g    | N/A                  |
| Light tap  | 1.5 - 2.0g    | IMPACT: 2.0g         |
| Moderate hit | 2.5 - 3.5g  | IMPACT: 2.5g         |
| Hard crash | 3.5 - 6.0g    | CRASH: 3.5g          |

## Troubleshooting

### Common Issues

**1. "Could not initialize MPU6050"**
- Check I2C wiring (SDA, SCL, VCC, GND)
- Run: `test_hardware.test_i2c_scan()`
- Try swapping SDA/SCL pins
- Check if MPU6050 address is 0x68 or 0x69

**2. No serial output**
- Check baud rate is 115200
- Try different USB port
- Restart Pico
- Check if UART is available

**3. False impact detections**
- Increase IMPACT_THRESHOLD
- Secure wiring to reduce vibrations
- Mount sensor firmly
- Check for loose breadboard connections

**4. No LED/Buzzer response**
- Verify pin numbers in config.py
- Test individually with test_hardware.py
- Check component connections
- Ensure 3.3V compatibility

## Advanced Configuration

### Changing I2C Pins

```python
# In config.py
I2C_SDA_PIN = 4    # Change to GP4
I2C_SCL_PIN = 5    # Change to GP5
```

### Using External LED

```python
# In config.py
LED_PIN = 16       # Use GP16 instead of built-in
```

### Adjusting Sample Rate

```python
# In config.py
SAMPLE_RATE_MS = 50    # 20 samples/second (faster)
SAMPLE_RATE_MS = 200   # 5 samples/second (slower)
```

## Project File Verification

After upload, verify files on Pico:

```python
import os
print(os.listdir())
# Should show: ['main.py', 'config.py', 'test_hardware.py']
```

## Updating the Code

To update after changes:

1. Edit files on your computer
2. Re-upload using same method as installation
3. Restart Pico or run: `import main`

## Deployment Checklist

- [ ] MicroPython firmware flashed
- [ ] MPU6050 wired correctly
- [ ] Optional buzzer connected
- [ ] Files uploaded to Pico
- [ ] Hardware tests passed
- [ ] Thresholds calibrated
- [ ] System tested with real impacts
- [ ] Documentation reviewed
- [ ] Power supply verified (for portable use)

## Next Steps

1. Test in real-world scenarios
2. Fine-tune thresholds
3. Add additional features (logging, wireless, etc.)
4. Mount in your target application
5. Consider power optimization for battery operation

## Support Resources

- MicroPython Docs: https://docs.micropython.org/
- Pico Forum: https://forums.raspberrypi.com/
- MPU6050 Guide: https://invensense.tdk.com/

---

**Installation Complete!** 🎉

Your crash detection system is ready to use. Start monitoring for impacts!
