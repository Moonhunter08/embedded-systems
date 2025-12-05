import time
import math

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
        
    def _read_accel(self):
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
    
    def _get_acceleration_g(self):
        """Get acceleration in G units"""
        accel_x, accel_y, accel_z = self._read_accel()
        # Scale factor for ±4g range: 8192 LSB/g
        scale = 8192.0
        ax = accel_x / scale
        ay = accel_y / scale
        az = accel_z / scale
        return ax, ay, az
    
    def get_total_acceleration(self):
        """Get total acceleration magnitude (with gravity removed)"""
        ax, ay, az = self._get_acceleration_g()
        # Calculate magnitude and subtract 1g to account for gravity
        magnitude = math.sqrt(ax*ax + ay*ay + az*az)
        # Remove gravity offset to get actual impact acceleration
        return abs(magnitude - 1.0)
