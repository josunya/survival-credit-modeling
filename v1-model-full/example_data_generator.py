"""
Generate realistic example datasets for survival credit modeling.
Creates training and test data with typical loan performance patterns.
"""

import pandas as pd
import numpy as np
from typing import Dict, List


class LoanDataGenerator:
    """
    Generates realistic loan performance data for testing survival credit models.
    """
    
    def __init__(self, random_seed: int = 42):
        np.random.seed(random_seed)
        self.random_seed = random_seed
    
    def generate_training_data(self, 
                             segments: List[str] = None,
                             max_months: int = 48,
                             origination_amounts: Dict[str, float] = None) -> pd.DataFrame:
        """
        Generate training dataset with multiple completed loan segments.
        
        Args:
            segments: List of segment names
            max_months: Maximum loan age to generate
            origination_amounts: Dictionary mapping segments to origination amounts
            
        Returns:
            DataFrame with training data
        """
        
        if segments is None:
            segments = ['Prime_Auto_2021Q1', 'Near_Prime_Auto_2021Q1', 'Subprime_Auto_2021Q1']
        
        if origination_amounts is None:
            origination_amounts = {
                'Prime_Auto_2021Q1': 10_000_000,
                'Near_Prime_Auto_2021Q1': 5_000_000, 
                'Subprime_Auto_2021Q1': 3_000_000
            }
        
        all_data = []
        
        for segment in segments:
            segment_data = self._generate_segment_data(
                segment_id=segment,
                max_months=max_months,
                origination_amount=origination_amounts[segment],
                segment_type=self._get_segment_type(segment)
            )
            all_data.append(segment_data)
        
        return pd.concat(all_data, ignore_index=True)
    
    def generate_test_data(self,
                          segment_id: str = 'Prime_Auto_2023Q1',
                          known_months: int = 12,
                          origination_amount: float = 8_000_000) -> pd.DataFrame:
        """
        Generate test dataset with known actuals for forecasting.
        
        Args:
            segment_id: Test segment identifier
            known_months: Number of months of known actuals
            origination_amount: Total origination amount
            
        Returns:
            DataFrame with test data (known actuals only)
        """
        
        segment_type = self._get_segment_type(segment_id)
        
        return self._generate_segment_data(
            segment_id=segment_id,
            max_months=known_months,
            origination_amount=origination_amount,
            segment_type=segment_type
        )
    
    def _generate_segment_data(self,
                              segment_id: str,
                              max_months: int,
                              origination_amount: float,
                              segment_type: str) -> pd.DataFrame:
        """
        Generate data for a single segment with realistic payment/chargeoff patterns.
        """
        
        # Define hazard rate patterns by segment type
        hazard_patterns = {
            'prime': {
                'payment_base': 0.08,      # 8% monthly payment rate
                'payment_decay': 0.001,    # Slight decay over time
                'chargeoff_base': 0.005,   # 0.5% monthly chargeoff rate
                'chargeoff_peak': 6,       # Peak chargeoffs around month 6
                'chargeoff_decay': 0.02    # Faster decay after peak
            },
            'near_prime': {
                'payment_base': 0.09,
                'payment_decay': 0.0015,
                'chargeoff_base': 0.012,
                'chargeoff_peak': 8,
                'chargeoff_decay': 0.025
            },
            'subprime': {
                'payment_base': 0.11,
                'payment_decay': 0.002,
                'chargeoff_base': 0.025,
                'chargeoff_peak': 4,
                'chargeoff_decay': 0.03
            }
        }
        
        pattern = hazard_patterns.get(segment_type, hazard_patterns['prime'])
        
        data_rows = []
        current_balance = origination_amount
        
        for month in range(max_months + 1):
            # Calculate payment hazard rate (declining over time)
            payment_rate = pattern['payment_base'] * (1 - pattern['payment_decay'] * month)
            payment_rate = max(0.02, payment_rate)  # Floor at 2%
            
            # Calculate chargeoff hazard rate (peaks early, then declines)
            if month <= pattern['chargeoff_peak']:
                chargeoff_rate = pattern['chargeoff_base'] * (1 + 0.5 * month / pattern['chargeoff_peak'])
            else:
                decay_factor = np.exp(-pattern['chargeoff_decay'] * (month - pattern['chargeoff_peak']))
                chargeoff_rate = pattern['chargeoff_base'] * (1 + 0.5) * decay_factor
            
            chargeoff_rate = max(0.001, chargeoff_rate)  # Floor at 0.1%
            
            # Add some random noise
            payment_rate *= (1 + np.random.normal(0, 0.1))
            chargeoff_rate *= (1 + np.random.normal(0, 0.15))
            
            # Ensure rates are reasonable
            payment_rate = np.clip(payment_rate, 0.01, 0.20)
            chargeoff_rate = np.clip(chargeoff_rate, 0.001, 0.05)
            
            # Calculate dollar amounts
            payment_amount = current_balance * payment_rate
            chargeoff_amount = current_balance * chargeoff_rate
            
            # Ensure we don't exceed available balance
            total_outflow = payment_amount + chargeoff_amount
            if total_outflow > current_balance:
                scale_factor = current_balance / total_outflow
                payment_amount *= scale_factor
                chargeoff_amount *= scale_factor
            
            # Create data row
            row = {
                'segment_id': segment_id,
                'month_on_book': month,
                'outstanding_balance': current_balance,
                'payments': payment_amount,
                'chargeoffs': chargeoff_amount
            }
            
            data_rows.append(row)
            
            # Update balance for next month
            current_balance = current_balance - payment_amount - chargeoff_amount
            current_balance = max(0, current_balance)
            
            # Stop if balance is essentially zero
            if current_balance < origination_amount * 0.001:  # 0.1% of original
                break
        
        return pd.DataFrame(data_rows)
    
    def _get_segment_type(self, segment_id: str) -> str:
        """Extract segment type from segment ID."""
        segment_lower = segment_id.lower()
        
        if 'prime' in segment_lower and 'sub' not in segment_lower:
            return 'prime'
        elif 'near' in segment_lower or 'near_prime' in segment_lower:
            return 'near_prime'
        elif 'sub' in segment_lower:
            return 'subprime'
        else:
            return 'prime'  # Default
    
    def save_datasets(self, output_dir: str = '.'):
        """Generate and save example training and test datasets."""
        
        # Generate training data
        training_data = self.generate_training_data()
        training_file = f"{output_dir}/training_data_example.csv"
        training_data.to_csv(training_file, index=False)
        
        # Generate test data
        test_data = self.generate_test_data()
        test_file = f"{output_dir}/test_data_example.csv"
        test_data.to_csv(test_file, index=False)
        
        return {
            'training_file': training_file,
            'test_file': test_file,
            'training_shape': training_data.shape,
            'test_shape': test_data.shape
        }


