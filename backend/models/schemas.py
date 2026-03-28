"""Pydantic schemas for request/response validation."""

from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    """Request schema for property analysis."""
    
    price: float = Field(..., gt=0, description="Property price in USD")
    down_payment: float = Field(..., ge=0, description="Down payment in USD")
    interest_rate: float = Field(..., ge=0, le=15, description="Annual interest rate (0-15)")
    hoa: float = Field(default=0, ge=0, description="Monthly HOA fees in USD")
    property_tax_rate: float = Field(default=0.01, ge=0, le=0.1, description="Annual property tax rate")
    insurance: float = Field(default=0, ge=0, description="Monthly insurance in USD")
    model: str = Field(default="gemini-1.5-flash", description="AI model to use for analysis")
    
    class Config:
        json_schema_extra = {
            "example": {
                "price": 500000,
                "down_payment": 100000,
                "interest_rate": 6.5,
                "hoa": 250,
                "property_tax_rate": 0.015,
                "insurance": 150,
                "model": "gemini-1.5-flash"
            }
        }


class FinancialMetrics(BaseModel):
    """Financial metrics computed by calculator."""
    
    loan_amount: float
    monthly_mortgage_payment: float
    monthly_property_tax: float
    monthly_total_cost: float
    total_principal_30_years: float
    total_interest_30_years: float
    total_cost_30_years_excluding_principal: float


class AnalysisResponse(BaseModel):
    """Response schema for analysis endpoint."""
    
    metrics: FinancialMetrics
    ai_analysis: str


class ModelsResponse(BaseModel):
    """Schema for available models response."""
    generate_content_models: list[str]
    embed_content_models: list[str]
