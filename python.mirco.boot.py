# boot.py
import time
try:
    import rp2  # Pico W regulatory domain (optional but recommended)
    rp2.country('LK')  # Sri Lanka; use your country code
except:
    pass

# Small delay lets you interrupt with Ctrl+C on USB serial
time.sleep(0.5)

