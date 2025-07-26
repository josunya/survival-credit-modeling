"""
Test the complete survival credit modeling pipeline with example data.
Validates all components and demonstrates end-to-end workflow.
"""

import pandas as pd
import numpy as np
from survival_credit_model import SurvivalCreditModel
from example_data_generator import generate_example_datasets
import matplotlib.pyplot as plt


def test_full_pipeline():
    """
    Test the complete pipeline from data generation to forecasting.
    """
    
    print("=== Testing Survival Credit Modeling Pipeline ===\n")
    
    # Step 1: Generate example data
    print("1. Generating example datasets...")
    training_data, test_data = generate_example_datasets()
    print(f"   Training data: {training_data.shape}")
    print(f"   Test data: {test_data.shape}")
    print(f"   Training segments: {training_data['segment_id'].unique()}")
    print(f"   Test segment: {test_data['segment_id'].iloc[0]}\n")
    
    # Step 2: Initialize and train the model
    print("2. Training the survival credit model...")
    model = SurvivalCreditModel(smoothing_window=3)
    
    try:
        training_results = model.train(training_data)
        print("   ✓ Training completed successfully")
        print(f"   ✓ Validation passed: {training_results['validation_results']['valid']}")
        print(f"   ✓ Segments processed: {training_results['training_summary']['segments_processed']}")
        print(f"   ✓ Max month trained: {training_results['training_summary']['max_month']}")
        
        # Display hazard curves
        hazard_curves = model.get_hazard_curves()
        print(f"   ✓ Payment hazard rates: {len(hazard_curves['payment_hazard'])} months")
        print(f"   ✓ Chargeoff hazard rates: {len(hazard_curves['chargeoff_hazard'])} months\n")
        
    except Exception as e:
        print(f"   ✗ Training failed: {e}")
        return False
    
    # Step 3: Generate forecast
    print("3. Generating forecast for test segment...")
    origination_amount = 8_000_000  # From test data generation
    
    try:
        forecast_output, validation_results = model.forecast(
            known_actuals=test_data,
            origination_amount=origination_amount,
            max_month=48
        )
        
        print("   ✓ Forecast completed successfully")
        print(f"   ✓ Data validation passed: {validation_results['data_validation']['valid']}")
        print(f"   ✓ Output shape: {forecast_output.shape}")
        print(f"   ✓ Months forecasted: {forecast_output['month_on_book'].min()} to {forecast_output['month_on_book'].max()}")
        
        # Check curve validation
        curve_val = validation_results['curve_validation']
        if curve_val['warnings']:
            print(f"   ⚠ Curve validation warnings: {len(curve_val['warnings'])}")
        else:
            print("   ✓ Curve validation: No significant warnings")
        
        print(f"   ✓ Mean payment variance: {curve_val['summary_stats']['mean_payment_variance']:.4f}")
        print(f"   ✓ Mean chargeoff variance: {curve_val['summary_stats']['mean_chargeoff_variance']:.4f}\n")
        
    except Exception as e:
        print(f"   ✗ Forecasting failed: {e}")
        return False
    
    # Step 4: Analyze results
    print("4. Analyzing forecast results...")
    
    # Separate actual vs forecast
    actuals = forecast_output[forecast_output['forecast_flag'] == 'Actual']
    forecasts = forecast_output[forecast_output['forecast_flag'] == 'Forecast']
    
    print(f"   ✓ Actual months: {len(actuals)}")
    print(f"   ✓ Forecast months: {len(forecasts)}")
    
    # Summary statistics
    print(f"   ✓ Starting balance ratio: {forecast_output['outstanding_balance_ratio'].iloc[0]:.3f}")
    print(f"   ✓ Final balance ratio: {forecast_output['outstanding_balance_ratio'].iloc[-1]:.3f}")
    print(f"   ✓ Total payments ratio: {forecast_output['payments_ratio'].sum():.3f}")
    print(f"   ✓ Total chargeoffs ratio: {forecast_output['chargeoffs_ratio'].sum():.3f}")
    
    # Check hazard rates are reasonable
    payment_rates = forecast_output['payment_hazard_rate']
    chargeoff_rates = forecast_output['chargeoff_hazard_rate']
    
    print(f"   ✓ Payment hazard rates: {payment_rates.min():.4f} to {payment_rates.max():.4f}")
    print(f"   ✓ Chargeoff hazard rates: {chargeoff_rates.min():.4f} to {chargeoff_rates.max():.4f}")
    
    # Validate hazard rates are between 0-100%
    if (payment_rates < 0).any() or (payment_rates > 1).any():
        print("   ✗ Payment hazard rates outside valid range [0, 1]")
        return False
    
    if (chargeoff_rates < 0).any() or (chargeoff_rates > 1).any():
        print("   ✗ Chargeoff hazard rates outside valid range [0, 1]")
        return False
    
    print("   ✓ All hazard rates within valid range [0, 1]\n")
    
    # Step 5: Save results
    print("5. Saving results...")
    try:
        # Save forecast output
        forecast_output.to_csv('forecast_output_test.csv', index=False)
        print("   ✓ Forecast saved to 'forecast_output_test.csv'")
        
        # Save hazard curves for inspection
        hazard_curves = model.get_hazard_curves()
        curves_df = pd.DataFrame({
            'month_on_book': list(hazard_curves['payment_hazard'].keys()),
            'payment_hazard_rate': list(hazard_curves['payment_hazard'].values()),
            'chargeoff_hazard_rate': [hazard_curves['chargeoff_hazard'].get(m, 0) 
                                    for m in hazard_curves['payment_hazard'].keys()]
        })
        curves_df.to_csv('hazard_curves_test.csv', index=False)
        print("   ✓ Hazard curves saved to 'hazard_curves_test.csv'\n")
        
    except Exception as e:
        print(f"   ✗ Failed to save results: {e}")
        return False
    
    # Step 6: Display sample results
    print("6. Sample forecast output (first 10 rows):")
    print(forecast_output.head(10).round(4))
    print("\n   Sample forecast output (last 5 rows):")
    print(forecast_output.tail(5).round(4))
    
    print("\n=== Pipeline Test Completed Successfully ===")
    return True


