# Rice Grain Counter 🍚

A beginner-friendly Streamlit application that estimates the number of rice grains from container geometry and average grain properties.

## Important

This application **does not count individual grains** and does not use deep-learning object detection.

It produces an **analytical estimate** based on:

- container/plate diameter
- rice height
- average grain length
- average grain width/diameter
- rice density
- packing/solid-volume factor
- optional measured total weight

## Mathematical model

### 1. Container volume

The rice is approximated as a cylinder:

`V_bulk = π × (D/2)^2 × H`

where:

- `D` = container/plate diameter
- `H` = rice height/depth

### 2. Packing factor

Rice contains air gaps between grains, so the grains do not occupy all of the bulk volume:

`V_solid = V_bulk × P`

where `P` is the packing/solid-volume factor.

For example, `P = 0.60` means approximately 60% of the measured bulk volume is occupied by rice material and the remaining 40% is treated as void space.

### 3. Single-grain volume

A rice grain is approximated as an ellipsoid:

`V_grain = π/6 × L × W × T`

For simplicity, the application assumes:

`T ≈ W`

so:

`V_grain ≈ π/6 × L × W²`

### 4. Single-grain mass

Using rice material density:

`m_grain = ρ × V_grain`

### 5. Total rice mass

`m_rice = ρ × V_solid`

### 6. Estimated count

`N = V_solid / V_grain`

Equivalently, using mass:

`N = m_rice / m_grain`

When the same density is used consistently, density cancels in the geometry-based count. Density is still useful for estimating mass and for checking the model against a real weighing.

### 7. Optional weight validation

If the user supplies measured rice weight:

`N_weight = m_measured / m_grain`

This gives an independent estimate that can be compared with the geometry-based estimate.

## Image processing

### OpenCV

OpenCV attempts to detect a circular boundary using Hough Circle Transform. This is only a rough visual aid; the physical diameter entered by the user remains the authoritative measurement.

### MediaPipe

MediaPipe Hands is used optionally to identify hand landmarks when a hand appears in the image. These landmarks are visual reference points only and are **not used to count individual grains**.

The project intentionally avoids deep-learning object detection for grain-by-grain counting.

## Folder structure

```text
rice_grain_counter/
│
├── app.py
├── requirements.txt
├── README.md
│
└── modules/
    ├── __init__.py
    ├── image_measurement.py
    ├── geometry.py
    ├── grain_properties.py
    └── grain_count.py
```

## Setup

### Windows

Open Command Prompt or PowerShell in the project folder:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

### macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Then open the Streamlit address shown in the terminal.

## Suggested hackathon experiment

For better results, calibrate the packing factor using your actual rice type:

1. Measure a known quantity of rice by weight.
2. Measure the approximate volume occupied by that rice.
3. Calculate its effective packing factor.
4. Repeat several times.
5. Use the average packing factor in the application.

Also measure average grain length and width from a representative sample rather than relying on one grain.

## Limitations

- The pot/plate is approximated as a cylinder.
- A real pot may have sloped sides or a curved bottom.
- Rice grains are not identical ellipsoids.
- Width is used as a proxy for grain thickness.
- Packing changes with rice type, cooking state, moisture, shaking, and arrangement.
- A photo alone cannot reliably determine physical dimensions without a calibrated reference.
- Therefore, the displayed result is an estimate, not an exact count.
