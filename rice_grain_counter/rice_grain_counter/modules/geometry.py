import math

_TO_CM = {
    "cm": 1.0,
    "mm": 0.1,
    "m": 100.0,
}

def to_cm(value, unit):
    return float(value) * _TO_CM[unit]

def calculate_rice_volume(diameter, diameter_unit, height, height_unit, packing_factor):
    diameter_cm = to_cm(diameter, diameter_unit)
    height_cm = to_cm(height, height_unit)

    radius_cm = diameter_cm / 2.0
    bulk_volume_cm3 = math.pi * radius_cm**2 * height_cm

    return {
        "diameter_cm": diameter_cm,
        "height_cm": height_cm,
        "bulk_volume_cm3": bulk_volume_cm3,
    }
