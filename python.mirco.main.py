import urequests as requests
import ujson
import time
import dht
import gc
from machine import Pin, ADC, I2C, reset
import network

API_URL = "http://192.168.1.9:8000/predict/"
API_KEY = "1234"
DEVICE_SECRET = "ds-2999"
ITEM_TYPE = "apple"
SENSOR_INTERVAL = 5  # seconds

# ===== Motor tunables =====
MOTOR_MODE = "half"     # 'full' = 2048 steps/rev, 'half' = 4096 steps/rev (smoother, easier start)
MOTOR_DELAY_US = 1200   # initial delay; will be updated by mapping
MOTOR_CLOCKWISE = True

# ---- Wi-Fi ----
def connect_wifi(ssid, password, tries=8, quiet=False):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(ssid, password)
        if not quiet: print("Wi-Fi: connecting...")
        n = 0
        while not wlan.isconnected() and n < tries:
            n += 1
            time.sleep(1)
            if not quiet: print("Wi-Fi: wait", n)
    if wlan.isconnected():
        if not quiet: print("Wi-Fi: OK", wlan.ifconfig())
        return True
    if not quiet: print("Wi-Fi: FAILED")
    return False

# connect_wifi("SLT-4G_1F85A4", "2CE2D8E5")
connect_wifi("Dewmin", "0779062527")

# ---- Sensors ----
dht22 = dht.DHT22(Pin(1))
mq2 = ADC(Pin(26))
MQ2_CALIBRATION_SLOPE = 0.1
MQ2_CALIBRATION_OFFSET = 200

# GY-30
i2c = I2C(0, sda=Pin(12), scl=Pin(13), freq=100000)

BH1750_ADDR = 0x23  # 0x23 if ADDR left floating, 0x5C if tied to VCC
BH1750_MODE = 0x10  # Continuously H-resolution mode

def bh1750_read():
    try:
        print("Scan:", i2c.scan())
        devices = i2c.scan()
        if not devices:
            print("⚠️ No I2C devices found")
        else:
            print("I2C devices found:", [hex(d) for d in devices])
        # trigger measurement
        i2c.writeto(BH1750_ADDR, bytes([BH1750_MODE]))
        # measurement time for H-resolution ≈ 120ms; 180ms safe
        time.sleep_ms(180)
        data = i2c.readfrom(BH1750_ADDR, 2)
        raw = (data[0] << 8) | data[1]
        lux = raw / 1.2   # datasheet conversion
        return lux
    except Exception as e:
        # non-fatal: print error and return None
        print("BH1750 read error:", e)
        return 0

# ==== STEPPER (ULN2003) ====
# Change if your IN1..IN4 wiring is different
PIN_ORDER = (2, 3, 4, 5)  # GP2->IN1, GP3->IN2, GP4->IN3, GP5->IN4
pins = [Pin(p, Pin.OUT) for p in PIN_ORDER]

HALFSTEP = [
    (1,0,0,0),(1,1,0,0),(0,1,0,0),(0,1,1,0),
    (0,0,1,0),(0,0,1,1),(0,0,0,1),(1,0,0,1),
]
FULLSTEP = [
    (1,1,0,0),(0,1,1,0),(0,0,1,1),(1,0,0,1),
]

def _coils(a,b,c,d):
    p0,p1,p2,p3 = pins
    p0.value(a); p1.value(b); p2.value(c); p3.value(d)

def release():
    for p in pins: p.value(0)

# --- RPM mapping helpers (real fan rpm -> safe stepper speed) ---
def map_real_to_stepper_rpm(real_rpm, in_min=900.0, in_max=1600.0, out_min=2.0, out_max=20.0):
    if real_rpm < in_min: real_rpm = in_min
    if real_rpm > in_max: real_rpm = in_max
    frac = (real_rpm - in_min) / (in_max - in_min)
    return out_min + frac * (out_max - out_min)

def rpm_to_delay_us(stepper_rpm, steps_per_rev):
    # delay_us = 60s / (rpm * steps_per_rev)
    if stepper_rpm < 0.1: stepper_rpm = 0.1
    return int(60_000_000 / (stepper_rpm * steps_per_rev))

