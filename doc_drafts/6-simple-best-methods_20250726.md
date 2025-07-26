# Alternative Simple Methods for Phase 1 Survival Credit Modeling

## Executive Summary

This document provides detailed implementation guidance for three simple, explainable approaches to Phase 1 survival credit modeling that maintain transparency while meeting PRD requirements.

## Top 3 Recommendations

1. **Moving Average Decay Curves** - Simplest possible approach
2. **Vintage Cohort Curves** - Natural segmentation for different origination periods  
3. **Quantile-Based Approach** - Adds uncertainty quantification with scenarios

---

## 1. MOVING AVERAGE DECAY CURVES - Detailed Implementation

### Mathematical Foundation
```
Payment_Rate(t) = MA[n](Payments(t) / Balance(t))
Chargeoff_Rate(t) = MA[n](Chargeoffs(t) / Balance(t))

Where MA[n] = n-period moving average
```

### Step-by-Step Implementation

**Step 1: Data Aggregation**
```python
# Aggregate by loan age across all segments
for month in range(max_loan_age):
    total_balance[month] = sum(all balances at month)
    total_payments[month] = sum(all payments at month)
    total_chargeoffs[month] = sum(all chargeoffs at month)
```

**Step 2: Raw Rate Calculation**
```python
raw_payment_rate[month] = total_payments[month] / total_balance[month]
raw_chargeoff_rate[month] = total_chargeoffs[month] / total_balance[month]
```

**Step 3: Moving Average Smoothing**
```python
# 3-month centered moving average
for month in range(1, max_month-1):
    smoothed_payment_rate[month] = mean(
        raw_payment_rate[month-1:month+2]
    )
```

**Step 4: Extrapolation Beyond Training Data**
- **Linear Decay**: Fit line to last 6 months, project forward
- **Exponential Decay**: Rate(t) = Rate(last) * exp(-decay_factor * (t - last))
- **Constant**: Use average of last 3 months

### Practical Example
```
Month | Raw Payment Rate | 3-Month MA | Forecast Type
------|-----------------|------------|---------------
  10  |     8.5%        |    8.3%    | Historical
  11  |     8.1%        |    8.4%    | Historical  
  12  |     8.6%        |    8.3%    | Historical
  13  |     ---         |    8.2%    | Linear decay
  14  |     ---         |    8.0%    | Linear decay
```

### Advantages for Credit Portfolio
- **Volatility Reduction**: Smooths month-to-month payment spikes
- **Seasonal Handling**: 3-month window captures quarterly patterns
- **Transparent Calculations**: "Average of last 3 months" easily understood
- **Quick Implementation**: Can be coded in <100 lines

### Parameter Selection Guide
- **Window Size**: 3 months (quarterly), 6 months (semi-annual), 12 months (annual)
- **Weighting**: Equal weights or exponentially declining (recent months weighted more)
- **Edge Handling**: Use available data at start/end of series

---

## 2. VINTAGE COHORT CURVES - Detailed Implementation

### Mathematical Foundation
```
Payment_Rate_Vintage[v,t] = Payments[v,t] / Balance[v,t]
Forecast_Rate[t] = Σ(Weight[v] × Payment_Rate_Vintage[v,t])

Where v = vintage (origination period)
      t = loan age in months
```

### Step-by-Step Implementation

**Step 1: Vintage Segmentation**
```python
# Group loans by origination quarter
vintages = {
    '2023Q1': loans originated Jan-Mar 2023,
    '2023Q2': loans originated Apr-Jun 2023,
    ...
}
```

**Step 2: Calculate Vintage-Specific Curves**
```python
for vintage in vintages:
    for month in loan_ages:
        vintage_curves[vintage][month] = {
            'payment_rate': payments[vintage,month] / balance[vintage,month],
            'chargeoff_rate': chargeoffs[vintage,month] / balance[vintage,month]
        }
```

**Step 3: Weighting Schemes**
```python
# Option A: Recency weighting
weights = exponential_decay(vintage_age)

# Option B: Volume weighting  
weights = origination_volume[vintage] / total_volume

# Option C: Performance weighting
weights = 1 / variance(vintage_performance)
```

**Step 4: Blended Forecast**
```python
for month in forecast_months:
    forecast_payment_rate[month] = 0
    for vintage in relevant_vintages:
        forecast_payment_rate[month] += (
            weights[vintage] * vintage_curves[vintage][month]
        )
```

### Practical Example
```
Vintage | Weight | Month 12 Payment Rate | Contribution
--------|--------|---------------------|-------------
2023Q1  |  20%   |       7.5%          |    1.50%
2023Q2  |  30%   |       8.2%          |    2.46%
2023Q3  |  35%   |       8.0%          |    2.80%
2023Q4  |  15%   |       7.8%          |    1.17%
--------|--------|---------------------|-------------
Blended |  100%  |                     |    7.93%
```

### Handling Incomplete Vintages
- **Truncated Data**: Use available months, adjust weights
- **Curve Extension**: Apply average curve shape from complete vintages
- **Maturity Adjustment**: Scale based on observed vs expected maturity

