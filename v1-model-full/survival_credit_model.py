"""
Survival Credit Modeling Tool - Phase 1 Implementation
Simplified hazard rate modeling focusing on payment and chargeoff curves
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import warnings


class DataValidator:
    """
    Validates simplified flow-based input data for hazard rate modeling.
    """
    
    REQUIRED_COLUMNS = [
        'segment_id',         # Segment/vintage identifier
        'month_on_book',      # Months since origination (0, 1, 2, ...)
        'payments',           # Dollar payments made this month
        'chargeoffs',         # Dollar chargeoffs this month
        'outstanding_balance' # Balance at START of month (denominator)
    ]
    
    def __init__(self):
        self.validation_results = {}
    
    def validate_data(self, df: pd.DataFrame) -> Dict:
        """
        Validate input data structure and business logic.
        
        Args:
            df: Input DataFrame with loan flow data
            
        Returns:
            Dictionary with validation results
        """
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'summary': {}
        }
        
        # Check required columns
        missing_cols = set(self.REQUIRED_COLUMNS) - set(df.columns)
        if missing_cols:
            results['valid'] = False
            results['errors'].append(f"Missing required columns: {missing_cols}")
            return results
        
        # Check data types and ranges
        self._check_data_quality(df, results)
        
        # Check business logic
        self._check_business_logic(df, results)
        
        # Check completeness
        self._check_completeness(df, results)
        
        return results
    
    def _check_data_quality(self, df: pd.DataFrame, results: Dict):
        """Validate data types and reasonable ranges."""
        
        # Month on book should be non-negative integers
        if df['month_on_book'].min() < 0:
            results['errors'].append("month_on_book cannot be negative")
        
        # Outstanding balance should be positive
        if (df['outstanding_balance'] <= 0).any():
            results['warnings'].append("Zero or negative outstanding_balance detected")
        
        # Payments and chargeoffs should be non-negative
        if (df['payments'] < 0).any():
            results['errors'].append("Negative payments detected")
        
        if (df['chargeoffs'] < 0).any():
            results['errors'].append("Negative chargeoffs detected")
        
        # Check hazard rates are reasonable (0-100%)
        payment_rates = df['payments'] / df['outstanding_balance']
        chargeoff_rates = df['chargeoffs'] / df['outstanding_balance']
        
        if (payment_rates > 1.0).any():
            results['warnings'].append("Payment rates > 100% detected")
        
        if (chargeoff_rates > 1.0).any():
            results['warnings'].append("Chargeoff rates > 100% detected")
    
    def _check_business_logic(self, df: pd.DataFrame, results: Dict):
        """Validate business logic consistency."""
        
        # Check balance flow consistency for each segment
        for segment_id in df['segment_id'].unique():
            segment_df = df[df['segment_id'] == segment_id].sort_values('month_on_book')
            
            # Calculate implied next month balance
            segment_df = segment_df.copy()
            segment_df['implied_next_balance'] = (
                segment_df['outstanding_balance'] - 
                segment_df['payments'] - 
                segment_df['chargeoffs']
            )
            
            # Check if it matches actual next month (with tolerance)
            for i in range(len(segment_df) - 1):
                current_implied = segment_df.iloc[i]['implied_next_balance']
                next_actual = segment_df.iloc[i + 1]['outstanding_balance']
                
                if abs(current_implied - next_actual) > 0.01:  # $0.01 tolerance
                    results['warnings'].append(
                        f"Balance flow inconsistency in segment {segment_id} "
                        f"at month {segment_df.iloc[i]['month_on_book']}"
                    )
                    break  # Only report first inconsistency per segment
    
    def _check_completeness(self, df: pd.DataFrame, results: Dict):
        """Check for missing months within each segment."""
        
        for segment_id in df['segment_id'].unique():
            segment_df = df[df['segment_id'] == segment_id]
            months = sorted(segment_df['month_on_book'].unique())
            
            # Check for gaps in month sequence
            if months:
                expected_months = list(range(min(months), max(months) + 1))
                missing_months = set(expected_months) - set(months)
                
                if missing_months:
                    results['warnings'].append(
                        f"Missing months in segment {segment_id}: {missing_months}"
                    )


class HazardRateEstimator:
    """
    Estimates payment and chargeoff hazard rate curves from historical data.
    """
    
    def __init__(self, smoothing_window: int = 3):
        self.smoothing_window = smoothing_window
        self.hazard_curves = {}
    
    def fit(self, df: pd.DataFrame) -> Dict:
        """
        Estimate hazard rate curves from training data.
        
        Args:
            df: Training data with payment/chargeoff flows
            
        Returns:
            Dictionary containing estimated hazard rate curves
        """
        
        # Aggregate across all segments by month_on_book
        agg_df = df.groupby('month_on_book').agg({
            'outstanding_balance': 'sum',
            'payments': 'sum',
            'chargeoffs': 'sum'
        }).reset_index()
        
        # Calculate hazard rates
        agg_df['payment_hazard_rate'] = agg_df['payments'] / agg_df['outstanding_balance']
        agg_df['chargeoff_hazard_rate'] = agg_df['chargeoffs'] / agg_df['outstanding_balance']
        
        # Handle division by zero
        agg_df['payment_hazard_rate'] = agg_df['payment_hazard_rate'].fillna(0)
        agg_df['chargeoff_hazard_rate'] = agg_df['chargeoff_hazard_rate'].fillna(0)
        
        # Apply smoothing if requested
        if self.smoothing_window > 1:
            agg_df['payment_hazard_rate_smoothed'] = agg_df['payment_hazard_rate'].rolling(
                window=self.smoothing_window, center=True, min_periods=1
            ).mean()
            agg_df['chargeoff_hazard_rate_smoothed'] = agg_df['chargeoff_hazard_rate'].rolling(
                window=self.smoothing_window, center=True, min_periods=1
            ).mean()
        else:
            agg_df['payment_hazard_rate_smoothed'] = agg_df['payment_hazard_rate']
            agg_df['chargeoff_hazard_rate_smoothed'] = agg_df['chargeoff_hazard_rate']
        
        # Store hazard curves as dictionaries for easy lookup
        self.hazard_curves = {
            'payment_hazard': dict(zip(agg_df['month_on_book'], agg_df['payment_hazard_rate_smoothed'])),
            'chargeoff_hazard': dict(zip(agg_df['month_on_book'], agg_df['chargeoff_hazard_rate_smoothed'])),
            'training_data': agg_df
        }
        
        return self.hazard_curves
    
    def get_hazard_rate(self, month: int, hazard_type: str) -> float:
        """
        Get hazard rate for specific month on book.
        
        Args:
            month: Month on book
            hazard_type: 'payment' or 'chargeoff'
            
        Returns:
            Hazard rate for the given month
        """
        if not self.hazard_curves:
            raise ValueError("Model must be fitted first")
        
        curve_key = f"{hazard_type}_hazard"
        if curve_key not in self.hazard_curves:
            raise ValueError(f"Invalid hazard_type: {hazard_type}")
        
        rates = self.hazard_curves[curve_key]
        
        # Return exact rate if available
        if month in rates:
            return rates[month]
        
        # Otherwise interpolate or extrapolate
        available_months = sorted(rates.keys())
        
        if not available_months:
            return 0.0
        
        if month < min(available_months):
            return rates[min(available_months)]
        elif month > max(available_months):
            # Use last available rate for extrapolation
            return rates[max(available_months)]
        else:
            # Linear interpolation
            lower_month = max([m for m in available_months if m <= month])
            upper_month = min([m for m in available_months if m >= month])
            
            if lower_month == upper_month:
                return rates[lower_month]
            
            weight = (month - lower_month) / (upper_month - lower_month)
            return rates[lower_month] * (1 - weight) + rates[upper_month] * weight


class CurveTransferEngine:
    """
    Applies trained hazard rate curves to new data for validation and forecasting.
    """
    
    def __init__(self, rate_estimator: HazardRateEstimator):
        self.rate_estimator = rate_estimator
    
    def validate_known_actuals(self, df: pd.DataFrame) -> Dict:
        """
        Compare known actuals against trained curves.
        
        Args:
            df: DataFrame with known actual performance
            
        Returns:
            Validation results comparing actuals vs expected curves
        """
        results = {
            'detailed_comparison': [],
            'summary_stats': {},
            'warnings': []
        }
        
        for _, row in df.iterrows():
            month = row['month_on_book']
            
            # Get expected rates from trained curves
            expected_payment_rate = self.rate_estimator.get_hazard_rate(month, 'payment')
            expected_chargeoff_rate = self.rate_estimator.get_hazard_rate(month, 'chargeoff')
            
            # Calculate actual rates
            actual_payment_rate = row['payments'] / row['outstanding_balance']
            actual_chargeoff_rate = row['chargeoffs'] / row['outstanding_balance']
            
            # Calculate variances
            payment_variance = actual_payment_rate - expected_payment_rate
            chargeoff_variance = actual_chargeoff_rate - expected_chargeoff_rate
            
            comparison = {
                'month_on_book': month,
                'expected_payment_rate': expected_payment_rate,
                'actual_payment_rate': actual_payment_rate,
                'payment_variance': payment_variance,
                'expected_chargeoff_rate': expected_chargeoff_rate,
                'actual_chargeoff_rate': actual_chargeoff_rate,
                'chargeoff_variance': chargeoff_variance
            }
            
            results['detailed_comparison'].append(comparison)
            
            # Flag large variances
            if abs(payment_variance) > 0.05:  # 5% threshold
                results['warnings'].append(
                    f"Large payment variance at month {month}: {payment_variance:.3f}"
                )
            
            if abs(chargeoff_variance) > 0.02:  # 2% threshold
                results['warnings'].append(
                    f"Large chargeoff variance at month {month}: {chargeoff_variance:.3f}"
                )
        
        # Calculate summary statistics
        if results['detailed_comparison']:
            comparison_df = pd.DataFrame(results['detailed_comparison'])
            results['summary_stats'] = {
                'mean_payment_variance': comparison_df['payment_variance'].mean(),
                'mean_chargeoff_variance': comparison_df['chargeoff_variance'].mean(),
                'rmse_payment': np.sqrt((comparison_df['payment_variance'] ** 2).mean()),
                'rmse_chargeoff': np.sqrt((comparison_df['chargeoff_variance'] ** 2).mean())
            }
        
        return results


class ForecastGenerator:
    """
    Generates forecasts by applying hazard rate curves to project future cash flows.
    """
    
    def __init__(self, rate_estimator: HazardRateEstimator):
        self.rate_estimator = rate_estimator
    
    def generate_forecast(self, known_actuals: pd.DataFrame, max_month: int) -> pd.DataFrame:
        """
        Generate forecast extending known actuals using hazard rate curves.
        
        Args:
            known_actuals: DataFrame with actual performance through current month
            max_month: Maximum month on book to forecast to
            
        Returns:
            Complete forecast DataFrame with actual and forecasted months
        """
        
        # Start with known actuals
        forecast_df = known_actuals.copy()
        forecast_df['forecast_flag'] = 'Actual'
        
        # Get the last known month and ending balance
        last_known_month = forecast_df['month_on_book'].max()
        last_row = forecast_df[forecast_df['month_on_book'] == last_known_month].iloc[0]
        
        # Calculate ending balance for last known month
        current_balance = (
            last_row['outstanding_balance'] - 
            last_row['payments'] - 
            last_row['chargeoffs']
        )
        
        # Generate forecasts for remaining months
        forecast_rows = []
        
        for month in range(last_known_month + 1, max_month + 1):
            if current_balance <= 0.01:  # Stop if balance is essentially zero
                break
            
            # Get hazard rates from trained curves
            payment_rate = self.rate_estimator.get_hazard_rate(month, 'payment')
            chargeoff_rate = self.rate_estimator.get_hazard_rate(month, 'chargeoff')
            
            # Calculate dollar flows
            payment_amount = current_balance * payment_rate
            chargeoff_amount = current_balance * chargeoff_rate
            
            # Create forecast row
            forecast_row = {
                'segment_id': last_row['segment_id'],
                'month_on_book': month,
                'outstanding_balance': current_balance,
                'payments': payment_amount,
                'chargeoffs': chargeoff_amount,
                'forecast_flag': 'Forecast'
            }
            
            forecast_rows.append(forecast_row)
            
            # Update balance for next iteration
            current_balance = current_balance - payment_amount - chargeoff_amount
            current_balance = max(0, current_balance)  # Ensure non-negative
        
        # Combine actuals and forecasts
        if forecast_rows:
            forecast_extension = pd.DataFrame(forecast_rows)
            complete_forecast = pd.concat([forecast_df, forecast_extension], ignore_index=True)
        else:
            complete_forecast = forecast_df
        
        return complete_forecast.sort_values('month_on_book')


class OutputFormatter:
    """
    Formats outputs with hazard rate curves and ratio-based projections.
    """
    
    def __init__(self):
        pass
    
    def format_curves_output(self, forecast_df: pd.DataFrame, origination_amount: float) -> pd.DataFrame:
        """
        Format forecast with hazard rate curves and balance ratios.
        
        Args:
            forecast_df: Complete forecast DataFrame
            origination_amount: Original loan amount for ratio calculations
            
        Returns:
            Formatted output with curves and ratios
        """
        output_df = forecast_df.copy()
        
        # Calculate hazard rates
        output_df['payment_hazard_rate'] = output_df['payments'] / output_df['outstanding_balance']
        output_df['chargeoff_hazard_rate'] = output_df['chargeoffs'] / output_df['outstanding_balance']
        
        # Calculate ratios as percentage of origination
        output_df['outstanding_balance_ratio'] = output_df['outstanding_balance'] / origination_amount
        output_df['payments_ratio'] = output_df['payments'] / origination_amount
        output_df['chargeoffs_ratio'] = output_df['chargeoffs'] / origination_amount
        
        # Select final columns
        final_columns = [
            'month_on_book',
            'outstanding_balance_ratio',
            'payments_ratio', 
            'chargeoffs_ratio',
            'payment_hazard_rate',
            'chargeoff_hazard_rate',
            'forecast_flag'
        ]
        
        return output_df[final_columns]
    
    def save_output(self, output_df: pd.DataFrame, file_path: str, format: str = 'csv'):
        """Save formatted output to file."""
        if format.lower() == 'csv':
            output_df.to_csv(file_path, index=False)
        elif format.lower() in ['excel', 'xlsx']:
            output_df.to_excel(file_path, index=False)
        else:
            raise ValueError(f"Unsupported format: {format}")


class SurvivalCreditModel:
    """
    Main pipeline for hazard rate-based survival credit modeling.
    """
    
    def __init__(self, smoothing_window: int = 3):
        self.validator = DataValidator()
        self.rate_estimator = HazardRateEstimator(smoothing_window=smoothing_window)
        self.curve_engine = CurveTransferEngine(self.rate_estimator)
        self.forecast_generator = ForecastGenerator(self.rate_estimator)
        self.output_formatter = OutputFormatter()
        
        self.is_trained = False
    
    def train(self, training_data: pd.DataFrame) -> Dict:
        """
        Train hazard rate curves on historical data.
        
        Args:
            training_data: Historical loan flow data
            
        Returns:
            Training results and validation metrics
        """
        
        # Validate input data
        validation_results = self.validator.validate_data(training_data)
        
        if not validation_results['valid']:
            raise ValueError(f"Training data validation failed: {validation_results['errors']}")
        
        # Fit hazard rate curves
        hazard_curves = self.rate_estimator.fit(training_data)
        
        self.is_trained = True
        
        return {
            'validation_results': validation_results,
            'hazard_curves': hazard_curves,
            'training_summary': {
                'segments_processed': training_data['segment_id'].nunique(),
                'max_month': training_data['month_on_book'].max(),
                'total_volume': training_data['outstanding_balance'].sum()
            }
        }
    
    def forecast(self, known_actuals: pd.DataFrame, origination_amount: float, 
                max_month: int = 60) -> Tuple[pd.DataFrame, Dict]:
        """
        Generate forecast for new segment.
        
        Args:
            known_actuals: Known actual performance
            origination_amount: Original loan amount for ratio calculations
            max_month: Maximum month to forecast to
            
        Returns:
            Tuple of (formatted_output, validation_results)
        """
        
        if not self.is_trained:
            raise ValueError("Model must be trained before forecasting")
        
        # Validate known actuals
        validation_results = self.validator.validate_data(known_actuals)
        if not validation_results['valid']:
            raise ValueError(f"Known actuals validation failed: {validation_results['errors']}")
        
        # Validate against training curves
        curve_validation = self.curve_engine.validate_known_actuals(known_actuals)
        
        # Generate forecast
        forecast_df = self.forecast_generator.generate_forecast(known_actuals, max_month)
        
        # Format output
        formatted_output = self.output_formatter.format_curves_output(forecast_df, origination_amount)
        
        return formatted_output, {
            'data_validation': validation_results,
            'curve_validation': curve_validation
        }
    
    def get_hazard_curves(self) -> Dict:
        """Get the trained hazard rate curves."""
        if not self.is_trained:
            return {"error": "Model not trained"}
        
        return self.rate_estimator.hazard_curves