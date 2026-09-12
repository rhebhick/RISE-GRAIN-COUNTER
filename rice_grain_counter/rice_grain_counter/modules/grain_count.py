def estimate_grain_count(
    rice_bulk_volume_cm3,
    packing_factor,
    grain_volume_cm3,
    grain_mass_g,
    validation_weight_g=None,
):
    solid_rice_volume_cm3 = rice_bulk_volume_cm3 * packing_factor

    # Geometry-based mass:
    estimated_mass_g = solid_rice_volume_cm3 * (
        grain_mass_g / grain_volume_cm3
    )

    # Number of grains:
    estimated_count = solid_rice_volume_cm3 / grain_volume_cm3

    validation_count = None
    if validation_weight_g is not None and validation_weight_g > 0:
        validation_count = validation_weight_g / grain_mass_g

    return {
        "solid_rice_volume_cm3": solid_rice_volume_cm3,
        "estimated_mass_g": estimated_mass_g,
        "estimated_count": estimated_count,
        "validation_count": validation_count,
    }
