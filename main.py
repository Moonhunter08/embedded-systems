"""
Crash and Impact Detection System for Raspberry Pi Pico 2
Uses an accelerometer (MPU6050) to detect sudden impacts
"""

from machine import Pin, I2C, UART
import time
from accelerometer_driver import MPU6050
from buzzer_driver import Buzzer
from led_driver import LEDDriver

# Configuration Constants
IMPACT_THRESHOLD = 2.5  # G-force threshold for impact detection
SAMPLE_RATE_MS = 100    # Sampling rate in milliseconds
LED_PIN = "LED"         # Built-in LED on Pico
BUZZER_PIN = 0          # Pin for buzzer/alert
I2C_SDA_PIN = 4         # I2C data pin
I2C_SCL_PIN = 5         # I2C clock pin
ALERT_DURATION_MS = 3000    # Duration of crash alert in milliseconds
ALERT_LED_FLASH_INTERVAL_MS = 100  # LED flash interval during alert

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
        
        # Initialize peripherals
        self.led = LEDDriver(LED_PIN)
        self.led.off()
        self.buzzer = Buzzer(BUZZER_PIN)
        
        # Initialize UART for serial communication (not tested)
        try:
            self.uart = UART(0, baudrate=115200)
            self.uart_available = True
        except:
            self.uart_available = False
            print("UART not available")
        
        # State variables
        self.alert_active = False
        
    def uart_send_message(self, message):
        """Send alert message via available channels"""
        print("Sending UART Message:", message)
        if self.uart_available:
            try:
                self.uart.write(message + '\n')
            except:
                pass
    
    def impact_callback(self, magnitude):
        """Trigger visual and audio alerts"""
        self.uart_send_message(f"IMPACT DETECTED! Magnitude: {magnitude:.2f}g")
        self.buzzer.buzz(frequency_hz=600)
        
        # Flash LED for during alert duration
        alert_passed = 0
        while alert_passed < ALERT_DURATION_MS:
            self.led.toggle()
            time.sleep_ms(ALERT_LED_FLASH_INTERVAL_MS)
            alert_passed += ALERT_LED_FLASH_INTERVAL_MS

        self.led.off()
        self.buzzer.stop()    
    
    def check_impact(self):
        """Check for impact events"""
        if not self.sensor_available:
            return
        try:
            magnitude = self.sensor.get_total_acceleration() 
            if magnitude > IMPACT_THRESHOLD:
                self.impact_callback(magnitude)
        except Exception as e:
            print(f"Error reading sensor: {e}")
    
    def run(self):
        """Main monitoring loop"""
        self.uart_send_message("Crash Detection System Starting...")
        self.uart_send_message(f"Impact Threshold: {IMPACT_THRESHOLD}g")
        self.uart_send_message(f"Sample Rate: {SAMPLE_RATE_MS}ms")
        self.uart_send_message("System Ready - Monitoring for impacts...")
        
        heartbeat = 0
        while True:
            try:
                self.check_impact()
                time.sleep_ms(SAMPLE_RATE_MS)
                heartbeat += SAMPLE_RATE_MS
                if heartbeat >= 1000:
                    heartbeat = 0
                    self.led.toggle()
                    
            except KeyboardInterrupt:
                self.uart_send_message("System shutting down...")
                self.led.off()
                self.buzzer.stop
                break
            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(1)

# Main execution
if __name__ == "__main__":
    detector = CrashDetector()
    detector.run()
