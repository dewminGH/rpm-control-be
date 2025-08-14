import dht
from machine import Pin, ADC
import time

# --- Sensor setup ---
dht22 = dht.DHT22(Pin(1))
mq2 = ADC(Pin(26))

MQ2_CALIBRATION_SLOPE = 0.1
MQ2_CALIBRATION_OFFSET = 200

# --- Stepper motor setup ---
# coil_pins = [
#     Pin(1, Pin.OUT),  # IN1 -> GP1
#     Pin(2, Pin.OUT),  # IN2 -> GP2
#     Pin(3, Pin.OUT),  # IN3 -> GP3
#     Pin(4, Pin.OUT)   # IN4 -> GP4
# ]

# step_sequence = [
#     [1,0,0,0],
#     [0,1,0,0],
#     [0,0,1,0],
#     [0,0,0,1],
# ]

delay_ms = 1  # motor speed (smaller = faster)
sensor_interval = 5  # seconds between sensor measurements

print('debug----------')

# Track timing for sensors
last_sensor_time = time.ticks_ms()
current_step = 0

while True:
    # --- Motor: do 1 step ---
    # step = step_sequence[current_step % len(step_sequence)]
    # for pin, val in zip(coil_pins, step):
    #     pin.value(val)
    # time.sleep_ms(delay_ms)  # control motor speed
    # current_step += 1

    # --- Sensor: check if it's time to read ---
    now = time.ticks_ms()
    if time.ticks_diff(now, last_sensor_time) >= sensor_interval * 1000:
        dht22.measure()
        t = dht22.temperature()
        h = dht22.humidity()

        gas_value = mq2.read_u16()
        ppm = (gas_value / 65535) * 100
        co2_concentration = (ppm * MQ2_CALIBRATION_SLOPE) + MQ2_CALIBRATION_OFFSET

        print(f"Estimated CO2 Concentration: {co2_concentration:.2f} ppm")
        print({"Temperature": t, "Humidity": h, "Gas Value": gas_value, "CO2 (ppm)": co2_concentration})
        print({"Temperature": t, "Humidity": h})

        last_sensor_time = now  # reset timer