def _parse_first_float_from_str(s):
    num = ""
    seen = False
    for ch in s:
        if ch.isdigit() or ch in ".-":
            num += ch
            seen = True
        elif seen:
            break
    try:
        return float(num)
    except:
        return None

def extract_real_rpm(resp_data):
    """
    Accepts:
      - {"data": "fan rpm [1438.7751355]"}
      - "fan rpm [1438.77]"
      - {"data": 1438.7}
    Returns: float or None
    """
    val = resp_data
    if isinstance(val, dict):
        val = val.get("data", val.get("rpm", val))
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        return _parse_first_float_from_str(val)
    return None

# --- Non-blocking stepper state machine ---
_motor = {
    "seq": HALFSTEP if MOTOR_MODE == "half" else FULLSTEP,
    "idx": 0,
    "steps_left": 0,
    "delay_us": MOTOR_DELAY_US,
    "next_ts": 0,
    "running": False,
    "inc": 1,   # 1 = CW, -1 = CCW
}

def motor_start_one_rev(mode=MOTOR_MODE, delay_us=MOTOR_DELAY_US, clockwise=MOTOR_CLOCKWISE):
    """
    Start one revolution non-blocking. Adjust delay_us for speed.
    mode: 'full' (2048 steps) or 'half' (4096 steps)
    """
    seq = FULLSTEP if mode == "full" else HALFSTEP
    steps = 2048 if mode == "full" else 4096

    _motor["seq"] = seq
    _motor["idx"] = 0
    _motor["steps_left"] = steps
    _motor["delay_us"] = int(delay_us)
    _motor["inc"] = 1 if clockwise else -1
    _motor["running"] = True
    _motor["next_ts"] = time.ticks_us()      # step can happen immediately
    print("moter runing...")  # keep your log

def motor_tick():
    """Advance motor; catch up if we're late to avoid stalls."""
    m = _motor
    if not m["running"]:
        return

    now = time.ticks_us()
    steps_burst = 0
    max_burst = 16  # allow a bigger catch-up after prints/HTTP

    while time.ticks_diff(now, m["next_ts"]) >= 0:
        a,b,c,d = m["seq"][m["idx"]]
        _coils(a,b,c,d)

        m["steps_left"] -= 1
        m["idx"] += m["inc"]
        n = len(m["seq"])
        if m["idx"] >= n: m["idx"] = 0
        elif m["idx"] < 0: m["idx"] = n - 1

        # keep cadence based on previous target time (prevents drift)
        m["next_ts"] = time.ticks_add(m["next_ts"], m["delay_us"])

        steps_burst += 1
        if m["steps_left"] <= 0:
            m["running"] = False
            release()
            break
        if steps_burst >= max_burst:
            break

def motor_stop():
    _motor["running"] = False
    release()
    print('stoped')

# ---- HTTP ----
headers = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY,
    "Connection": "close",  # don't keep sockets around
}

_fail_count = 0
FAIL_RESET_LIMIT = 6
LOW_MEM_RESET = 20000  # bytes

def _truncate(s, max_len):
    try:
        if len(s) > max_len:
            return s[:max_len] + "...<trunc>"
    except:
        pass
    return s

def safe_float(val, default=0.0):
    try:
        f = float(val)
        if f != f or f == float("inf") or f == float("-inf"):
            return default
        return round(f, 4)
    except:
        return default


