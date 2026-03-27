"""Financial calculator service - deterministic calculations only."""

import logging
from decimal import Decimal, ROUND_HALF_UP

from backend.models.schemas import FinancialMetrics

logger = logging.getLogger(__name__)


class FinancialCalculator:
    """Handles all deterministic financial calculations for real estate analysis."""
    
    @staticmethod
    def calculate_monthly_mortgage(
        loan_amount: float,
        annual_interest_rate: float,
        years: int = 30
    ) -> float:
        """
        Calculate monthly mortgage payment using amortization formula.
        
        Formula: M = P * [r(1+r)^n] / [(1+r)^n-1]
        where:
        - P = principal (loan amount)
        - r = monthly interest rate
        - n = number of payments
        """
        if loan_amount == 0:
            return 0.0
            
        monthly_rate = annual_interest_rate / 100 / 12
        if monthly_rate == 0:  # Handle edge case of 0% interest
            return loan_amount / (years * 12)
            
        num_payments = years * 12
        numerator = monthly_rate * (1 + monthly_rate) ** num_payments
        denominator = (1 + monthly_rate) ** num_payments - 1
        
        payment = loan_amount * (numerator / denominator)
        return round(payment, 2)
    
    @staticmethod
    def calculate_metrics(
        price: float,
        down_payment: float,
        interest_rate: float,
        hoa: float,
        property_tax_rate: float,
        insurance: float,
        rent_estimate: float
    ) -> FinancialMetrics:
        """Calculate all financial metrics for property analysis."""
        
        # Basic calculations
        loan_amount = price - down_payment
        monthly_mortgage = FinancialCalculator.calculate_monthly_mortgage(
            loan_amount, interest_rate
        )
        
        monthly_property_tax = price * property_tax_rate / 12
        monthly_total_cost = monthly_mortgage + monthly_property_tax + hoa + insurance
        
        # 10-year projections (120 months)
        months = 120
        total_cost_10_years = round(monthly_total_cost * months, 2)
        total_rent_10_years = round(rent_estimate * months, 2)
        
        # Buy vs rent comparison
        buy_vs_rent_delta = round(total_rent_10_years - total_cost_10_years, 2)
        
        # Calculate break-even months (when cumulative buy cost equals rent)
        break_even_months = None
        if monthly_total_cost > rent_estimate and monthly_total_cost > 0:
            # Simple payoff calculation without considering principal buildup
            break_even_months = round(
                down_payment / (rent_estimate - monthly_total_cost),
                2
            ) if (rent_estimate - monthly_total_cost) != 0 else None
            # Cap at 360 months (30 years) for practical purposes
            if break_even_months and break_even_months > 360:
                break_even_months = None
        
        return FinancialMetrics(
            loan_amount=round(loan_amount, 2),
            monthly_mortgage_payment=monthly_mortgage,
            monthly_property_tax=round(monthly_property_tax, 2),
            monthly_total_cost=round(monthly_total_cost, 2),
            total_cost_10_years=total_cost_10_years,
            total_rent_10_years=total_rent_10_years,
            buy_vs_rent_delta=buy_vs_rent_delta,
            break_even_months=break_even_months
        )
