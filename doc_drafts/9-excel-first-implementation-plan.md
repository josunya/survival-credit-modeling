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

**Critical Logic:**
- For historical data: Ending_Balance[t] should equal Beginning_Balance[t+1]
- For forecasts: Beginning_Balance[t+1] = Ending_Balance[t]
- For new vintages: Beginning_Balance[1] = Input parameter (e.g., $1M)

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

**Step 2: Excel Implementation for Weighted Averages**

For Month_Age = X:
```excel
=IF(COUNTIFS($B:$B,X,$H:$H,1)>=12,
    SUMPRODUCT((MOD(ROW($A:$A)-ROW($A$2),24)=X-1)*($H:$H=1)*($D:$D))/
    SUMPRODUCT((MOD(ROW($A:$A)-ROW($A$2),24)=X-1)*($H:$H=1)*($C:$C)),
    AVERAGEIFS($D:$D/$C:$C,$B:$B,X,$H:$H,1))
```

Simpler approach - use helper columns:
- Months 1-6: Average of all available data at that age
- Months 7-12: Average of all available data at that age
- Months 13-24: Average of all available data at that age
- Months 25-144: Use last observed rate or decay to zero

---

## Excel Model Layout

### Sheet 1: "Raw_Data"
- Paste your segment data here
- One contiguous table
- No formulas, just data

### Sheet 2: "Rate_Analysis"
```
| Month_Age | Vintage_Count | Payment_Rate | CO_Rate |
|-----------|---------------|--------------|---------|
| 1         | 24            | 2.00%        | 0.50%   |
| 2         | 24            | 2.00%        | 0.49%   |
| 3         | 23            | 1.95%        | 0.48%   |
```

### Sheet 3: "Forecast_Rates"
```
| Month_Age | Payment_Rate | CO_Rate | Source        | Logic                    |
|-----------|--------------|---------|---------------|---------------------------|
| 1         | 2.00%        | 0.50%   | Historical    | From Rate_Analysis       |
| 2         | 2.00%        | 0.49%   | Historical    | From Rate_Analysis       |
| ...       | ...          | ...     | ...           | ...                      |
| 24        | 1.60%        | 0.40%   | Historical    | From Rate_Analysis       |
| 25        | 1.50%        | 0.35%   | Extended      | Month 24 rate * 0.95     |
| ...       | ...          | ...     | ...           | ...                      |
| 144       | 0.10%        | 0.05%   | Extended      | Decay formula            |
```

**Extension Logic (Months 25-144):**
- Payment_Rate[t] = Payment_Rate[24] * 0.95^((t-24)/12)
- CO_Rate[t] = CO_Rate[24] * 0.90^((t-24)/12)

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
   - Payment_Amt <= Beginning_Balance
   - Chargeoff_Amt <= Beginning_Balance
   - Payment_Amt + Chargeoff_Amt <= Beginning_Balance
   
4. Data quality helper columns:
   - Balance_Check: `=ABS(F2-(C2-D2-E2))<0.01`
   - Rate_Check: `=(D2+E2)/C2<=1`
   - Flag anomalies with conditional formatting

### Hour 3-4: Historical Rate Calculation
1. Build Rate_Analysis sheet with correct formulas:
   
   For Payment_Rate (assuming Month_Age in A2):
   ```excel
   =SUMIFS(Raw_Data!$D:$D, Raw_Data!$B:$B, A2, Raw_Data!$H:$H, 1) / 
    SUMIFS(Raw_Data!$C:$C, Raw_Data!$B:$B, A2, Raw_Data!$H:$H, 1)
   ```
   
   For CO_Rate:
   ```excel
   =SUMIFS(Raw_Data!$E:$E, Raw_Data!$B:$B, A2, Raw_Data!$H:$H, 1) / 
    SUMIFS(Raw_Data!$C:$C, Raw_Data!$B:$B, A2, Raw_Data!$H:$H, 1)
   ```
   
2. Count vintages: `=COUNTIFS(Raw_Data!$B:$B, A2, Raw_Data!$H:$H, 1)`
3. Handle division by zero with IFERROR wrapper

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
1. Add input parameters:
   - Lifetime_CO_Rate: 20% (example)
   - Loan_Term_Months: 144
   - Curve_Shape: 1.2 (adjustable)
   
2. Create monthly target curve:
   ```excel
   Cumulative_CO_Target[t] = Lifetime_CO_Rate * (t / Loan_Term_Months)^Curve_Shape
   Monthly_CO_Target[t] = Cumulative_CO_Target[t] - Cumulative_CO_Target[t-1]
   ```
   
3. Blend forecast rates with lifetime expectations:
   - Weight_Historical = MIN(1, Vintage_Count / 6)
   - Weight_Lifetime = 1 - Weight_Historical
   - Blended_CO_Rate = Historical_Rate * Weight_Historical + Target_Rate * Weight_Lifetime

### Afternoon: Make It Production-Ready
1. Add control panel:
   - Input_Starting_Balance (e.g., $1,000,000)
   - Segment_Name (text field)
   - Forecast_Start_Vintage (e.g., 2025-01)
   - Rate override options (optional)
   
2. Create one-click forecast update:
   - Clear previous forecast
   - Apply rates to new vintage
   - Generate 144-month projection
   
3. Format output table for easy export:
   - Consistent column headers
   - No merged cells
   - Date formatting for vintages

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

### Rate Application Method (Recommendation)

**Use Beginning Balance Method:**
```
Payment_Amt[t] = Beginning_Balance[t] * Payment_Rate[t]
Chargeoff_Amt[t] = Beginning_Balance[t] * CO_Rate[t]
Ending_Balance[t] = Beginning_Balance[t] - Payment_Amt[t] - Chargeoff_Amt[t]
Beginning_Balance[t+1] = Ending_Balance[t]
```

**Why Beginning Balance:**
1. Matches industry standard practice
2. Prevents circular references in Excel
3. Easier to audit and validate
4. Consistent with how rates were calculated historically

**Remember:** You're building a working prototype, not a perfect system. Excel first, Python second, perfection never.