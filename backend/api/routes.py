"""FastAPI routes for property analysis endpoint."""

import logging
from fastapi import APIRouter, HTTPException

from backend.models.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    GeminiRequest,
    GeminiResponse,
)
from backend.services.financial_calculator import FinancialCalculator
from backend.ai.analyzer import PropertyAnalyzer, GeminiAnalyzer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["analysis"])


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_property(request: AnalysisRequest) -> AnalysisResponse:
    """
    Analyze a property investment and return financial metrics + AI insights.
    
    Args:
        request: Property data including price, down payment, rates, etc.
    
    Returns:
        AnalysisResponse with calculated metrics and AI analysis
    
    Raises:
        HTTPException: If down payment exceeds price or API fails
    """
    
    try:
        # Input validation
        if request.down_payment > request.price:
            raise ValueError("Down payment cannot exceed property price")
        
        # Calculate financial metrics (deterministic)
        logger.info(f"Calculating metrics for property: ${request.price:,.0f}")
        metrics = FinancialCalculator.calculate_metrics(
            price=request.price,
            down_payment=request.down_payment,
            interest_rate=request.interest_rate,
            hoa=request.hoa,
            property_tax_rate=request.property_tax_rate,
            insurance=request.insurance,
            rent_estimate=request.rent_estimate
        )
        
        # Generate AI analysis
        logger.info("Requesting AI analysis from OpenAI")
        analyzer = PropertyAnalyzer()
        ai_analysis = analyzer.analyze(
            metrics=metrics,
            price=request.price,
            rent_estimate=request.rent_estimate
        )
        
        return AnalysisResponse(
            metrics=metrics,
            ai_analysis=ai_analysis
        )
    
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Analysis failed. Please try again.")


@router.post("/gemini", response_model=GeminiResponse)
async def gemini_generate(request: GeminiRequest) -> GeminiResponse:
    """Generate a text completion using Google Gemini API."""
    try:
        logger.info("Generating Gemini response")
        gemini = GeminiAnalyzer()
        output = gemini.generate(
            prompt=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )

        return GeminiResponse(output=output)

    except ValueError as e:
        logger.warning(f"Gemini request validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Gemini generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Gemini generation failed. Please try again.")


@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy"}
