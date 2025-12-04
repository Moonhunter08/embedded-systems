"""
Example and test scripts for the crash detection system
This file can be used to test individual components
"""

from machine import Pin, I2C
import time

def test_i2c_scan():
    """Scan for I2C devices"""
    print("Scanning I2C bus...")
    i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)
    devices = i2c.scan()
    if devices:
        print(f"I2C devices found: {[hex(device) for device in devices]}")
    else:
        print("No I2C devices found!")
    return devices

def test_led():
    """Test the built-in LED"""
    print("Testing LED...")
    led = Pin(25, Pin.OUT)
    for i in range(5):
        print(f"LED ON (iteration {i+1})")
        led.value(1)
        time.sleep(0.5)
        print(f"LED OFF (iteration {i+1})")
        led.value(0)
        time.sleep(0.5)
    print("LED test complete")

def test_buzzer(pin=15):
    """Test buzzer on specified pin"""
    print(f"Testing buzzer on pin {pin}...")
    buzzer = Pin(pin, Pin.OUT)
    for i in range(3):
        print(f"Buzzer ON (iteration {i+1})")
        buzzer.value(1)
        time.sleep(0.3)
        print(f"Buzzer OFF (iteration {i+1})")
        buzzer.value(0)
        time.sleep(0.3)
    print("Buzzer test complete")

def test_mpu6050_basic():
    """Basic test of MPU6050 sensor"""
    print("Testing MPU6050...")
    try:
        i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)
        time.sleep_ms(100)
        
        # MPU6050 address
        addr = 0x68
        
        # Wake up MPU6050
        i2c.writeto_mem(addr, 0x6B, b'\x00')
        time.sleep_ms(100)
        
        print("Reading accelerometer data...")
        for i in range(10):
            data = i2c.readfrom_mem(addr, 0x3B, 6)
            accel_x = (data[0] << 8) | data[1]
            accel_y = (data[2] << 8) | data[3]
            accel_z = (data[4] << 8) | data[5]
            
            # Convert to signed
            if accel_x > 32767:
                accel_x -= 65536
            if accel_y > 32767:
                accel_y -= 65536
            if accel_z > 32767:
                accel_z -= 65536
            
            print(f"Sample {i+1}: X={accel_x}, Y={accel_y}, Z={accel_z}")
            time.sleep(0.5)
        
        print("MPU6050 test complete")
        return True
    except Exception as e:
        print(f"MPU6050 test failed: {e}")
        return False

def run_all_tests():
    """Run all hardware tests"""
    print("\n" + "="*50)
    print("CRASH DETECTION SYSTEM - HARDWARE TEST")
    print("="*50 + "\n")
    
    print("\n--- Test 1: I2C Scan ---")
    test_i2c_scan()
    
    print("\n--- Test 2: LED Test ---")
    test_led()
    
    print("\n--- Test 3: Buzzer Test ---")
    try:
        test_buzzer(15)
    except Exception as e:
        print(f"Buzzer test skipped: {e}")
    
    print("\n--- Test 4: MPU6050 Test ---")
    test_mpu6050_basic()
    
    print("\n" + "="*50)
    print("ALL TESTS COMPLETE")
    print("="*50 + "\n")

if __name__ == "__main__":
    run_all_tests()
