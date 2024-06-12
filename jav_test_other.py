from hub import port
import motor
import force_sensor
import time

while True:
    if force_sensor.pressed(port.D):
        motor.run_for_degrees(port.B, -60, 1000)
        time.sleep(0.5)
        motor.run_for_degrees(port.B, 60, 300)
    time.sleep_ms(100)
