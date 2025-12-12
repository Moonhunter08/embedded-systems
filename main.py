from machine import Pin, I2C
import time
import network
import uasyncio as asyncio
import network

from drivers.csv_interface import CSV_Interface
from drivers.accelerometer_driver import MPU6050_Driver
from drivers.buzzer_driver import Buzzer_Driver
from drivers.led_driver import LEDDriver
from webserver.webserver import run_server

import secrets


# Configuration Constants
IMPACT_THRESHOLD = 1.5  # G-force threshold for impact detection
SAMPLE_RATE_MS = 10    # Sampling rate in milliseconds
LED_PIN = "LED"         # Built-in LED on Pico
BUZZER_PIN = 28          # Pin for buzzer/alert
BUZZER_FREQ_HZ = 600  # Frequency for buzzer alert
I2C_SDA_PIN = 26         # I2C data pin
I2C_SCL_PIN = 27         # I2C clock pin
I2C_ID = 1              # I2C bus ID
ALERT_DURATION_MS = 1000    # Duration of crash alert in milliseconds
ALERT_LED_FLASH_INTERVAL_MS = 100  # LED flash interval during alert
CSV_FILE = "impact_log.csv"  # CSV file to log impacts

def start_wifi():
    # Modify Wi-Fi credentials in secrets.py. DO NOT commit secrets.py to VCS
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=secrets.WIFI_SSID, password=secrets.WIFI_PASS)
    ap.active(True)
    print("AP IP:", ap.ifconfig())
    print(f"WiFi hotspot started. SSID: {secrets.WIFI_SSID}")

def getTimeSinceBoot() -> str:
    """Get time since boot in HH:MM:SS format"""
    ms = time.ticks_ms()
    seconds = ms // 1000
    minutes = seconds // 60
    hours = minutes // 60
    return f"{hours:02}:{minutes % 60:02}:{seconds % 60:02}"


class CrashDetector:
    """Main crash detection system"""
    
    def __init__(self, csv_interface):
        # Initialize I2C for accelerometer
        try:
            self.i2c = I2C(I2C_ID, scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN), freq=400000)
            time.sleep_ms(100)
            self.sensor = MPU6050_Driver(self.i2c)
            self.sensor_available = True
            print("MPU6050 initialized successfully")
        except Exception as e:
            print(f"Warning: Could not initialize MPU6050: {e}")
            self.sensor_available = False
        
        # Initialize peripherals
        self.led = LEDDriver(LED_PIN)
        self.led.off()
        self.buzzer = Buzzer_Driver(BUZZER_PIN)
        
        # State variables
        self.alert_active = False

        self.csv = csv_interface
    
    async def impact_callback(self, magnitude):
        """Trigger visual and audio alerts"""
        magnitude = f"{magnitude:.2f}g"
        timestamp = getTimeSinceBoot()
        print(f"IMPACT DETECTED! Magnitude: {magnitude}")
        self.csv.write_row([timestamp, magnitude])
        self.buzzer.buzz(BUZZER_FREQ_HZ)

        # Flash LED for during alert duration
        alert_passed = 0
        while alert_passed < ALERT_DURATION_MS:
            self.led.toggle()
            await asyncio.sleep_ms(ALERT_LED_FLASH_INTERVAL_MS)
            alert_passed += ALERT_LED_FLASH_INTERVAL_MS

        self.led.off()
        self.buzzer.stop()
    
    async def check_impact(self):
        """Check for impact events"""
        if not self.sensor_available:
            return
        try:
            magnitude = self.sensor.get_total_acceleration() 
            if magnitude > IMPACT_THRESHOLD:
                await self.impact_callback(magnitude)
        except Exception as e:
            print(f"Error reading sensor: {e}")
    
    async def run_async(self):
        """Main monitoring loop"""
        print("Crash Detection System Starting...")
        print(f"Impact Threshold: {IMPACT_THRESHOLD}g")
        print(f"Sample Rate: {SAMPLE_RATE_MS}ms")
        print("System Ready - Monitoring for impacts...")
        
        heartbeat = 0
        while True:
            try:
                await self.check_impact()
                await asyncio.sleep_ms(SAMPLE_RATE_MS)
                heartbeat += SAMPLE_RATE_MS
                if heartbeat >= 1000:
                    heartbeat = 0
                    self.led.toggle()
                    
            except KeyboardInterrupt:
                print("System shutting down...")
                self.led.off()
                self.buzzer.stop()
                break
            except Exception as e:
                print(f"Error in main loop: {e}")
                await asyncio.sleep(1)


if __name__ == "__main__":
    csv_interface = CSV_Interface(CSV_FILE)
    detector = CrashDetector(csv_interface)
    start_wifi()

    asyncio.create_task(detector.run_async())
    asyncio.run(run_server(csv_interface))