### Advantages for Credit Portfolio
- **Macro Sensitivity**: Captures economic conditions at origination
- **Underwriting Changes**: Reflects policy changes over time
- **Natural Segmentation**: Aligns with how credit teams think
- **Backtesting Friendly**: Can validate vintage-by-vintage

---

## 3. QUANTILE-BASED APPROACH - Detailed Implementation

### Mathematical Foundation
```
Payment_Rate_Quantiles[t] = {
    P10: 10th percentile of payment rates at month t
    P25: 25th percentile (optimistic scenario)
    P50: 50th percentile (base case)
    P75: 75th percentile (conservative scenario)
    P90: 90th percentile (stress scenario)
}
```

### Step-by-Step Implementation

**Step 1: Calculate Historical Distributions**
```python
# For each loan age, collect all historical observations
for month in loan_ages:
    observations[month] = []
    for segment in all_segments:
        if data_exists(segment, month):
            rate = payments[segment,month] / balance[segment,month]
            observations[month].append(rate)
```

**Step 2: Compute Quantiles**
```python
for month in loan_ages:
    quantiles[month] = {
        'P10': np.percentile(observations[month], 10),
        'P25': np.percentile(observations[month], 25),
        'P50': np.percentile(observations[month], 50),
        'P75': np.percentile(observations[month], 75),
        'P90': np.percentile(observations[month], 90)
    }
```

**Step 3: Scenario Generation**
```python
scenarios = {
    'optimistic': quantiles['P25'],  # Good performance
    'base_case': quantiles['P50'],   # Median expectation
    'conservative': quantiles['P75'], # Poor performance
    'stress': quantiles['P90']       # Severe stress
}
```

**Step 4: Forecast with Uncertainty Bands**
```python
for month in forecast_months:
    forecast[month] = {
        'expected': quantiles[month]['P50'],
        'range_80': [quantiles[month]['P10'], quantiles[month]['P90']],
        'range_50': [quantiles[month]['P25'], quantiles[month]['P75']]
    }
```

### Practical Example
```
Month | P10  | P25  | P50  | P75  | P90  | Interpretation
------|------|------|------|------|------|----------------
  6   | 5.2% | 6.8% | 8.1% | 9.3% |10.5% | Wide dispersion
  12  | 6.5% | 7.2% | 7.8% | 8.4% | 9.1% | Converging
  24  | 4.1% | 4.5% | 5.0% | 5.5% | 6.0% | Mature/stable
```

### Visualization Approach
```
Payment Rate
12% |                    
10% |    ·····P90········
 8% | ···P75·············
 6% | ---P50(BASE)-------  
 4% | ···P25·············
 2% |    ·····P10········
 0% |____________________
    0   6   12  18  24  30
         Loan Age (Months)
```

### Advanced Features

**Conditional Quantiles**
```python
# Quantiles by segment characteristics
if risk_score > 700:
    use_quantiles = high_quality_quantiles
else:
    use_quantiles = subprime_quantiles
```

**Dynamic Scenario Selection**
```python
# Adjust scenario based on current performance
if actual_performance < P25:
    shift_to_conservative_scenario()
```

### Advantages for Credit Portfolio
- **Natural Risk Ranges**: Shows performance distribution
- **Scenario Planning**: Built-in stress testing
- **No Distribution Assumptions**: Works with any data shape
- **Regulatory Friendly**: Demonstrates consideration of adverse scenarios
- **Communication Tool**: "We expect 8% payment rate, but it could range from 6% to 10%"

---

## IMPLEMENTATION COMPARISON

| Aspect | Moving Average | Vintage Cohort | Quantile-Based |
|--------|---------------|----------------|----------------|
| **Complexity** | Low | Medium | Low-Medium |
| **Data Needs** | Minimal | Moderate | Moderate |
| **Interpretability** | Excellent | Excellent | Very Good |
| **Uncertainty Handling** | None | Implicit | Explicit |
| **Computational Load** | Minimal | Low | Low |
| **Extrapolation** | Simple | Vintage-based | Quantile-based |
| **Best Use Case** | Stable portfolios | Changing origination | Risk assessment |

## COMBINED RECOMMENDATION

For maximum robustness, implement **Quantile-Based as primary** with:
- Base forecast using P50 (median)
- Scenario analysis using P25/P75
- Stress testing using P90

Then use **Moving Average** for smoothing the quantile curves if needed, creating a hybrid approach that's both simple and comprehensive.

## Alternative Approaches Summary

### Complete List of Phase 1 Alternatives

1. **Moving Average Decay Curves** - Simplest possible approach
2. **Vintage Cohort Curves** - Natural segmentation 
3. **Simple Regression Interpolation** - Mathematical foundation
4. **Empirical CDF Approach** - Lifecycle modeling
5. **Segment-Weighted Blending** - Handles heterogeneity
6. **Decay Curve Fitting** - Parsimonious mathematical models
7. **Quantile-Based Approach** - Built-in uncertainty
8. **Ensemble Methods** - Combines multiple simple approaches
9. **Conditional Switching** - Different methods for different loan ages

Each maintains Phase 1's core principles of transparency and business-friendly implementation while offering different foundations based on specific data characteristics and business requirements.