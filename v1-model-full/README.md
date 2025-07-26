# Survival Credit Modeling Tool - Phase 1

A simplified hazard rate-based survival modeling tool for loan performance forecasting. Focuses on payment and chargeoff curves with transparent, explainable methodology suitable for business stakeholders.

## Overview

This tool implements Phase 1 of the comprehensive survival credit modeling approach outlined in the PRD. It provides:

- **Simple empirical hazard rate estimation** from historical loan data
- **Transparent forecasting methodology** using payment and chargeoff curves
- **Ratio-based outputs** for easy scaling across different origination amounts
- **Clear validation framework** with business-friendly metrics

## Key Features

### Data Structure (Simplified)
Required input columns:
- `segment_id`: Segment/vintage identifier
- `month_on_book`: Months since origination (0, 1, 2, ...)
- `payments`: Dollar payments made this month
- `chargeoffs`: Dollar chargeoffs this month  
- `outstanding_balance`: Balance at START of month

### Core Methodology
1. **Training**: Estimate hazard rate curves from historical data
   - `payment_hazard_rate = payments / outstanding_balance`
   - `chargeoff_hazard_rate = chargeoffs / outstanding_balance`

2. **Forecasting**: Apply curves to new segments
   - Use known actuals through current month
   - Apply trained curves for future months
   - Project balance flows: `balance[t+1] = balance[t] - payments[t] - chargeoffs[t]`

3. **Output**: Ratio-based results
   - All amounts expressed as % of origination amount
   - Hazard rate curves (0-100%)
   - Easy conversion to dollars via multiplication

## Quick Start

### Installation
```python
# No external dependencies beyond pandas and numpy
pip install pandas numpy matplotlib  # matplotlib optional for visualization
```

### Basic Usage

```python
from survival_credit_model import SurvivalCreditModel
from example_data_generator import generate_example_datasets

# Generate example data
training_data, test_data = generate_example_datasets()

# Initialize and train model
model = SurvivalCreditModel(smoothing_window=3)
training_results = model.train(training_data)

# Generate forecast
origination_amount = 8_000_000
forecast_output, validation = model.forecast(
    known_actuals=test_data,
    origination_amount=origination_amount,
    max_month=48
)

# View results
print(forecast_output.head())
```

### Complete Test Pipeline
```bash
python test_pipeline.py
```

This will:
- Generate example training and test datasets
- Train the model on historical data
- Generate forecasts for a new segment
- Validate results and save outputs
- Create visualizations (if matplotlib available)

## Files Structure

- **`survival_credit_model.py`** - Main model classes
- **`example_data_generator.py`** - Generate realistic test data
- **`test_pipeline.py`** - Complete testing pipeline
- **`README.md`** - This documentation

## Output Files

After running the test pipeline:
- **`training_data_example.csv`** - Example training data
- **`test_data_example.csv`** - Example test data  
- **`forecast_output_test.csv`** - Forecast results with ratios and hazard rates
- **`hazard_curves_test.csv`** - Trained hazard rate curves
- **`survival_model_results.png`** - Visualization plots

## Model Components

### DataValidator
- Validates input data structure and quality
- Checks business logic consistency (balance flows)
- Flags unreasonable hazard rates or missing data

### HazardRateEstimator  
- Estimates payment and chargeoff hazard rates by month
- Aggregates across segments for training
- Optional smoothing to reduce noise

### CurveTransferEngine
- Applies trained curves to new data
- Validates known actuals against expectations
- Flags significant variances for investigation

### ForecastGenerator
- Projects future cash flows using hazard curves
- Iteratively applies rates to calculate monthly amounts
- Handles balance depletion gracefully

### OutputFormatter
- Converts to ratio-based output format
- Calculates hazard rates for transparency
- Provides business-friendly column names

## Example Output

### Forecast Output (first few rows)
```
month_on_book  outstanding_balance_ratio  payments_ratio  chargeoffs_ratio  payment_hazard_rate  chargeoff_hazard_rate  forecast_flag
0              1.0000                     0.0000          0.0000           0.0000              0.0000                Actual
1              0.9250                     0.0680          0.0070           0.0735              0.0076                Actual  
2              0.8456                     0.0631          0.0163           0.0683              0.0176                Actual
...
13             0.4123                     0.0301          0.0045           0.0730              0.0109                Forecast
```

### Hazard Rate Curves
```
month_on_book  payment_hazard_rate  chargeoff_hazard_rate
0              0.0000              0.0000
1              0.0735              0.0076
2              0.0683              0.0176
3              0.0691              0.0145
...
```

## Validation Features

- **Data Quality Checks**: Missing columns, negative values, unreasonable rates
- **Business Logic Validation**: Balance flow consistency across months
- **Curve Validation**: Compare known actuals vs trained expectations
- **Range Validation**: Ensure hazard rates stay within [0, 1]

## Dollar Conversion

To convert ratio outputs to dollar amounts:
```python
# Example: Convert payment ratios to dollar forecasts
dollar_payments = forecast_output['payments_ratio'] * origination_amount
dollar_balances = forecast_output['outstanding_balance_ratio'] * origination_amount
```

## Phase 1 Design Principles

- **Simplicity**: Transparent empirical methods over complex statistical models
- **Explainability**: Clear connection between inputs and outputs
- **Business Focus**: Outputs designed for stakeholder consumption
- **Foundation**: Establishes framework for Phase 2-4 enhancements

## Next Steps (Phase 2+)

This Phase 1 implementation provides the foundation for:
- Advanced statistical methods (Kaplan-Meier, Cox models)
- Multi-segment batch processing
- Automated monitoring and variance detection
- Machine learning enhancements

## Support

For questions or issues, refer to the comprehensive PRD document and validation framework included in this repository.