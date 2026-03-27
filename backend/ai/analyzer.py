"""OpenAI integration for property analysis insights."""

import logging
import os
from typing import Optional

import openai
from google import generativeai as genai

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
        model: str = "gemini-2.0-flash",
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
        rent_estimate: float,
        model: str = "gemini-1.5-flash"
    ) -> str:
        """
        Generate AI analysis of property investment based on calculated metrics.
        
        Returns investment summary, key risks, and recommendation.
        """
        
        prompt = self._build_prompt(metrics, price, rent_estimate)
        
        try:
            analysis = self.generate(
                prompt=prompt,
                model=model,
                max_tokens=2048,
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
        rent_estimate: float
    ) -> str:
        """Build the prompt for Gemini analysis."""
        
        return f"""Based on these real estate investment metrics, provide a comprehensive analysis of this property investment opportunity:

Property Details:
- Property Price: ${price:,.0f}
- Monthly Mortgage Payment: ${metrics.monthly_mortgage_payment:,.2f}
- Monthly Property Tax: ${metrics.monthly_property_tax:,.2f}
- Monthly HOA/Insurance: ${metrics.monthly_total_cost - metrics.monthly_mortgage_payment - metrics.monthly_property_tax:,.2f}
- Total Monthly Ownership Cost: ${metrics.monthly_total_cost:,.2f}
- Estimated Monthly Rent: ${rent_estimate:,.2f}

10-Year Financial Projections:
- Total Cost of Buying: ${metrics.total_cost_10_years:,.2f}
- Total Cost of Renting: ${metrics.total_rent_10_years:,.2f}
- Buy vs Rent Savings/Loss: ${metrics.buy_vs_rent_delta:,.2f}
{"- Break-even Period: " + f"{metrics.break_even_months:.1f} months" if metrics.break_even_months else "- Break-even: Rent appears cheaper long-term"}

Please provide a detailed analysis covering:

1. **Investment Summary**: Comprehensive overview of the financial opportunity
2. **Cash Flow Analysis**: Monthly cash flow, ROI calculations, and long-term projections
3. **Market Considerations**: Current market conditions and property appreciation potential
4. **Risk Assessment**: Key risks including interest rate changes, market fluctuations, and property-specific concerns
5. **Tax Implications**: Potential tax benefits and deductions
6. **Recommendation**: Clear buy/rent/hold recommendation with reasoning

Provide specific numbers, calculations, and practical insights. Be thorough but practical."""


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
