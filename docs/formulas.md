# Heat Exchanger Formulas - Quick Reference

---

## Basic Heat Transfer

### Heat Transfer Rate

```
Q = m × Cp × ΔT
```

**Hot fluid:**
```
Q_hot = m_hot × Cp_hot × (T_hot_in - T_hot_out)
```

**Cold fluid:**
```
Q_cold = m_cold × Cp_cold × (T_cold_out - T_cold_in)
```

**Units:**
- Q: W or kW (1 kW = 1000 W)
- m: kg/s
- Cp: J/(kg·K)
- ΔT: K or °C

---

## LMTD Method

### Main Equation

```
Q = U × A × LMTD × F
```

Where F = correction factor (usually 1.0 for pure counter or parallel flow)

### LMTD Calculation

**Counter Flow:**
```
ΔT₁ = T_hot_in - T_cold_out
ΔT₂ = T_hot_out - T_cold_in

LMTD = (ΔT₁ - ΔT₂) / ln(ΔT₁/ΔT₂)
```

**Parallel Flow:**
```
ΔT₁ = T_hot_in - T_cold_in
ΔT₂ = T_hot_out - T_cold_out

LMTD = (ΔT₁ - ΔT₂) / ln(ΔT₁/ΔT₂)
```

**Special case:** If ΔT₁ approximately equals ΔT₂, then LMTD approximately equals ΔT₁

### Required Area

```
A = Q / (U × LMTD)
```

---

## NTU Method

### Number of Transfer Units

```
NTU = (U × A) / C_min
```

### Heat Capacity Rates

```
C_hot = m_hot × Cp_hot
C_cold = m_cold × Cp_cold

C_min = min(C_hot, C_cold)
C_max = max(C_hot, C_cold)

C_ratio = C_min / C_max
```

**Units:** C in W/K

### Maximum Heat Transfer

```
Q_max = C_min × (T_hot_in - T_cold_in)
```

### Effectiveness

```
ε = Q_actual / Q_max
```

### Effectiveness-NTU Relations

**Counter Flow:**

If C_ratio less than 1:
```
ε = [1 - exp(-NTU(1 - C_ratio))] / [1 - C_ratio × exp(-NTU(1 - C_ratio))]
```

If C_ratio equals 1:
```
ε = NTU / (1 + NTU)
```

**Parallel Flow:**
```
ε = [1 - exp(-NTU(1 + C_ratio))] / (1 + C_ratio)
```

### Outlet Temperatures

```
T_hot_out = T_hot_in - Q / C_hot

T_cold_out = T_cold_in + Q / C_cold
```

---

## Overall Heat Transfer Coefficient

### Thermal Resistance Network

```
1/U = 1/h_hot + R_wall + 1/h_cold + R_fouling
```

For a tube wall:
```
R_wall = t_wall / k_wall
```

### Film Coefficients

**Laminar flow (Re less than 2300):**
```
Nu = 3.66  (constant wall temperature)
```

**Turbulent flow (Re greater than 4000):**

Dittus-Boelter equation:
```
Nu = 0.023 × Re^0.8 × Pr^n
```
where n = 0.4 for heating, 0.3 for cooling

**Nusselt number:**
```
Nu = h × D / k
```

Therefore:
```
h = (Nu × k) / D
```

---

## Dimensionless Numbers

### Reynolds Number

```
Re = (ρ × V × D) / μ = (m × D) / (A × μ)
```

**Flow regimes:**
- Re less than 2,300: Laminar
- 2,300 less than Re less than 4,000: Transitional
- Re greater than 4,000: Turbulent

### Prandtl Number

```
Pr = (Cp × μ) / k = ν / α
```

**Typical values:**
- Liquid metals: 0.001 - 0.03
- Gases: 0.7 - 1.0
- Water: 1 - 10
- Oils: 50 - 10,000

### Nusselt Number

```
Nu = (h × L) / k
```

Represents ratio of convective to conductive heat transfer

---

## Unit Conversions

### Temperature

```
T(K) = T(°C) + 273.15
T(°F) = T(°C) × 9/5 + 32
T(°C) = [T(°F) - 32] × 5/9
```

### Heat Transfer Rate

```
1 kW = 3,412.14 BTU/hr
1 BTU/hr = 0.293071 W
1 ton of refrigeration = 3.517 kW = 12,000 BTU/hr
```

### Area

```
1 m² = 10.7639 ft²
1 ft² = 0.092903 m²
```

### Mass Flow Rate

```
1 kg/s = 7,936.64 lb/hr
1 lb/hr = 0.000126 kg/s
```

### Overall Heat Transfer Coefficient

