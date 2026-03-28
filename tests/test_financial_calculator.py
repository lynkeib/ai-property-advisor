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
        )
        
        assert metrics.loan_amount == 400000
        assert metrics.monthly_mortgage_payment > 0
        assert metrics.monthly_property_tax == pytest.approx(625, rel=0.01)
        assert metrics.monthly_total_cost > 0
        assert metrics.total_principal_30_years == 400000
        assert metrics.total_interest_30_years > 0
        assert metrics.total_cost_30_years_excluding_principal > 0
    
    def test_metrics_30_year_totals(self):
        """Test 30-year principal and interest totals."""
        metrics = FinancialCalculator.calculate_metrics(
            price=300000,
            down_payment=60000,
            interest_rate=5.0,
            hoa=100,
            property_tax_rate=0.01,
            insurance=100,
        )
        
        # Verify 30-year calculations
        assert metrics.total_principal_30_years == pytest.approx(240000, rel=0.01)
        assert metrics.total_interest_30_years == pytest.approx(
            (metrics.monthly_mortgage_payment * 360) - metrics.loan_amount,
            rel=0.01,
        )
        assert metrics.total_cost_30_years_excluding_principal == pytest.approx(
            metrics.total_interest_30_years + ((metrics.monthly_property_tax + 100 + 100) * 360),
            rel=0.01,
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
