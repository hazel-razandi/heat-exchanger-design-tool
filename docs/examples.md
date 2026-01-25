# Worked Examples

This document contains detailed worked examples for common heat exchanger design scenarios.

---

## Example 1: Sizing a Cooling Coil (LMTD Method)

### Problem Statement

Design a cooling coil for an air conditioning system. Hot air needs to be cooled using chilled water in a counter-flow arrangement.

**Given:**
- Hot fluid: Air at 30°C inlet, cooled to 15°C
- Cold fluid: Chilled water at 7°C inlet, exits at 12°C
- Air flow rate: 1.5 kg/s
- Water flow rate: 2.0 kg/s
- Overall heat transfer coefficient: U = 50 W/m²·K

**Find:** Required heat exchanger area

### Solution

**Step 1: Get fluid properties**

Air at average temperature (22.5°C): Cp_air = 1,005 J/(kg·K)

Water at average temperature (9.5°C): Cp_water = 4,190 J/(kg·K)

**Step 2: Calculate heat transfer rate**

From air (hot fluid):
```
Q_air = 1.5 × 1,005 × (30 - 15) = 22,612.5 W = 22.6 kW
```

From water (cold fluid):
```
Q_water = 2.0 × 4,190 × (12 - 7) = 41,900 W = 41.9 kW
```

Energy balance check shows large error, so recalculate water outlet temperature:
```
T_water_out = 7 + 22,612.5 / (2.0 × 4,190) = 9.7°C
```

**Step 3: Calculate LMTD (Counter flow)**

```
ΔT₁ = 30 - 9.7 = 20.3°C
ΔT₂ = 15 - 7 = 8.0°C

LMTD = (20.3 - 8.0) / ln(20.3/8.0) = 12.3 / 0.932 = 13.2°C
```

**Step 4: Calculate required area**

```
A = Q / (U × LMTD) = 22,612.5 / (50 × 13.2) = 34.3 m²
```

### Answer

**Required heat exchanger area: 34.3 m²**

This is a relatively large area, typical for air-to-water heat exchangers due to the low U-value.

---

## Example 2: Analyzing an Oil Cooler (NTU Method)

### Problem Statement

An existing oil cooler uses water to cool engine oil. Determine the outlet temperatures and cooling capacity.

**Given:**
- Hot fluid: Engine oil at 95°C inlet, 0.5 kg/s
- Cold fluid: Cooling water at 25°C inlet, 1.2 kg/s
- Heat exchanger: Counter flow, A = 2.5 m²
- Overall heat transfer coefficient: U = 250 W/m²·K

**Find:** Oil and water outlet temperatures, heat transfer rate

### Solution

**Step 1: Get fluid properties**

Engine oil at estimated average (75°C): Cp_oil = 2,100 J/(kg·K)

Water at estimated average (30°C): Cp_water = 4,180 J/(kg·K)

**Step 2: Calculate heat capacity rates**

```
C_hot = 0.5 × 2,100 = 1,050 W/K
C_cold = 1.2 × 4,180 = 5,016 W/K

C_min = 1,050 W/K (oil side)
C_max = 5,016 W/K (water side)

C_ratio = 1,050 / 5,016 = 0.209
```

**Step 3: Calculate NTU**

```
NTU = (250 × 2.5) / 1,050 = 0.595
```

**Step 4: Calculate effectiveness (Counter flow)**

For C_ratio less than 1:
```
ε = [1 - exp(-0.595×0.791)] / [1 - 0.209 × exp(-0.595×0.791)]
ε = 0.432 or 43.2%
```

**Step 5: Calculate heat transfer**

```
Q_max = 1,050 × (95 - 25) = 73,500 W = 73.5 kW
Q = 0.432 × 73.5 = 31.8 kW
```

**Step 6: Calculate outlet temperatures**

Oil outlet:
```
T_oil_out = 95 - 31,800 / 1,050 = 64.7°C
```

