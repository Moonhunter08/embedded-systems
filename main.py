from machine import Pin, I2C
import time
import network
import asyncio
import _thread

from drivers.csv_interface import CSV_Interface
from drivers.accelerometer_driver import MPU6050_Driver
from drivers.buzzer_driver import Buzzer_Driver
from drivers.led_driver import LEDDriver
from webserver.webserver import run_server

import secrets

# Configuration Constants
IMPACT_THRESHOLD = 4.5
SAMPLE_RATE_MS = 10
LED_PIN = "LED"
BUZZER_PIN = 28
BUZZER_FREQ_HZ = 600
I2C_SDA_PIN = 26
I2C_SCL_PIN = 27
ALERT_DURATION_MS = 500
ALERT_LED_FLASH_INTERVAL_MS = 100
CSV_FILE = "impact_log.csv"

def start_wifi():
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=secrets.WIFI_SSID, password=secrets.WIFI_PASS)
    ap.active(True)
    print("AP IP:", ap.ifconfig())
    print(f"WiFi hotspot started. SSID: {secrets.WIFI_SSID}")

def getTimeSinceBoot() -> str:
    """Get time since boot in MM:SS::MSMS format"""
    ms = time.ticks_ms()
    seconds = ms // 1000
    minutes = seconds // 60
    return f"{minutes:02}:{seconds % 60:02}:{ms % 60:02}"

class CrashDetector:
    def __init__(self, csv_interface):
        try:
            self.i2c = I2C(1, scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN), freq=400000)
            time.sleep_ms(100)
            self.sensor = MPU6050_Driver(self.i2c)
            self.sensor_available = True
            print("MPU6050 initialized successfully")
        except Exception as e:
            print(f"Warning: Could not initialize MPU6050: {e}")
            self.sensor_available = False
        
        self.led = LEDDriver(LED_PIN)
        self.led.off()
        self.buzzer = Buzzer_Driver(BUZZER_PIN)
        
        self.csv = csv_interface

    def impact_callback(self, magnitude):
        magnitude = f"{magnitude:.2f}g"
        timestamp = getTimeSinceBoot()
        
        self.csv.write_row([timestamp, magnitude])
        
        # --- UPDATE TRIGGER FOR WEBSERVER ---
        # Increment the shared counter so the website knows to reload
        self.csv.impact_count += 1
        # ------------------------------------

        self.buzzer.buzz(BUZZER_FREQ_HZ)

        try:
            alert_passed = 0
            while alert_passed < ALERT_DURATION_MS:
                self.led.toggle()
                time.sleep_ms(ALERT_LED_FLASH_INTERVAL_MS)
                alert_passed += ALERT_LED_FLASH_INTERVAL_MS
        finally:
            self.led.off()
            self.buzzer.stop()
    
    def check_impact(self):
        if not self.sensor_available:
            return
        try:
            magnitude = self.sensor.get_total_acceleration() 
            if magnitude > IMPACT_THRESHOLD:
                self.impact_callback(magnitude)
        except Exception as e:
            print(f"Error reading sensor: {e}")
    
    def run(self):
        print("Crash Detection System Starting on Core 1...")
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
                break
            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(1)

if __name__ == "__main__":
    csv_interface = CSV_Interface(CSV_FILE)
    
    # --- INITIALIZE SHARED COUNTER ---
    # We add this attribute dynamically so main.py and webserver.py can share it
    csv_interface.impact_count = 0 
    # ---------------------------------

    detector = CrashDetector(csv_interface)
    start_wifi()

    # Start detector on the second core (Core 1)
    _thread.start_new_thread(detector.run, ())
    
    # Start web server on the main core (Core 0)
    asyncio.run(run_server(csv_interface))