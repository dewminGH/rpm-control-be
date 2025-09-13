from django.db import models

class User(models.Model):
    """user model"""

    user_id = models.BigAutoField(primary_key=True, db_column="user_id")
    device_sc = models.CharField(max_length=255)
    user_name = models.CharField(max_length=255)
    password = models.CharField(max_length=50)
    container_type = models.CharField(max_length=50)

    class Meta:
        db_table = 'users'
        managed = False
