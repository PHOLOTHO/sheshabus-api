import random
import string
from datetime import datetime


def generate_otp(length=6):
    """
    Generate a numeric OTP
    """
    return ''.join(random.choices(string.digits, k=length))


def format_time(minutes):
    """
    Format minutes into human readable time
    """
    if minutes < 60:
        return f"{minutes} min"
    else:
        hours = minutes // 60
        mins = minutes % 60
        if mins == 0:
            return f"{hours} hr"
        else:
            return f"{hours} hr {mins} min"


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two coordinates using Haversine formula
    """
    from math import radians, sin, cos, sqrt, atan2

    R = 6371  # Earth radius in kilometers

    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)

    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c