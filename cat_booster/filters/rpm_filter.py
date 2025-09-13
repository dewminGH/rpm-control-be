from ..models.fan_rpm_model import FanRpm
from users.models.user import User


def filter_rpm_by_device(device_secret):
    return FanRpm.objects.filter(device_secret=device_secret)

def filter_container_type(device_sc):
    return User.objects.filter(device_sc=device_sc)