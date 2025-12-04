"""
Crash and Impact Detection System for Raspberry Pi Pico 2
Uses an accelerometer (MPU6050) to detect sudden impacts and crashes
"""

from machine import Pin, I2C, UART
import time
import math

# Configuration Constants
IMPACT_THRESHOLD = 2.5  # G-force threshold for impact detection
CRASH_THRESHOLD = 3.5   # G-force threshold for crash detection
SAMPLE_RATE_MS = 100    # Sampling rate in milliseconds
LED_PIN = 25            # Built-in LED on Pico
BUZZER_PIN = 15         # Pin for buzzer/alert
I2C_SDA_PIN = 0         # I2C data pin
I2C_SCL_PIN = 1         # I2C clock pin

# MPU6050 I2C address and registers
MPU6050_ADDR = 0x68
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B
ACCEL_CONFIG = 0x1C

class MPU6050:
    """Driver for MPU6050 accelerometer/gyroscope"""
    
    def __init__(self, i2c, address=MPU6050_ADDR):
        self.i2c = i2c
        self.address = address
        # Wake up the MPU6050
        self.i2c.writeto_mem(self.address, PWR_MGMT_1, b'\x00')
        time.sleep_ms(100)
        # Set accelerometer range to ±4g
        self.i2c.writeto_mem(self.address, ACCEL_CONFIG, b'\x08')
        time.sleep_ms(100)
        
    def read_accel(self):
        """Read raw accelerometer data"""
        data = self.i2c.readfrom_mem(self.address, ACCEL_XOUT_H, 6)
        # Convert to signed 16-bit values
        accel_x = self._bytes_to_int(data[0], data[1])
        accel_y = self._bytes_to_int(data[2], data[3])
        accel_z = self._bytes_to_int(data[4], data[5])
        return accel_x, accel_y, accel_z
    
    def _bytes_to_int(self, high_byte, low_byte):
        """Convert two bytes to signed integer"""
        value = (high_byte << 8) | low_byte
        if value > 32767:
            value -= 65536
        return value
    
    def get_acceleration_g(self):
        """Get acceleration in G units"""
        accel_x, accel_y, accel_z = self.read_accel()
        # Scale factor for ±4g range: 8192 LSB/g
        scale = 8192.0
        ax = accel_x / scale
        ay = accel_y / scale
        az = accel_z / scale
        return ax, ay, az
    
    def get_total_acceleration(self):
        """Get total acceleration magnitude (with gravity removed)"""
        ax, ay, az = self.get_acceleration_g()
        # Calculate magnitude and subtract 1g to account for gravity
        magnitude = math.sqrt(ax*ax + ay*ay + az*az)
        # Remove gravity offset to get actual impact acceleration
        return abs(magnitude - 1.0)

class CrashDetector:
    """Main crash detection system"""
    
    def __init__(self):
        # Initialize I2C for accelerometer
        try:
            self.i2c = I2C(0, scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN), freq=400000)
            time.sleep_ms(100)
            self.sensor = MPU6050(self.i2c)
            self.sensor_available = True
            print("MPU6050 initialized successfully")
        except Exception as e:
            print(f"Warning: Could not initialize MPU6050: {e}")
            self.sensor_available = False
        
        # Initialize LED
        self.led = Pin(LED_PIN, Pin.OUT)
        self.led.value(0)
        
        # Initialize buzzer (optional)
        try:
            self.buzzer = Pin(BUZZER_PIN, Pin.OUT)
            self.buzzer.value(0)
            self.buzzer_available = True
        except:
            self.buzzer_available = False
            print("Buzzer not available on pin", BUZZER_PIN)
        
        # Initialize UART for serial communication (optional)
        try:
            self.uart = UART(0, baudrate=115200)
            self.uart_available = True
        except:
            self.uart_available = False
            print("UART not available")
        
        # State variables
        self.impact_count = 0
        self.crash_count = 0
        self.last_impact_time = 0
        self.alert_active = False
        
    def send_message(self, message):
        """Send alert message via available channels"""
        print(message)
        if self.uart_available:
            try:
                self.uart.write(message + '\n')
            except:
                pass
    
    def trigger_alert(self, alert_type, magnitude):
        """Trigger visual and audio alerts"""
        if alert_type == "impact":
            self.impact_count += 1
            self.send_message(f"IMPACT DETECTED! Magnitude: {magnitude:.2f}g | Count: {self.impact_count}")
            # Blink LED rapidly 3 times
            for _ in range(3):
                self.led.value(1)
                time.sleep_ms(100)
                self.led.value(0)
                time.sleep_ms(100)
        
        elif alert_type == "crash":
            self.crash_count += 1
            self.send_message(f"CRASH DETECTED! Magnitude: {magnitude:.2f}g | Count: {self.crash_count}")
            # Keep LED on and sound buzzer
            self.led.value(1)
            if self.buzzer_available:
                # Sound buzzer in pattern
                for _ in range(5):
                    self.buzzer.value(1)
                    time.sleep_ms(200)
                    self.buzzer.value(0)
                    time.sleep_ms(100)
            time.sleep(2)
            self.led.value(0)
        
        self.last_impact_time = time.ticks_ms()
    
    def check_impact(self):
        """Check for impact/crash events"""
        if not self.sensor_available:
            return
        
        try:
            # Get total acceleration
            magnitude = self.sensor.get_total_acceleration()
            
            # Check for crash (severe impact)
            if magnitude > CRASH_THRESHOLD:
                self.trigger_alert("crash", magnitude)
            # Check for impact (moderate impact)
            elif magnitude > IMPACT_THRESHOLD:
                self.trigger_alert("impact", magnitude)
                
        except Exception as e:
            print(f"Error reading sensor: {e}")
    
    def run(self):
        """Main monitoring loop"""
        self.send_message("Crash Detection System Starting...")
        self.send_message(f"Impact Threshold: {IMPACT_THRESHOLD}g")
        self.send_message(f"Crash Threshold: {CRASH_THRESHOLD}g")
        self.send_message(f"Sample Rate: {SAMPLE_RATE_MS}ms")
        
        # Blink LED to indicate system ready
        for _ in range(3):
            self.led.value(1)
            time.sleep_ms(200)
            self.led.value(0)
            time.sleep_ms(200)
        
        self.send_message("System Ready - Monitoring for impacts...")
        
        while True:
            try:
                self.check_impact()
                time.sleep_ms(SAMPLE_RATE_MS)
            except KeyboardInterrupt:
                self.send_message("System shutting down...")
                self.led.value(0)
                if self.buzzer_available:
                    self.buzzer.value(0)
                break
            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(1)

# Main execution
if __name__ == "__main__":
    detector = CrashDetector()
    detector.run()