def test_error_handling():
    """
    Test error handling and edge cases.
    """
    
    print("\n=== Testing Error Handling ===\n")
    
    model = SurvivalCreditModel()
    
    # Test 1: Forecast without training
    print("1. Testing forecast without training...")
    try:
        fake_data = pd.DataFrame({
            'segment_id': ['test'],
            'month_on_book': [0],
            'outstanding_balance': [1000],
            'payments': [100],
            'chargeoffs': [10]
        })
        model.forecast(fake_data, 1000)
        print("   ✗ Should have failed")
        return False
    except ValueError as e:
        print(f"   ✓ Correctly caught error: {str(e)[:50]}...")
    
    # Test 2: Invalid training data
    print("2. Testing invalid training data...")
    try:
        invalid_data = pd.DataFrame({
            'wrong_column': [1, 2, 3],
            'another_wrong': [4, 5, 6]
        })
        model.train(invalid_data)
        print("   ✗ Should have failed")
        return False
    except ValueError as e:
        print(f"   ✓ Correctly caught error: {str(e)[:50]}...")
    
    # Test 3: Negative values
    print("3. Testing negative payment values...")
    try:
        negative_data = pd.DataFrame({
            'segment_id': ['test'],
            'month_on_book': [0],
            'outstanding_balance': [1000],
            'payments': [-100],  # Negative payment
            'chargeoffs': [10]
        })
        result = model.validator.validate_data(negative_data)
        if result['valid']:
            print("   ✗ Should have detected negative payments")
            return False
        else:
            print("   ✓ Correctly detected negative payments")
    except Exception as e:
        print(f"   ✓ Correctly caught error: {str(e)[:50]}...")
    
    print("   ✓ Error handling tests passed\n")
    return True


def create_visualization():
    """
    Create simple visualizations of the results (if matplotlib available).
    """
    
    try:
        # Read saved results
        forecast_df = pd.read_csv('forecast_output_test.csv')
        curves_df = pd.read_csv('hazard_curves_test.csv')
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        
        # Plot 1: Outstanding balance over time
        ax1.plot(forecast_df['month_on_book'], forecast_df['outstanding_balance_ratio'])
        ax1.set_title('Outstanding Balance Ratio Over Time')
        ax1.set_xlabel('Month on Book')
        ax1.set_ylabel('Balance Ratio')
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Cumulative payments and chargeoffs
        forecast_df['cum_payments'] = forecast_df['payments_ratio'].cumsum()
        forecast_df['cum_chargeoffs'] = forecast_df['chargeoffs_ratio'].cumsum()
        
        ax2.plot(forecast_df['month_on_book'], forecast_df['cum_payments'], label='Payments')
        ax2.plot(forecast_df['month_on_book'], forecast_df['cum_chargeoffs'], label='Chargeoffs')
        ax2.set_title('Cumulative Payments and Chargeoffs')
        ax2.set_xlabel('Month on Book')
        ax2.set_ylabel('Cumulative Ratio')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Payment hazard rates
        ax3.plot(curves_df['month_on_book'], curves_df['payment_hazard_rate'])
        ax3.set_title('Payment Hazard Rate Curve')
        ax3.set_xlabel('Month on Book')
        ax3.set_ylabel('Payment Hazard Rate')
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Chargeoff hazard rates
        ax4.plot(curves_df['month_on_book'], curves_df['chargeoff_hazard_rate'])
        ax4.set_title('Chargeoff Hazard Rate Curve')
        ax4.set_xlabel('Month on Book')
        ax4.set_ylabel('Chargeoff Hazard Rate')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('survival_model_results.png', dpi=150, bbox_inches='tight')
        print("   ✓ Visualization saved to 'survival_model_results.png'")
        
    except ImportError:
        print("   ⚠ Matplotlib not available, skipping visualization")
    except Exception as e:
        print(f"   ⚠ Visualization failed: {e}")


if __name__ == "__main__":
    # Run all tests
    success = True
    
    success &= test_full_pipeline()
    success &= test_error_handling()
    
    if success:
        print("Creating visualization...")
        create_visualization()
        print("\n🎉 All tests passed successfully!")
    else:
        print("\n❌ Some tests failed")
    
    # Print summary
    print(f"\nFiles created:")
    print("- training_data_example.csv")
    print("- test_data_example.csv") 
    print("- forecast_output_test.csv")
    print("- hazard_curves_test.csv")
    print("- survival_model_results.png (if matplotlib available)")