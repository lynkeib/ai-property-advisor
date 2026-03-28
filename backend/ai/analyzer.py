"""AI integration for property analysis insights."""

import logging
import os
from typing import Optional

import google.generativeai as genai  # type: ignore

from backend.models.schemas import FinancialMetrics

logger = logging.getLogger(__name__)


class GeminiAnalyzer:
    """Uses Google Gemini via google-genai SDK for text generation."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        genai.configure(api_key=self.api_key)

    def list_available_models(self) -> dict:
        """List all available Google Generative AI models and their capabilities."""
        try:
            logger.info("Fetching available models from Google Generative AI...")

            models = genai.list_models()

            # Models that support generateContent (text generation)
            generate_content_models = []
            embed_content_models = []

            for model in models:
                model_name = model.name

                # Check model capabilities
                if hasattr(model, 'supported_generation_methods'):
                    methods = model.supported_generation_methods
                else:
                    # Try to infer from model name and common patterns
                    methods = []
                    if 'gemini' in model_name.lower():
                        methods.append('generateContent')
                    if any(embed_model in model_name.lower() for embed_model in ['embedding', 'embed']):
                        methods.append('embedContent')

                # Check for generateContent capability
                if 'generateContent' in methods or 'generate_content' in str(model).lower():
                    generate_content_models.append(model_name)

                # Check for embedContent capability
                if 'embedContent' in methods or 'embed_content' in str(model).lower():
                    embed_content_models.append(model_name)

            return {
                'generate_content_models': generate_content_models,
                'embed_content_models': embed_content_models
            }

        except Exception as e:
            logger.error(f"Error listing models: {e}")
            # Return default models if API fails
            return {
                'generate_content_models': ["gemini-1.5-flash", "gemini-1.5-pro"],
                'embed_content_models': ["text-embedding-004"]
            }

    def generate(
        self,
        prompt: str,
        model: str = "gemini-1.5-flash",
        max_tokens: int = 256,
        temperature: float = 0.0,
    ) -> str:
        """Generate text from Gemini model."""
        if not prompt.strip():
            raise ValueError("Prompt must not be empty")

        try:
            # Create model with specified parameters
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )

            model_instance = genai.GenerativeModel(
                model_name=model,
                generation_config=generation_config
            )

            response = model_instance.generate_content(prompt)

            if response.text:
                logger.info("Successfully generated text from Gemini")
                return response.text
            else:
                raise ValueError("Empty response from Gemini API")

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise

    def analyze(
        self,
        metrics: FinancialMetrics,
        price: float,
        model: str = "gemini-1.5-flash"
    ) -> str:
        """
        Generate AI analysis of property investment based on calculated metrics.

        Returns investment summary, key risks, and recommendation.
        """

        prompt = self._build_prompt(metrics, price)

        try:
            analysis = self.generate(
                prompt=prompt,
                model=model,
                max_tokens=8192,
                temperature=0.7,
            )
            logger.info("Successfully generated AI analysis from Gemini")
            return analysis

        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise

    @staticmethod
    def _build_prompt(
        metrics: FinancialMetrics,
        price: float,
    ) -> str:
        """Build the prompt for Gemini analysis."""

        prompt = """Based on these real estate investment metrics, provide a comprehensive analysis of this property investment opportunity:

Property Details:
- Property Price: ${price:,.0f}
- Monthly Mortgage Payment: ${monthly_mortgage:,.2f}
- Monthly Property Tax: ${monthly_tax:,.2f}
- Monthly HOA/Insurance: ${monthly_hoa:,.2f}
- Total Monthly Ownership Cost: ${monthly_total:,.2f}

30-Year Financial Projections:
- Total Principal Paid (30 years): ${total_principal:,.2f}
- Total Interest Paid (30 years): ${total_interest:,.2f}
- Total Ownership Cost Excluding Principal (30 years): ${total_cost_excl_principal:,.2f}

Please provide a detailed analysis covering:

1. **Investment Summary**: Comprehensive overview of the financial opportunity
2. **Cash Flow Analysis**: Monthly cash flow, ROI calculations, and long-term projections
3. **Market Considerations**: Current market conditions and property appreciation potential
4. **Risk Assessment**: Key risks including interest rate changes, market fluctuations, and property-specific concerns
5. **Tax Implications**: Potential tax benefits and deductions
6. **Recommendation**: Clear investment recommendation with reasoning

IMPORTANT: Provide a COMPLETE and COMPREHENSIVE analysis. Do not truncate your response - ensure all sections are fully detailed with specific numbers and complete explanations. Take your time to provide thorough insights."""

        return prompt.format(
            price=price,
            monthly_mortgage=metrics.monthly_mortgage_payment,
            monthly_tax=metrics.monthly_property_tax,
            monthly_hoa=metrics.monthly_total_cost - metrics.monthly_mortgage_payment - metrics.monthly_property_tax,
            monthly_total=metrics.monthly_total_cost,
            total_principal=metrics.total_principal_30_years,
            total_interest=metrics.total_interest_30_years,
            total_cost_excl_principal=metrics.total_cost_30_years_excluding_principal,
        )
