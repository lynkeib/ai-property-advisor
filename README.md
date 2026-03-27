# Property Copilot

A production-quality MVP for AI-powered real estate investment analysis.

## Overview

Property Copilot combines **deterministic financial calculations** with **AI-generated insights** to help analyze real estate investments.

- **Backend**: Python 3.11, FastAPI, Pydantic
- **Frontend**: Streamlit
- **AI**: Google Gemini API (gemini-2.0-flash)

## Features

### Financial Calculator
- Monthly mortgage payment (30-year amortization)
- Monthly property tax, insurance, HOA
- Total monthly cost
- 10-year projections
- Buy vs rent comparison
- Break-even analysis

### AI Analysis
- Investment summary
- Key risks assessment
- Buy/rent/neutral recommendation
- Based on calculated metrics

## Project Structure

```
property-copilot/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py           # FastAPI endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   └── financial_calculator.py  # Deterministic math
│   ├── ai/
│   │   ├── __init__.py
│   │   └── analyzer.py         # Gemini integration
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic models
│   ├── main.py                 # FastAPI app
│   └── __init__.py
├── frontend/
│   └── app.py                  # Streamlit UI
├── requirements.txt
├── .env.example
└── README.md
```

## Setup & Installation

### 1. Clone and Install

```bash
cd ai-property-advisor
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Add your Gemini API key:

```
GEMINI_API_KEY=your-gemini-api-key-here
```

Get your API key at: https://aistudio.google.com/app/apikey

### 3. Run Backend

```bash
python -m uvicorn backend.main:app --reload
```

Backend runs at: `http://localhost:8000`
API docs: `http://localhost:8000/docs`

### 4. Run Frontend (separate terminal)

```bash
streamlit run frontend/app.py
```

Frontend opens at: `http://localhost:8501`

## API Usage

### Health Check

```bash
curl http://localhost:8000/api/health
```

Response:
```json
{"status": "healthy"}
```

### Analysis Endpoint

**Endpoint**: `POST /api/analyze`

**Request Example**:
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "price": 500000,
    "down_payment": 100000,
    "interest_rate": 6.5,
    "hoa": 250,
    "property_tax_rate": 0.015,
    "insurance": 150,
    "rent_estimate": 2500
  }'
```

**Response Example**:
```json
{
  "metrics": {
    "loan_amount": 400000.0,
    "monthly_mortgage_payment": 2398.20,
    "monthly_property_tax": 625.0,
    "monthly_total_cost": 3423.20,
    "total_cost_10_years": 410784.0,
    "total_rent_10_years": 300000.0,
    "buy_vs_rent_delta": -110784.0,
    "break_even_months": null
  },
  "ai_analysis": "Investment Summary: This property is financially attractive for long-term ownership...\n\nKey Risks:\n- Interest rate sensitivity...\n- Market volatility...\n\nRecommendation: BUY"
}
```

## Frontend Use

1. Enter property details in the sidebar
2. Click "Analyze Property"
3. View financial metrics and AI analysis

## Code Quality

- ✅ Type hints throughout (Pydantic, Python typing)
- ✅ Modular design (clear separation of concerns)
- ✅ Environment variables for secrets
- ✅ Error handling and validation
- ✅ Logging for debugging
- ✅ Clean code structure

## Notes

- Financial calculations are 100% deterministic (no AI)
- AI analysis uses Google Gemini gemini-2.0-flash API
- CORS enabled for local frontend development
- All monetary values in USD
- Interest rates as percentages (e.g., 6.5 for 6.5%)

## Testing

```bash
# Run tests
pytest

# Type checking
mypy backend/

# Code formatting
black backend/ frontend/

# Linting
flake8 backend/ frontend/
```

## Next Steps

- Add unit tests for financial calculator
- Implement database for storing analyses
- Add user authentication
- Deploy to production (e.g., AWS, Heroku)
- Add property image/description inputs
- Compare multiple properties

## License

MIT
