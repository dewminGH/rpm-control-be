import urequests as requests
import ujson
import time
import dht
import gc
from machine import Pin, ADC
import network

# run django on 0000000
# ---- CONFIG ----
API_URL = "http://192.168.1.9:8000/predict/"   # <-- replace with your Django host (LAN IP) and correct path
API_KEY = "1234"                    # <-- x-api-key value expected by your DRF auth
DEVICE_SECRET = "ds-2999"                          # <-- your device id/secret
ITEM_TYPE = "apple"                              # or whatever container type you need
SENSOR_INTERVAL = 5                             # seconds between sends

# Wi-Fi
def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(ssid, password)
        print("Connecting to Wi-Fi...")
        while not wlan.isconnected():
            time.sleep(1)
    print("Connected:", wlan.ifconfig())

connect_wifi("xxxx", "xxxxxxx")

# ---- Sensors ----
dht22 = dht.DHT22(Pin(1))
mq2 = ADC(Pin(26))

MQ2_CALIBRATION_SLOPE = 0.1
MQ2_CALIBRATION_OFFSET = 200

headers = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY,
}

def send_reading(item_type, temperature, humidity, light, cos_2, device_secret):
    payload = {
        "item_type": item_type,
        "temperature": temperature,
        "humidity": humidity,
        "light": light,
        "cos_2": cos_2,           # <-- keep in sync with your DRF serializer field name
        "device_secret": device_secret,
    }
    try:
        print(payload , headers)
        resp = requests.post(API_URL, headers=headers, data=ujson.dumps(payload))
        print("POST", resp.status_code, resp.text)
        resp.close()
        gc.collect()
    except Exception as e:
        print("POST failed:", e)

last_sensor_time = time.ticks_ms()

while True:
    now = time.ticks_ms()
    if time.ticks_diff(now, last_sensor_time) >= SENSOR_INTERVAL * 5000:
        try:
            # Read DHT22
            dht22.measure()
            t = dht22.temperature()   # °C
            h = dht22.humidity()      # %

            # MQ2 read (example CO2 estimate; calibrate as needed)
            gas_value = mq2.read_u16()
            ppm = (gas_value / 65535) * 100
            co2_concentration = (ppm * MQ2_CALIBRATION_SLOPE) + MQ2_CALIBRATION_OFFSET
            gc.collect()
            time.sleep_ms(1000)

            # Example “light” placeholder — replace with a real sensor/ADC pin if you have one
            light = 1300

            # Send to API
            send_reading(
                ITEM_TYPE,
                float(t),
                float(h),
                float(light),
                float(co2_concentration),  # or rename to "co2" on server/client consistently
                DEVICE_SECRET,
            )
            gc.collect()
            time.sleep_ms(1000)

        except Exception as e:
            print("Sensor read failed:", e)

        last_sensor_time = now
        gc.collect()

    time.sleep_ms(1000)