```
1 W/(m²·K) = 0.1761 BTU/(hr·ft²·°F)
1 BTU/(hr·ft²·°F) = 5.678 W/(m²·K)
```

### Specific Heat

```
1 kJ/(kg·K) = 0.238846 BTU/(lb·°F)
1 BTU/(lb·°F) = 4.1868 kJ/(kg·K)
```

---

## Fluid Properties (at 25°C, 1 atm)

### Water

```
ρ = 997 kg/m³
Cp = 4,180 J/(kg·K)
k = 0.607 W/(m·K)
μ = 0.00089 Pa·s
Pr = 6.14
```

### Air

```
ρ = 1.184 kg/m³
Cp = 1,005 J/(kg·K)
k = 0.0263 W/(m·K)
μ = 0.0000184 Pa·s
Pr = 0.703
```

### Engine Oil

```
ρ = 888 kg/m³
Cp = 2,000 J/(kg·K)
k = 0.145 W/(m·K)
μ = 0.086 Pa·s
Pr = 1,190
```

---

## Typical Design Values

### Overall Heat Transfer Coefficients

| Fluid Combination | Type | U (W/m²·K) |
|-------------------|------|------------|
| Water - Water | Shell-and-Tube | 800 - 1,500 |
| Water - Water | Plate | 3,000 - 7,000 |
| Water - Oil | Shell-and-Tube | 100 - 400 |
| Water - Air | Finned Tube | 25 - 100 |
| Air - Air | Plate | 10 - 40 |
| Steam - Water | Shell-and-Tube | 1,500 - 4,000 |
| Refrigerant - Water | Evaporator | 400 - 1,000 |
| Refrigerant - Air | Condenser | 20 - 100 |

### Temperature Approaches

- Excellent: 2 - 5°C
- Good: 5 - 10°C
- Acceptable: 10 - 20°C
- Poor: greater than 20°C

### Effectiveness Ranges

- Counter Flow: 60 - 90%
- Parallel Flow: 40 - 70%
- Cross Flow: 50 - 80%

---

## Common Pitfalls

### Energy Balance Error

Always check:
```
Error = |Q_hot - Q_cold| / Q_hot × 100%
```

Should be less than 1-2%

If error is large:
- Check property evaluation temperatures
- Verify mass flow rate units
- Confirm specific heat values

### Invalid Temperatures

Must satisfy:
```
T_hot_out > T_cold_in  (2nd Law)
T_cold_out < T_hot_in  (2nd Law)
T_hot_in > T_hot_out   (hot fluid cools)
T_cold_out > T_cold_in (cold fluid heats)
```

**Parallel Flow additional constraint:**
```
T_hot_out > T_cold_out (always)
```

---

## Quick Calculation Steps

### LMTD Method (Design)

1. Calculate Q from hot fluid: `Q = m_hot × Cp_hot × (T_hot_in - T_hot_out)`
2. Verify with cold fluid: `Q = m_cold × Cp_cold × (T_cold_out - T_cold_in)`
3. Calculate ΔT₁ and ΔT₂ based on flow type
4. Calculate LMTD: `LMTD = (ΔT₁ - ΔT₂) / ln(ΔT₁/ΔT₂)`
5. Calculate area: `A = Q / (U × LMTD)`

### NTU Method (Rating)

1. Calculate C_hot and C_cold
2. Find C_min, C_max, C_ratio
3. Calculate NTU: `NTU = UA / C_min`
4. Calculate effectiveness from correlation
5. Calculate Q_max: `Q_max = C_min × (T_hot_in - T_cold_in)`
6. Calculate Q: `Q = ε × Q_max`
7. Calculate outlet temperatures from Q

---

## Example Calculation

**Given:** Counter flow, Water-Water
- Hot: 90°C → 50°C, 2 kg/s
- Cold: 25°C → 45°C, 3 kg/s
- U = 500 W/m²·K

**Find:** Area

**Solution:**

```
Q_hot = 2 × 4180 × (90-50) = 334,400 W

ΔT₁ = 90 - 45 = 45°C
ΔT₂ = 50 - 25 = 25°C

LMTD = (45-25)/ln(45/25) = 20/0.588 = 34.0°C

A = 334,400 / (500 × 34.0) = 19.7 m²
```

---

## References

**Textbooks:**
- Bergman et al., Fundamentals of Heat and Mass Transfer, 8th Ed.
- Holman, Heat Transfer, 10th Ed.
- Kays & London, Compact Heat Exchangers, 3rd Ed.

**Standards:**
- ASHRAE Handbook - HVAC Systems and Equipment
- TEMA Standards
