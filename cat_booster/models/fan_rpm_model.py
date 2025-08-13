from django.db import models

class FanRpm(models.Model):
    # Map to your existing SQL table name
    class Meta:
        db_table = 'fan_rpms'

    device_secret   = models.CharField(max_length=64)
    fan_speed       = models.FloatField()                 # RPM you predicted
    time            = models.DateTimeField(auto_now_add=True)  # auto-filled
    temperature     = models.FloatField()
    humidity        = models.FloatField()
    light           = models.FloatField()
    # Your column in SQL is "cO2" (odd casing). Map it cleanly to Python "co2":
    co2             = models.FloatField()
    container_type  = models.CharField(max_length=32)
