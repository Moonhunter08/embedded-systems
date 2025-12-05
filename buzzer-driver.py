from machine import Pin, PWM
import time

buzzer = Pin(0, Pin.OUT)  # use a free GPIO pin, e.g. GP20

class Buzzer:
    """Driver for passive Buzzer

    Tested with keyes buzzer (red board)
    connect buzzer gnd to pico gnd
    connect buzzer vcc to pico 3v3 out pin (36)
    connect buzzer S to a pico GPIO pin and pass GPIO number in constructor (0 in this example)
    
    Example usage:
    buzzer = Buzzer(0)

    while True:
        buzzer.buzz(440)  # A4 note
        time.sleep(1)
        buzzer.stop()
        time.sleep(1)
    """
    
    def __init__(self, pin):
        self.pwm_pin = PWM(pin)
        duty_cycle_50_percent = 65536 // 2
        self.pwm_pin.duty_u16(duty_cycle_50_percent)
        time.sleep_ms(100)

    def buzz(self, frequency_hz):
        self.pwm_pin.freq(frequency_hz)

    def stop(self):
        self.pwm_pin.deinit()
