import streamlit as st
from PIL import Image
import numpy as np

from modules.image_measurement import analyze_image
from modules.geometry import calculate_rice_volume
from modules.grain_properties import calculate_grain_properties
from modules.grain_count import estimate_grain_count

st.set_page_config(page_title="Rice Grain Counter", page_icon="🍚", layout="wide")

st.title("🍚 Rice Grain Counter")
st.caption(
    "Analytical estimate — not an exact grain-by-grain count. "
    "The estimate depends on average grain dimensions, rice density, container geometry, "
    "and the selected packing/void assumption."
)

with st.sidebar:
    st.header("Rice & Container Measurements")

    diameter = st.number_input("Container / plate diameter", min_value=0.1, value=20.0, step=0.1)
    diameter_unit = st.selectbox("Diameter unit", ["cm", "mm", "m"], index=0)

    height = st.number_input("Rice height / depth", min_value=0.01, value=3.0, step=0.1)
    height_unit = st.selectbox("Height unit", ["cm", "mm", "m"], index=0)

    st.subheader("Average grain dimensions")
    grain_length = st.number_input("Average grain length", min_value=0.01, value=7.0, step=0.1)
    grain_length_unit = st.selectbox("Grain length unit", ["mm", "cm", "m"], index=0)

    grain_width = st.number_input("Average grain width / diameter", min_value=0.01, value=2.0, step=0.1)
    grain_width_unit = st.selectbox("Grain width unit", ["mm", "cm", "m"], index=0)

    density = st.number_input(
        "Rice grain density",
        min_value=0.01,
        value=0.80,
        step=0.01,
        help="Use the density of the rice material, not bulk density. Example values vary by rice type and moisture."
    )
    density_unit = st.selectbox("Density unit", ["g/cm³", "kg/m³"], index=0)

    packing = st.slider(
        "Packing / solid-volume factor",
        min_value=0.30, max_value=0.95, value=0.60, step=0.01,
        help="Approximate fraction of the container's bulk volume occupied by rice grains. "
             "The remainder represents air gaps/voids."
    )

    validation_weight = st.number_input(
        "Optional total rice weight (for validation)",
        min_value=0.0, value=0.0, step=1.0
    )
    validation_unit = st.selectbox("Weight unit", ["g", "kg"], index=0)

    st.subheader("Image")
    uploaded = st.file_uploader(
        "Upload a photo of the rice container/plate",
        type=["jpg", "jpeg", "png"]
    )

st.markdown("### 1. Image / measurement view")

image_result = None
if uploaded:
    image = Image.open(uploaded).convert("RGB")
    image_result = analyze_image(np.array(image))

    col1, col2 = st.columns([2, 1])
    with col1:
        st.image(image_result["annotated"], caption="Measurement/visualization overlay", use_container_width=True)
    with col2:
        st.write("**Image assistance**")
        st.write(image_result["message"])
        if image_result["plate_circle"] is not None:
            x, y, r = image_result["plate_circle"]
            st.metric("Detected circular reference", f"center=({x}, {y}), radius={r}px")
        else:
            st.info("No reliable circular boundary was detected. Manual dimensions are still used.")
        st.caption(
            "OpenCV is used for optional circular boundary detection. "
            "MediaPipe is used only when available to identify visual reference points "
            "(hand landmarks); it does not count individual grains."
        )
else:
    st.info("Upload an image to see the visualization. The calculation can still be performed using manual measurements.")

st.markdown("### 2. Analytical calculation")

geometry = calculate_rice_volume(
    diameter=diameter,
    diameter_unit=diameter_unit,
    height=height,
    height_unit=height_unit,
    packing_factor=packing,
)

grain = calculate_grain_properties(
    length=grain_length,
    length_unit=grain_length_unit,
    width=grain_width,
    width_unit=grain_width_unit,
    density=density,
    density_unit=density_unit,
)

weight_g = validation_weight if validation_unit == "g" else validation_weight * 1000

result = estimate_grain_count(
    rice_bulk_volume_cm3=geometry["bulk_volume_cm3"],
    packing_factor=packing,
    grain_volume_cm3=grain["grain_volume_cm3"],
    grain_mass_g=grain["grain_mass_g"],
    validation_weight_g=weight_g if validation_weight > 0 else None,
)

st.markdown("### 3. Results")

c1, c2, c3 = st.columns(3)
c1.metric("Container / plate diameter", f"{geometry['diameter_cm']:.2f} cm")
c2.metric("Rice height", f"{geometry['height_cm']:.2f} cm")
c3.metric("Rice bulk volume", f"{geometry['bulk_volume_cm3']:.2f} cm³")

c4, c5, c6 = st.columns(3)
c4.metric("Estimated rice mass", f"{result['estimated_mass_g']:.2f} g")
c5.metric("Single-grain volume", f"{grain['grain_volume_cm3']:.5f} cm³")
c6.metric("Single-grain mass", f"{grain['grain_mass_g']:.5f} g")

st.success(f"### Estimated total grain count: **{result['estimated_count']:,.0f} grains**")

if result["validation_count"] is not None:
    st.info(
        f"Weight-based validation estimate: **{result['validation_count']:,.0f} grains** "
        f"from {weight_g:.2f} g of rice."
    )

with st.expander("Show all intermediate calculations"):
    st.write(f"**Diameter:** {geometry['diameter_cm']:.4f} cm")
    st.write(f"**Rice height:** {geometry['height_cm']:.4f} cm")
    st.write(f"**Bulk container volume:** {geometry['bulk_volume_cm3']:.4f} cm³")
    st.write(f"**Packing factor:** {packing:.2f}")
    st.write(f"**Solid rice volume:** {result['solid_rice_volume_cm3']:.4f} cm³")
    st.write(f"**Estimated rice mass:** {result['estimated_mass_g']:.4f} g")
    st.write(f"**Average grain length:** {grain['length_mm']:.3f} mm")
    st.write(f"**Average grain width/diameter:** {grain['width_mm']:.3f} mm")
    st.write(f"**Average grain volume:** {grain['grain_volume_cm3']:.7f} cm³")
    st.write(f"**Average grain mass:** {grain['grain_mass_g']:.7f} g")
    st.write(f"**Estimated count:** {result['estimated_count']:,.2f}")

st.markdown("### 4. Formulas used")

st.latex(r"V_{bulk} = \pi \left(\frac{D}{2}\right)^2 H")
st.write("For a roughly cylindrical pot/plate region.")

st.latex(r"V_{solid} = V_{bulk} \times P")
st.write("P is the configurable packing/solid-volume factor.")

st.latex(r"V_{grain} \approx \frac{\pi}{6}LWD")
st.write(
    "Each grain is approximated as an ellipsoid. L is length and W/D are the two "
    "cross-sectional dimensions. In this beginner version, width and thickness are "
    "both approximated by the supplied average width/diameter."
)

st.latex(r"m_{grain} = \rho V_{grain}")
st.latex(r"m_{rice} = \rho V_{solid}")
st.latex(r"N \approx \frac{m_{rice}}{m_{grain}} = \frac{V_{solid}}{V_{grain}}")
st.write(
    "If density is used consistently, it cancels in the final geometry-based count. "
    "Density is still important for estimating the rice mass and for validating the "
    "model against a measured weight."
)

st.warning(
    "This is an analytical estimate, not an exact count. Real rice grains differ in "
    "length, width, thickness, shape, moisture, and packing. The packing factor should "
    "ideally be calibrated experimentally for the particular rice type and preparation."
)
