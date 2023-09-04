import RPi.GPIO as GPIO

class RotaryEncoder:
    def __init__(self, clk_pin, dt_pin):
        # Set the GPIO numbering mode
        GPIO.setmode(GPIO.BCM)

        # Set up the GPIO pins
        GPIO.setup(clk_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(dt_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        self.clk_pin = clk_pin
        self.dt_pin = dt_pin
        self._counter = 0
        self._prev_clk_state = GPIO.input(clk_pin)
        
        GPIO.add_event_detect(clk_pin, GPIO.BOTH, callback=self._on_rotate, bouncetime=10)
        
    @property
    def counter(self):
        return self._counter
    
    @counter.setter
    def counter(self, value):
        self._counter = value
    
    def _on_rotate(self, channel):
        clk_state = GPIO.input(self.clk_pin)
        dt_state = GPIO.input(self.dt_pin)

        if clk_state != self._prev_clk_state:
            if dt_state != clk_state:
                self.counter = 1
            else:
                self.counter = -1
            self.when_rotated()

        self._prev_clk_state = clk_state
    
    def when_rotated(self):
        pass
