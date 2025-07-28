# Excel-First Implementation Plan: Day 1-2 Sprint
## From Aggregated Data to Working Forecast in Excel

**Target:** Single segment forecast in Excel within 48 hours  
**Approach:** Excel model first, Python automation second

---

## Critical Data Format Decision

### Recommended Format: Keep Dollar Amounts (Not Percentages)

**Why Dollars Over Percentages:**
1. **Reversibility**: Can always calculate % from $, but not vice versa without loan count
2. **Validation**: Easier to spot data errors in dollar amounts
3. **Flexibility**: Can aggregate segments later if needed
4. **Stakeholder Comfort**: CFO/CCO think in dollars, not just rates

**You'll Calculate Rates On-Demand:**
```
Payment Rate = Payment $ / Beginning Balance $
Charge-off Rate = Charge-off $ / Beginning Balance $
```

---

## Optimal Input Data Format

### Single-Segment Paste Format (One Segment = One Table)

```
| Vintage | Month_Age | Beginning_Balance | Payment_Amt | Chargeoff_Amt | Ending_Balance | Loan_Count | Is_Actual |
|---------|-----------|-------------------|-------------|---------------|----------------|------------|-----------|
| 2023-01 | 1         | 1,000,000        | 20,000      | 5,000         | 975,000        | 100        | 1         |
| 2023-01 | 2         | 975,000          | 19,500      | 4,875         | 950,625        | 100        | 1         |
| 2023-01 | 3         | 950,625          | 19,012      | 4,753         | 926,860        | 100        | 1         |
| ...     | ...       | ...              | ...         | ...           | ...            | ...        | ...       |
| 2023-01 | 24        | 750,000          | 0           | 0             | 750,000        | 100        | 0         |
```

### Critical Fields Explained

**Required Fields:**
- **Vintage**: Year-Month of origination (for grouping/sorting)
- **Month_Age**: Months since origination (1, 2, 3...)
- **Beginning_Balance**: Starting principal for the period
- **Payment_Amt**: Total payments in the period
- **Chargeoff_Amt**: Total charge-offs in the period
- **Is_Actual**: 1 = Historical data, 0 = Forecast/Missing

**Calculated Field:**
- **Ending_Balance**: Beginning - Payments - Chargeoffs

**Nice to Have:**
- **Loan_Count**: For per-loan analytics (but not critical Day 1)

---

## Handling Partially Mature Cohorts

### The Triangle Problem
```
Vintage   Age: 1   2   3   4   5   6   ...  24
2023-01      ✓   ✓   ✓   ✓   ✓   ✓   ...  ✓
2023-02      ✓   ✓   ✓   ✓   ✓   ✓   ...  ✓
2023-03      ✓   ✓   ✓   ✓   ✓   ✓   ...  ?
...
2024-12      ✓   ✓   ?   ?   ?   ?   ...  ?
2025-01      ✓   ?   ?   ?   ?   ?   ...  ?
```

### Solution: Weighted Average Approach

**Step 1: Calculate Historical Rates by Age**
```
For each Month_Age where Is_Actual = 1:
  Payment_Rate[Age] = AVG(Payment_Amt / Beginning_Balance)
  Chargeoff_Rate[Age] = AVG(Chargeoff_Amt / Beginning_Balance)
```

**Step 2: Use Recent Cohorts for Early Months**
- Months 1-6: Average of last 12 cohorts
- Months 7-12: Average of last 6 cohorts  
- Months 13-24: Average of last 3 cohorts
- Months 25+: Use mature cohort average

---

## Excel Model Layout

### Sheet 1: "Raw_Data"
- Paste your segment data here
- One contiguous table
- No formulas, just data

### Sheet 2: "Rate_Analysis"
```
| Month_Age | Obs_Count | Avg_Pay_Rate | Avg_CO_Rate | StdDev_Pay | StdDev_CO |
|-----------|-----------|--------------|-------------|------------|-----------|
| 1         | 24        | 2.00%        | 0.50%       | 0.10%      | 0.05%     |
| 2         | 24        | 2.00%        | 0.49%       | 0.09%      | 0.04%     |
| 3         | 23        | 1.95%        | 0.48%       | 0.11%      | 0.05%     |
```

