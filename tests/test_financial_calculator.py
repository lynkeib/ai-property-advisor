"""Unit tests for financial calculator."""

import pytest
from backend.services.financial_calculator import FinancialCalculator


class TestFinancialCalculator:
    """Test cases for financial calculations."""
    
    def test_mortgage_payment_zero_interest(self):
        """Test mortgage calculation with 0% interest."""
        loan = 300000
        rate = 0
        payment = FinancialCalculator.calculate_monthly_mortgage(loan, rate, 30)
        expected = loan / (30 * 12)
        assert payment == pytest.approx(expected, rel=1e-2)
    
    def test_mortgage_payment_standard(self):
        """Test mortgage with standard 6.5% rate."""
        loan = 400000
        rate = 6.5
        payment = FinancialCalculator.calculate_monthly_mortgage(loan, rate, 30)
        # Expected approximately $2,528.17 for $400k at 6.5% for 30 years
        assert 2500 < payment < 2600
    
    def test_mortgage_payment_zero_loan(self):
        """Test mortgage payment with no loan."""
        payment = FinancialCalculator.calculate_monthly_mortgage(0, 6.5, 30)
        assert payment == 0
    
    def test_metrics_basic_calculation(self):
        """Test complete metrics calculation."""
        metrics = FinancialCalculator.calculate_metrics(
            price=500000,
            down_payment=100000,
            interest_rate=6.5,
            hoa=250,
            property_tax_rate=0.015,
            insurance=150,
            rent_estimate=2500
        )
        
        assert metrics.loan_amount == 400000
        assert metrics.monthly_mortgage_payment > 0
        assert metrics.monthly_property_tax == pytest.approx(625, rel=0.01)
        assert metrics.monthly_total_cost > 0
        assert metrics.total_cost_10_years == pytest.approx(
            metrics.monthly_total_cost * 120, rel=0.01
        )
    
    def test_metrics_10_year_projection(self):
        """Test 10-year cost projections."""
        metrics = FinancialCalculator.calculate_metrics(
            price=300000,
            down_payment=60000,
            interest_rate=5.0,
            hoa=100,
            property_tax_rate=0.01,
            insurance=100,
            rent_estimate=1500
        )
        
        # Verify 10-year calculations
        assert metrics.total_cost_10_years == pytest.approx(
            metrics.monthly_total_cost * 120, rel=0.01
        )
        assert metrics.total_rent_10_years == pytest.approx(1500 * 120, rel=0.01)
    
    def test_buy_vs_rent_comparison(self):
        """Test buy vs rent delta calculation."""
        metrics = FinancialCalculator.calculate_metrics(
            price=400000,
            down_payment=80000,
            interest_rate=6.0,
            hoa=200,
            property_tax_rate=0.015,
            insurance=125,
            rent_estimate=2500
        )
        
        expected_delta = metrics.total_rent_10_years - metrics.total_cost_10_years
        assert metrics.buy_vs_rent_delta == pytest.approx(expected_delta, rel=0.01)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
