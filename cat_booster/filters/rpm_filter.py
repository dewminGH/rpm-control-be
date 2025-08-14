from ..models.fan_rpm_model import FanRpm


def filter_rpm_by_device(device_secret):
    return FanRpm.objects.filter(device_secret=device_secret)