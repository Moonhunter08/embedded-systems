"""
Configuration file for Crash Detection System
Adjust these values based on your specific requirements
"""

# Sensor Configuration
IMPACT_THRESHOLD = 2.5      # G-force threshold for impact detection (moderate impact)
CRASH_THRESHOLD = 3.5       # G-force threshold for crash detection (severe impact)
SAMPLE_RATE_MS = 100        # Sampling rate in milliseconds (10 Hz)

# Pin Configuration for Raspberry Pi Pico 2
LED_PIN = 25                # Built-in LED (GP25)
BUZZER_PIN = 15             # Buzzer output pin (GP15)
I2C_SDA_PIN = 0             # I2C data pin (GP0)
I2C_SCL_PIN = 1             # I2C clock pin (GP1)

# MPU6050 Accelerometer Configuration
MPU6050_ADDR = 0x68         # I2C address (0x68 or 0x69)
ACCEL_RANGE = 4             # Accelerometer range in ±g (2, 4, 8, or 16)

# Alert Configuration
IMPACT_LED_BLINKS = 3       # Number of LED blinks for impact
CRASH_BUZZER_BEEPS = 5      # Number of buzzer beeps for crash
ALERT_DURATION_MS = 2000    # Duration of crash alert in milliseconds

# UART Configuration
UART_BAUDRATE = 115200      # Serial communication baud rate
UART_ID = 0                 # UART interface number (0 or 1)

# Calibration values (adjust after testing)
GRAVITY_OFFSET = 1.0        # Expected gravity value in g
NOISE_THRESHOLD = 0.2       # Minimum acceleration change to consider

# Advanced Settings
ENABLE_UART_LOGGING = True  # Enable serial logging
ENABLE_BUZZER = True        # Enable buzzer alerts
ENABLE_LED = True           # Enable LED alerts
DEBUG_MODE = False          # Enable debug output
