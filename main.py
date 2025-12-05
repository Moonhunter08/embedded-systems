"""
Crash and Impact Detection System for Raspberry Pi Pico 2
Uses an accelerometer (MPU6050) to detect sudden impacts and crashes
"""

from machine import Pin, I2C, UART
import time
from accelerometer_driver import MPU6050

# Configuration Constants
IMPACT_THRESHOLD = 2.5  # G-force threshold for impact detection
CRASH_THRESHOLD = 3.5   # G-force threshold for crash detection
SAMPLE_RATE_MS = 100    # Sampling rate in milliseconds
LED_PIN = 25            # Built-in LED on Pico
BUZZER_PIN = 15         # Pin for buzzer/alert
I2C_SDA_PIN = 0         # I2C data pin
I2C_SCL_PIN = 1         # I2C clock pin

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
