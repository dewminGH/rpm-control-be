from django.db import models

class FanRpm(models.Model):
    """
    predicted fan rpms
    """
    # Map to your existing SQL table name
    class Meta:
        db_table = 'fan_rpms'
        managed = False
    id              = models.BigAutoField(primary_key=True, db_column="id")
    device_secret   = models.CharField(max_length=255)
    fan_speed       = models.FloatField()
    time            = models.DateTimeField(auto_now_add=True)
    temperature     = models.FloatField()
    humidity        = models.FloatField()
    light           = models.FloatField()
    co2             = models.FloatField()
    container_type  = models.CharField(max_length=32)