def send_reading(item_type, temperature, humidity, light, cos_2, device_secret, *, want_json=True, max_text=256):
    """
    POST sensor data.
    Returns: (status_code, data)
      - data is dict if want_json and JSON parse succeeds
      - else data is a (possibly truncated) string body
    Keeps all memory-safety measures (timeouts, close, GC, low-mem reset).
    """
    global _fail_count
    payload = {
        "item_type": item_type,
        "temperature": safe_float(temperature,30),
        "humidity": safe_float(humidity,72),
        "light": round(light,2) or 1300,
        "cos_2": safe_float(cos_2,200),
        "device_secret": device_secret,
    }

    body = None
    resp = None
    code = None
    out = None
    try:
        body = ujson.dumps(payload)
        # build once
        print(body)
        resp = requests.post(API_URL, headers=headers, data=body, timeout=8)
        code = resp.status_code

        # Only read the body once; keep it small
        txt = resp.text if resp is not None else ""
        if want_json:
            try:
                out = ujson.loads(txt)
            except:
                out = _truncate(txt, max_text)
        else:
            out = _truncate(txt, max_text)

        if code != 200:
            print("POST !200:", code)
        _fail_count = 0
    except Exception as e:
        _fail_count += 1
        if _fail_count >= FAIL_RESET_LIMIT:
            try:
                print("Restarting Wi-Fi...")
                wlan = network.WLAN(network.STA_IF)
                wlan.active(False)
                time.sleep(1)
                wlan.active(True)
                connect_wifi("Dewmin", "0779062527", quiet=True)
                _fail_count = 0
            except Exception as e2:
                print("Wi-Fi restart failed:", e2)
                # reset()
        code = code if code is not None else -1
        out = None
    finally:
        try:
            if resp:
                resp.close()
        except:
            pass
        del body
        gc.collect()
        try:
            if gc.mem_free() < LOW_MEM_RESET:
                print("Low mem, resetting device...")
                time.sleep(0.2)
                reset()
        except:
            pass

    return code, out

# ==== MAIN LOOP ====
last_sensor_time = time.ticks_ms()

while True:
    # advance motor without blocking; catches up if late
    motor_tick()
    if not _motor["running"]:
        motor_start_one_rev()   # uses current _motor["delay_us"]

    now = time.ticks_ms()
    # real "seconds" gate
    if time.ticks_diff(now, last_sensor_time) >= SENSOR_INTERVAL * 2500:
        try:
            # SENSORS — keep your logs
            dht22.measure()
            t = dht22.temperature()
            print('s1 read -done')
            h = dht22.humidity()
            print('s2 read -done')

            gas_value = mq2.read_u16()
            ppm = (gas_value / 65535.0) * 100.0
            co2_concentration = (ppm * MQ2_CALIBRATION_SLOPE) + MQ2_CALIBRATION_OFFSET

            # GY-30
            light = bh1750_read()
            if light >0 and light <1:
                light=1
            if light >= 9000:
                light = 9000
            print(light)
            light = round(light, 2)
            print(light)
            print('payload', ITEM_TYPE, t, h, light, co2_concentration, DEVICE_SECRET)

            # ---- send and safely get response back ----
            code, resp_data = send_reading(
                ITEM_TYPE,
                t,
                h,
                light,
                co2_concentration,
                DEVICE_SECRET,
                want_json=True,     # set False if you prefer raw text
                max_text=256,       # guard against huge bodies
            )

            # log response (compact)
            if isinstance(resp_data, dict):
                printable = resp_data.get("data", resp_data)
            else:
                printable = resp_data
            print("POST", code, printable)

            # ---- map real RPM -> stepper speed ----
            real_rpm = extract_real_rpm(resp_data)
            if real_rpm is not None:
                stepper_rpm = map_real_to_stepper_rpm(real_rpm, 900.0, 1600.0, 2.0, 20.0)
                steps_per_rev = 4096 if MOTOR_MODE == "half" else 2048
                new_delay = rpm_to_delay_us(stepper_rpm, steps_per_rev)

                # clamp for torque (too small delay may stall)
                if new_delay < 700:
                    new_delay = 700

                _motor["delay_us"] = int(new_delay)
                print("mapped:", real_rpm, "→ stepper", stepper_rpm, "rpm | delay_us =", _motor["delay_us"])
            else:
                print("WARN: couldn’t parse real RPM from response")

        except Exception as e:
            print("Sensor read failed:", e)

        last_sensor_time = now
        gc.collect()

    # tiny yield so we don't hog CPU, but don't starve motor_tick
    time.sleep_us(200)
 