def generate_example_datasets():
    """Convenience function to generate example datasets."""
    
    generator = LoanDataGenerator(random_seed=42)
    
    # Generate training data with 3 segments
    print("Generating training data...")
    training_data = generator.generate_training_data(
        segments=['Prime_Auto_2021Q1', 'Near_Prime_Auto_2021Q2', 'Subprime_Auto_2021Q3'],
        max_months=48
    )
    
    # Generate test data with 12 months of known actuals
    print("Generating test data...")
    test_data = generator.generate_test_data(
        segment_id='Prime_Auto_2023Q1',
        known_months=12,
        origination_amount=8_000_000
    )
    
    # Save to files
    training_data.to_csv('training_data_example.csv', index=False)
    test_data.to_csv('test_data_example.csv', index=False)
    
    print(f"Training data: {training_data.shape[0]} rows, {training_data.shape[1]} columns")
    print(f"Test data: {test_data.shape[0]} rows, {test_data.shape[1]} columns")
    print("\nTraining data segments:")
    print(training_data['segment_id'].value_counts())
    print(f"\nTest segment: {test_data['segment_id'].iloc[0]}")
    print(f"Test months: {test_data['month_on_book'].min()} to {test_data['month_on_book'].max()}")
    
    return training_data, test_data


if __name__ == "__main__":
    training_data, test_data = generate_example_datasets()