Water outlet:
```
T_water_out = 25 + 31,800 / 5,016 = 31.3°C
```

### Answer

- Oil outlet temperature: 64.7°C
- Water outlet temperature: 31.3°C
- Heat transfer rate: 31.8 kW
- Effectiveness: 43.2%

### Verification

Energy balance:
```
Q_oil = 0.5 × 2,100 × (95 - 64.7) = 31,815 W ✓
Q_water = 1.2 × 4,180 × (31.3 - 25) = 31,597 W ✓
Error = 0.7% ✓
```

---

## Example 3: Chiller Evaporator Design

### Problem Statement

Design an evaporator for a chiller system. Chilled water is cooled by evaporating R-134a refrigerant.

**Given:**
- Hot fluid: Water at 12°C inlet, to be cooled to 7°C
- Cold fluid: R-134a evaporating at constant 2°C
- Water flow rate: 10 kg/s
- U = 800 W/m²·K (typical for refrigerant evaporators)
- Counter flow arrangement

**Find:** Required evaporator area

### Solution

**Step 1: Calculate cooling load**

```
Q = 10 × 4,180 × (12 - 7) = 209,000 W = 209 kW
```

Verification: 209 kW ÷ 3.517 kW/ton = 59.4 tons ✓

**Step 2: Special case - Constant refrigerant temperature**

When one fluid changes phase at constant temperature:

```
ΔT₁ = 12 - 2 = 10°C
ΔT₂ = 7 - 2 = 5°C
```

**Step 3: Calculate LMTD**

```
LMTD = (10 - 5) / ln(10/5) = 5 / 0.693 = 7.21°C
```

**Step 4: Calculate area**

```
A = 209,000 / (800 × 7.21) = 36.2 m²
```

### Answer

**Required evaporator area: 36.2 m²**

This is a typical size for a 59-ton chiller evaporator. The relatively high U-value (800 W/m²·K) is due to boiling refrigerant on one side and water on the other.

---

## Example 4: Heat Recovery Unit Comparison

### Problem Statement

Compare counter flow vs. parallel flow arrangements for a heat recovery unit.

**Given:**
- Hot fluid: Exhaust air at 60°C, 3 kg/s
- Cold fluid: Fresh air at 20°C, 3 kg/s
- Heat exchanger: 15 m² area
- U = 30 W/m²·K

**Find:** Compare performance of both arrangements

### Solution for Counter Flow

**Step 1: Calculate C values**

```
C_hot = C_cold = 3 × 1,005 = 3,015 W/K
C_ratio = 1.0 (balanced flows)
C_min = 3,015 W/K
```

**Step 2: Calculate NTU**

```
NTU = (30 × 15) / 3,015 = 0.149
```

**Step 3: Effectiveness (Counter flow, C_ratio = 1)**

```
ε = NTU / (1 + NTU) = 0.149 / 1.149 = 0.130 or 13.0%
```

**Step 4: Heat transfer and temperatures**

```
Q_max = 3,015 × (60 - 20) = 120,600 W = 120.6 kW
Q = 0.130 × 120.6 = 15.7 kW

T_hot_out = 60 - 15,700/3,015 = 54.8°C
T_cold_out = 20 + 15,700/3,015 = 25.2°C
```

### Solution for Parallel Flow

**Steps 1-2: Same as counter flow**

**Step 3: Effectiveness (Parallel flow)**

```
ε = [1 - exp(-0.149×2)] / 2 = 0.129 or 12.9%
```

**Step 4: Heat transfer and temperatures**

```
Q = 0.129 × 120.6 = 15.6 kW

T_hot_out = 54.8°C
T_cold_out = 25.2°C
```

### Comparison Table

| Parameter | Counter Flow | Parallel Flow | Difference |
|-----------|--------------|---------------|------------|
| Effectiveness | 13.0% | 12.9% | 0.1% |
| Heat Recovery | 15.7 kW | 15.6 kW | 0.1 kW |
| Hot Outlet | 54.8°C | 54.8°C | ~0°C |
| Cold Outlet | 25.2°C | 25.2°C | ~0°C |

