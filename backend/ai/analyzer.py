"""OpenAI integration for property analysis insights."""

import logging
import os
from typing import Optional

import openai

from backend.models.schemas import FinancialMetrics

logger = logging.getLogger(__name__)


class PropertyAnalyzer:
    """Uses OpenAI API to generate AI-powered investment insights."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with OpenAI API key from parameter or environment."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        openai.api_key = self.api_key
    
    def analyze(
        self,
        metrics: FinancialMetrics,
        price: float,
        rent_estimate: float
    ) -> str:
        """
        Generate AI analysis of property investment based on calculated metrics.
        
        Returns investment summary, key risks, and recommendation.
        """
        
        prompt = self._build_prompt(metrics, price, rent_estimate)
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert real estate investment analyst. Provide concise, actionable insights."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            analysis = response["choices"][0]["message"]["content"]
            logger.info("Successfully generated AI analysis")
            return analysis
            
        except openai.error.OpenAIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    @staticmethod
    def _build_prompt(
        metrics: FinancialMetrics,
        price: float,
        rent_estimate: float
    ) -> str:
        """Build the prompt for OpenAI analysis."""
        
        return f"""Based on these real estate investment metrics, provide a brief analysis:

Property Price: ${price:,.0f}
Monthly Mortgage: ${metrics.monthly_mortgage_payment:,.2f}
Monthly Property Tax: ${metrics.monthly_property_tax:,.2f}
Total Monthly Cost: ${metrics.monthly_total_cost:,.2f}
Estimated Monthly Rent: ${rent_estimate:,.2f}

10-Year Projections:
- Buy Total Cost: ${metrics.total_cost_10_years:,.2f}
- Rent Total Cost: ${metrics.total_rent_10_years:,.2f}
- Buy vs Rent Delta: ${metrics.buy_vs_rent_delta:,.2f}

Please provide:
1. Investment Summary (1-2 sentences)
2. Key Risks (2-3 bullet points)
3. Recommendation (buy/rent/neutral)

Be concise and practical."""
