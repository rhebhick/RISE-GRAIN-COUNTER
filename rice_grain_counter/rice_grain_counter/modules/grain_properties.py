import math

_LENGTH_TO_MM = {
    "mm": 1.0,
    "cm": 10.0,
    "m": 1000.0,
}

def length_to_mm(value, unit):
    return float(value) * _LENGTH_TO_MM[unit]

def density_to_g_cm3(value, unit):
    if unit == "g/cm³":
        return float(value)
    if unit == "kg/m³":
        return float(value) / 1000.0
    raise ValueError("Unsupported density unit.")

def calculate_grain_properties(length, length_unit, width, width_unit, density, density_unit):
    length_mm = length_to_mm(length, length_unit)
    width_mm = length_to_mm(width, width_unit)

    # Ellipsoid approximation:
    # V = (pi/6) * L * W * T
    # T is approximated by W in this simplified model.
    grain_volume_mm3 = (math.pi / 6.0) * length_mm * width_mm * width_mm
    grain_volume_cm3 = grain_volume_mm3 / 1000.0

    density_g_cm3 = density_to_g_cm3(density, density_unit)
    grain_mass_g = density_g_cm3 * grain_volume_cm3

    return {
        "length_mm": length_mm,
        "width_mm": width_mm,
        "grain_volume_cm3": grain_volume_cm3,
        "density_g_cm3": density_g_cm3,
        "grain_mass_g": grain_mass_g,
    }
