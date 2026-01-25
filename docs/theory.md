# Heat Exchanger Theory

## Table of Contents
- [Introduction](#introduction)
- [Fundamental Concepts](#fundamental-concepts)
- [LMTD Method](#lmtd-method)
- [NTU-Effectiveness Method](#ntu-effectiveness-method)
- [Flow Arrangements](#flow-arrangements)
- [Heat Transfer Coefficient](#heat-transfer-coefficient)

---

## Introduction

A heat exchanger is a device that transfers thermal energy between two or more fluids at different temperatures without mixing them. Heat exchangers are critical components in HVAC systems, power plants, chemical processes, and many other applications.

### Basic Principle

Heat always flows from hot to cold. In a heat exchanger:
- Hot fluid loses heat and cools down
- Cold fluid gains heat and warms up
- The fluids are separated by a wall (typically metal)
- Heat transfers through the wall via conduction and convection

---

## Fundamental Concepts

### Heat Transfer Rate (Q)

The amount of thermal energy transferred per unit time, measured in Watts (W) or kilowatts (kW).

For the hot fluid:
```
Q = m_hot × Cp_hot × (T_hot_in - T_hot_out)
```

For the cold fluid:
```
Q = m_cold × Cp_cold × (T_cold_out - T_cold_in)
```

Where:
- m = mass flow rate (kg/s)
- Cp = specific heat capacity (J/kg·K)
- T = temperature (°C or K)

### Energy Balance

By conservation of energy (1st Law of Thermodynamics):
```
Q_hot = Q_cold
```

Heat lost by hot fluid = Heat gained by cold fluid

### Heat Capacity Rate (C)

The product of mass flow rate and specific heat:
```
C = m × Cp  (W/K)
```

- C_min = minimum of C_hot and C_cold
- C_max = maximum of C_hot and C_cold
- C_ratio = C_min / C_max (dimensionless, 0 to 1)

---

## LMTD Method

Log Mean Temperature Difference is the design method used when all temperatures are known.

### Basic Equation

```
Q = U × A × LMTD
```

Where:
- U = overall heat transfer coefficient (W/m²·K)
- A = heat transfer area (m²)
- LMTD = log mean temperature difference (°C or K)

### LMTD Calculation

**For Counter Flow:**
```
ΔT₁ = T_hot_in - T_cold_out
ΔT₂ = T_hot_out - T_cold_in

LMTD = (ΔT₁ - ΔT₂) / ln(ΔT₁/ΔT₂)
```

**For Parallel Flow:**
```
ΔT₁ = T_hot_in - T_cold_in
ΔT₂ = T_hot_out - T_cold_out

LMTD = (ΔT₁ - ΔT₂) / ln(ΔT₁/ΔT₂)
```

### When to Use LMTD

Use LMTD when you want to DESIGN a heat exchanger:
- All inlet and outlet temperatures are known
- Flow rates are known
- Want to find: Required area (A)

### Example Problem

**Given:**
- Hot water: 90°C → 50°C, 2 kg/s
- Cold water: 25°C → 45°C, 3 kg/s
- U = 500 W/m²·K
- Counter flow arrangement

**Find:** Required heat exchanger area

**Solution:**

Step 1 - Calculate heat transfer:
```
Q_hot = 2 × 4180 × (90-50) = 334,400 W = 334.4 kW
Q_cold = 3 × 4180 × (45-25) = 250,800 W = 250.8 kW
Q_avg = 292.6 kW
```

Step 2 - Calculate LMTD:
```
ΔT₁ = 90 - 45 = 45°C
ΔT₂ = 50 - 25 = 25°C
LMTD = (45-25)/ln(45/25) = 20/0.588 = 34.0°C
```

Step 3 - Calculate area:
```
A = Q/(U×LMTD) = 292,600/(500×34.0) = 17.2 m²
```

---

## NTU-Effectiveness Method

Number of Transfer Units method is used for rating existing heat exchangers.

### Key Parameters

**NTU (Number of Transfer Units):**
```
NTU = (U × A) / C_min
```

Dimensionless parameter representing heat exchanger "size"

**Effectiveness:**
```
ε = Q_actual / Q_maximum
```

Ratio of actual heat transfer to maximum possible heat transfer

**Maximum Heat Transfer:**
```
Q_max = C_min × (T_hot_in - T_cold_in)
```

This is the theoretical maximum if one fluid changes temperature all the way to the inlet temperature of the other fluid.

### Effectiveness Correlations

**Counter Flow:**
```
If C_ratio < 1:
  ε = [1 - exp(-NTU(1-C_ratio))] / [1 - C_ratio×exp(-NTU(1-C_ratio))]

If C_ratio = 1:
  ε = NTU / (1 + NTU)
```

**Parallel Flow:**
```
ε = [1 - exp(-NTU(1+C_ratio))] / (1 + C_ratio)
```

### When to Use NTU

Use NTU method when you want to ANALYZE an existing heat exchanger:
- Inlet temperatures are known
- Heat exchanger area is known
- Want to find: Outlet temperatures and performance

### Example Problem

**Given:**
- Hot water: 90°C inlet, 2 kg/s
- Cold water: 25°C inlet, 3 kg/s
- Area = 15 m²
- U = 500 W/m²·K
- Counter flow

**Find:** Outlet temperatures and heat transfer

**Solution:**

Step 1 - Calculate C values:
```
C_hot = 2 × 4180 = 8,360 W/K
C_cold = 3 × 4180 = 12,540 W/K
C_min = 8,360 W/K
C_max = 12,540 W/K
C_ratio = 8,360/12,540 = 0.667
```

Step 2 - Calculate NTU:
```
NTU = (500 × 15) / 8,360 = 0.898
```

Step 3 - Calculate effectiveness:
```
ε = [1 - exp(-0.898×(1-0.667))] / [1 - 0.667×exp(-0.898×(1-0.667))]
ε = 0.537 or 53.7%
```

Step 4 - Calculate Q:
```
Q_max = 8,360 × (90-25) = 543,400 W = 543.4 kW
Q = 0.537 × 543.4 = 291.8 kW
```

Step 5 - Calculate outlet temperatures:
```
T_hot_out = 90 - 291,800/8,360 = 55.1°C
T_cold_out = 25 + 291,800/12,540 = 48.3°C
```

---

## Flow Arrangements

### Counter Flow

```
Hot:  ──────────────────>
         Heat Transfer
Cold: <──────────────────
```

**Characteristics:**
- Fluids flow in opposite directions
- Most efficient arrangement
- Can achieve close temperature approach
- Hot outlet can be colder than cold outlet
- Maximum LMTD for given temperatures

**Advantages:**
- Highest effectiveness for given NTU
- Smallest size for given duty
- Best for close temperature approaches

**Applications:**
- High-efficiency heat recovery
- Processes requiring maximum efficiency
- Close temperature approach needed

### Parallel Flow

```
Hot:  ──────────────────>
         Heat Transfer
Cold: ──────────────────>
```

**Characteristics:**
- Fluids flow in same direction
- Less efficient than counter flow
- Limited temperature approach
- Hot outlet always warmer than cold outlet

**Advantages:**
- More uniform wall temperatures
- Better for temperature-sensitive materials
- Simpler to design

**Applications:**
- Temperature-sensitive processes
- When uniform wall temperature needed
- Simpler heat recovery applications

### Cross Flow

```
Hot:  ↓↓↓↓↓↓↓↓
      ─────────
Cold: ────────→
```

**Characteristics:**
- Fluids flow perpendicular to each other
- Efficiency between counter and parallel flow
- Common in gas-liquid applications

**Applications:**
- Air conditioning coils
- Radiators
- Gas-to-liquid heat transfer

---

## Heat Transfer Coefficient

The overall heat transfer coefficient (U) represents the ease with which heat flows through the heat exchanger.

### Overall Heat Transfer Coefficient

```
1/U = 1/h_hot + t_wall/k_wall + 1/h_cold + R_fouling
```

Where:
- h_hot = convection coefficient on hot side (W/m²·K)
- h_cold = convection coefficient on cold side (W/m²·K)
- t_wall = wall thickness (m)
- k_wall = wall thermal conductivity (W/m·K)
- R_fouling = fouling resistance (m²·K/W)

### Typical U-Values

| Fluid Combination | HX Type | U-value (W/m²·K) |
|-------------------|---------|------------------|
| Water - Water | Shell-and-Tube | 800 - 1,500 |
| Water - Water | Plate | 3,000 - 7,000 |
| Water - Oil | Shell-and-Tube | 100 - 400 |
| Water - Air | Finned Tube | 25 - 100 |
| Air - Air | Plate | 10 - 40 |
| Steam - Water | Shell-and-Tube | 1,500 - 4,000 |

### Factors Affecting U-Value

**Fluid Properties:**
- Thermal conductivity
- Viscosity
- Density

**Flow Conditions:**
- Velocity (Reynolds number)
- Turbulence
- Flow pattern

**Surface Conditions:**
- Fouling
- Surface roughness
- Scale buildup

**Geometry:**
- Tube diameter
- Fin configuration
- Flow passages

---

## Design Considerations

### Temperature Approach

The temperature approach is the minimum temperature difference between hot and cold fluids.

**Counter flow:** min(T_hot_out - T_cold_in, T_hot_in - T_cold_out)

**Parallel flow:** T_hot_out - T_cold_out

Typical approaches:
- 5-10°C: Good design, economical
- 2-5°C: Requires larger area, more expensive
- Less than 2°C: Very large area, rarely economical

### Second Law of Thermodynamics

Heat always flows from hot to cold. Invalid conditions:
- T_hot_out less than T_cold_in
- T_cold_out greater than T_hot_in

### Practical Limitations

**Pressure Drop:** Higher velocities improve heat transfer but increase pumping cost

**Fouling:** Surfaces get dirty over time, reducing performance

**Corrosion:** Material selection critical for fluid compatibility

**Cost:** Larger area equals higher cost

---

## Summary

| Method | Use When | Known | Find |
|--------|----------|-------|------|
| LMTD | Designing new HX | All temperatures, flow rates | Area required |
| NTU | Rating existing HX | Inlet temps, area, flow rates | Outlet temps, performance |

**Key Equations:**

LMTD Method:
```
Q = U × A × LMTD
LMTD = (ΔT₁ - ΔT₂) / ln(ΔT₁/ΔT₂)
```

NTU Method:
```
NTU = UA / C_min
ε = Q_actual / Q_max
Q_max = C_min × (T_hot_in - T_cold_in)
```

---

## Further Reading

**Textbooks:**
- Bergman, Lavine, Incropera, DeWitt - Fundamentals of Heat and Mass Transfer (8th Edition)
- Holman, J.P. - Heat Transfer (10th Edition)
- Kays, W.M. and London, A.L. - Compact Heat Exchangers (3rd Edition)

**Standards:**
- ASHRAE Handbook - HVAC Systems and Equipment
- TEMA Standards (Tubular Exchanger Manufacturers Association)
