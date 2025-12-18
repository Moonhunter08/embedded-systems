from machine import Pin, PWM

class Buzzer_Driver:
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
        self.pin = Pin(pin, Pin.OUT, value=0)
        self.pwm = None

    def buzz(self, frequency_hz):
        # Start PWM if it's not running
        if self.pwm is None:
            self.pwm = PWM(self.pin)
        self.pwm.freq(frequency_hz)
        self.pwm.duty_u16(65536 // 2)  # 50% duty cycle

    def stop(self):
        if self.pwm:
            self.pwm.duty_u16(0)
            self.pwm.deinit()
            self.pwm = None
        self.pin.init(mode=Pin.OUT, value=0)