### Sheet 3: "Forecast_Rates"
```
| Month_Age | Payment_Rate | CO_Rate | Source        |
|-----------|--------------|---------|---------------|
| 1         | 2.00%        | 0.50%   | Historical    |
| 2         | 2.00%        | 0.49%   | Historical    |
| ...       | ...          | ...     | ...           |
| 25        | 1.50%        | 0.30%   | Projected     |
```

### Sheet 4: "Forecast_Output"
```
| Vintage | Month_Age | Beginning_Bal | Payment_Amt | CO_Amt | Ending_Bal | Payment_Rate | CO_Rate |
|---------|-----------|---------------|-------------|---------|------------|--------------|---------|
| 2025-01 | 1         | 1,000,000     | 20,000      | 5,000   | 975,000    | 2.00%        | 0.50%   |
| 2025-01 | 2         | 975,000       | 19,500      | 4,778   | 950,722    | 2.00%        | 0.49%   |
```

---

## Day 1: Morning (4 hours)

### Hour 1-2: Data Setup
1. Create Excel file with 4 sheets
2. Paste segment data into Raw_Data
3. Add data validation checks:
   - Beginning_Balance > 0
   - Ending_Balance = Beginning - Payments - CO
   - Is_Actual in (0,1)

### Hour 3-4: Historical Rate Calculation
1. Build Rate_Analysis sheet:
   ```excel
   =AVERAGEIFS(Raw_Data!D:D/Raw_Data!C:C, Raw_Data!B:B, A2, Raw_Data!H:H, 1)
   ```
2. Calculate observation counts
3. Add standard deviation for volatility check

## Day 1: Afternoon (4 hours)

### Hour 5-6: Forecast Rate Development
1. Create age-based forecasting rules
2. Smooth transitions between actual and forecast
3. Apply caps based on historical min/max

### Hour 7-8: Single Cohort Forecast
1. Pick most recent vintage
2. Apply rates to generate 24-month forecast
3. Create summary charts:
   - Balance runoff curve
   - Cumulative payment %
   - Cumulative charge-off %

---

## Day 2: Polish and Validate

### Morning: Lifetime Expectation Integration
1. Add input cell for lifetime CO% (e.g., 20%)
2. Create monthly target curve:
   ```
   Month 18 Target = 20% * (18/144)^1.5
   ```
3. Show actual vs. target variance

### Afternoon: Make It Production-Ready
1. Add control panel:
   - Segment selector
   - Forecast start date
   - Rate override options
2. Create one-click forecast update
3. Format for PowerBI consumption

---

## Python Translation (Week 2)

### Keep It Simple
```python
import pandas as pd

# Read data
df = pd.read_excel('segment_data.xlsx')

# Calculate historical rates
rates = df[df['Is_Actual']==1].groupby('Month_Age').agg({
    'Payment_Amt': lambda x: (x / df.loc[x.index, 'Beginning_Balance']).mean(),
    'Chargeoff_Amt': lambda x: (x / df.loc[x.index, 'Beginning_Balance']).mean()
})

# Apply to forecast
# ... (20 lines of code max)
```

---

## Critical Success Factors

### What MUST Work Day 1
✓ Historical rates calculated correctly  
✓ Single vintage forecasted to month 24  
✓ Output matches manual "smell test"  
✓ Charts that CCO can understand

### What Can Wait
- Multiple segment handling  
- Sophisticated blending  
- Confidence intervals  
- Automated data refresh

### Red Flags to Avoid
❌ Rates > 100% or < 0%  
❌ Balances going negative  
❌ Forecast curves with sharp jumps  
❌ Overly complex formulas

**Remember:** You're building a working prototype, not a perfect system. Excel first, Python second, perfection never.