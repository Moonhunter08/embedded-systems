from machine import Pin

class LEDDriver:
    """Driver for the onboard LED"""

    def __init__(self, pin="LED"):
        self.led = Pin(pin, Pin.OUT)

    def on(self):
        self.led.value(1)

    def off(self):
        self.led.value(0)

    def toggle(self):
        self.led.toggle()