### Discussion

At this low NTU (0.149), there's virtually no difference between counter and parallel flow. The difference becomes significant at higher NTU values (NTU greater than 1).

With larger area (45 m²):

**Counter flow (NTU = 0.448):**
- Effectiveness = 30.9%
- Q = 37.3 kW

**Parallel flow (NTU = 0.448):**
- Effectiveness = 28.0%
- Q = 33.8 kW

**Now the difference is significant: 3.5 kW or 10% more heat recovery with counter flow!**

---

## Example 5: Radiator Performance Check

### Problem Statement

Verify if an automotive radiator can handle the required cooling.

**Given:**
- Hot fluid: Engine coolant (50% glycol) at 95°C inlet
- Cold fluid: Air at 30°C ambient
- Coolant flow: 0.8 kg/s
- Air flow: 2.5 kg/s (from fan and vehicle motion)
- Radiator: Cross-flow, 1.2 m² frontal area
- U = 60 W/m²·K
- Required cooling: 50 kW

**Find:** Can this radiator provide 50 kW cooling? What's the coolant outlet temperature?

### Solution

**Step 1: Properties**

Ethylene glycol 50%: Cp_glycol = 3,300 J/(kg·K)

Air: Cp_air = 1,005 J/(kg·K)

**Step 2: Heat capacity rates**

```
C_hot = 0.8 × 3,300 = 2,640 W/K
C_cold = 2.5 × 1,005 = 2,512.5 W/K

C_min = 2,512.5 W/K (air side)
C_max = 2,640 W/K
C_ratio = 0.952
```

**Step 3: NTU**

```
NTU = (60 × 1.2) / 2,512.5 = 0.0287
```

**Step 4: Effectiveness**

```
ε ≈ 0.0281 or 2.81%
```

**Step 5: Actual cooling capacity**

```
Q_max = 2,512.5 × (95 - 30) = 163,312 W = 163.3 kW
Q = 0.0281 × 163.3 = 4.6 kW
```

### Answer

**The radiator can only provide 4.6 kW, far below the required 50 kW!**

### Problem Analysis

The NTU is too small (0.0287). To achieve 50 kW:

Required effectiveness: 50 / 163.3 = 30.6%

Required NTU: approximately 0.42

Required UA: 0.42 × 2,512.5 = 1,055 W/K

**Options to fix:**
1. Increase area to 17.6 m² (impractical!)
2. Increase U-value by adding fins, improving airflow
3. Increase air flow rate with bigger fan
4. Reduce coolant temperature (improve engine design)

This example shows why automotive radiators need large surface areas and high air flow rates.

---

## Key Takeaways from Examples

1. Always check energy balance - errors indicate problems with inputs

2. Counter flow is superior - but only at moderate to high NTU values

3. Low U-values require large areas - especially for gas-liquid applications

4. Phase change simplifies analysis - constant temperature on one side

5. Balanced flows (C_ratio approximately 1) are efficient - especially in counter flow

6. Real systems have constraints - size, cost, pressure drop all matter

---

## Practice Problems

Try solving these on your own:

**Problem 1:** A shell-and-tube heat exchanger cools 5 kg/s of oil from 80°C to 40°C using water entering at 25°C. If U = 300 W/m²·K and water flow is 8 kg/s, what area is needed?

**Problem 2:** An existing 20 m² plate heat exchanger with U = 4,000 W/m²·K is used for water-water heat transfer. Hot water enters at 70°C at 3 kg/s, cold water enters at 20°C at 4 kg/s. Find outlet temperatures.

**Problem 3:** Compare the effectiveness of parallel flow vs counter flow when NTU = 2.0 and C_ratio = 0.5.

**Answers:**
1. Approximately 15.5 m²
2. Hot out: 46.3°C, Cold out: 37.8°C
3. Counter: 75.8%, Parallel: 63.2%
