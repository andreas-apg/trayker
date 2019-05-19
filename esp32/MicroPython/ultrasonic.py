from hcsr04 import HCSR04
import time

#sensor = HCSR04(trigger_pin=2, echo_pin=4, echo_timeout_us=10000)
def read_ultrasonic():
    distance = sensor.distance_cm()
    print('Distance:', distance, 'cm')
	