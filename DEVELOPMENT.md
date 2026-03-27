"""
Development guide for Property Copilot.

This guide helps developers understand and extend the codebase.
"""

# Architecture Overview

The application follows a clean, layered architecture:

```
Client (Streamlit)
       ↓
FastAPI Router (api/routes.py)
       ↓
    Services Layer
    ├─ Financial Calculator (deterministic math)
    └─ PropertyAnalyzer (OpenAI integration)
       ↓
    Data Models (Pydantic schemas)
```

## Key Components

### 1. Financial Calculator (`backend/services/financial_calculator.py`)

**Responsibility**: Deterministic financial calculations only

Key methods:
- `calculate_monthly_mortgage()`: Amortization formula for 30-year mortgage
- `calculate_metrics()`: Complete financial analysis

**Design notes**:
- No AI/randomness - always produces same output for same input
- Uses floating-point rounding to 2 decimal places for USD
- Handles edge cases (zero interest rate, zero loan amount)

**Testing**: See `tests/test_financial_calculator.py`

### 2. Property Analyzer (`backend/ai/analyzer.py`)

**Responsibility**: OpenAI API integration

Key methods:
- `analyze()`: Calls OpenAI gpt-3.5-turbo with financial metrics
- `_build_prompt()`: Constructs analysis prompt from metrics

**Design notes**:
- Encapsulates API key management
- Structured prompts for consistent output
- Error handling for API failures

### 3. FastAPI Routes (`backend/api/routes.py`)

**Responsibility**: HTTP endpoint handling

Key endpoints:
- `POST /api/analyze`: Main analysis endpoint
- `GET /api/health`: Health check

**Design notes**:
- Input validation via Pydantic schemas
- Orchestrates calculator → analyzer workflow
- Comprehensive error handling

### 4. Streamlit Frontend (`frontend/app.py`)

**Responsibility**: User interface

Key features:
- Sidebar for input collection
- Input validation before API call
- Formatted metric display
- AI analysis rendering

## Adding Features

### Example: Add a New Financial Metric

1. **Add to Pydantic model** (`backend/models/schemas.py`):
   ```python
   class FinancialMetrics(BaseModel):
       # ... existing fields ...
       new_metric: float
   ```

2. **Implement in calculator** (`backend/services/financial_calculator.py`):
   ```python
   new_metric = some_calculation()
   ```

3. **Update response** in `calculate_metrics()` return statement

4. **Display in frontend** (`frontend/app.py`):
   ```python
   st.metric("New Metric", f"${new_metric:,.2f}")
   ```

### Example: Change AI Model

In `backend/ai/analyzer.py`:
```python
response = openai.ChatCompletion.create(
    model="gpt-4",  # Change here
    # ... rest of config
)
```

## Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test

```bash
pytest tests/test_financial_calculator.py::TestFinancialCalculator::test_mortgage_payment_standard
```

### Check Coverage

```bash
pytest --cov=backend
```

## Code Quality

### Type Checking

```bash
mypy backend/
```

All code uses Python type hints. Add them to new functions:

```python
def calculate_something(price: float, rate: float) -> float:
    return price * rate
```

### Formatting

```bash
black backend/ frontend/
```

### Linting

```bash
flake8 backend/ frontend/ --max-line-length=99
```

## Common Tasks

### Add new endpoint

1. Create route in `backend/api/routes.py`
2. Add Pydantic schema in `backend/models/schemas.py`
3. Call service layer from route
4. Document with docstring

### Add new calculation

1. Add method to `FinancialCalculator`
2. Write test in `tests/test_financial_calculator.py`
3. Call from `calculate_metrics()` or new endpoint
4. Document the formula in docstring

### Debug API

Visit http://localhost:8000/docs for interactive API debugging

### Debug Frontend

Streamlit logs appear in terminal. Use `st.write()` for debugging:

```python
st.write("Debug info:", variable_name)
st.json(dict_variable)
```

## Environment Variables

Required:
- `OPENAI_API_KEY`: Your OpenAI API key

Optional:
- `BACKEND_HOST`: Backend host (default: 127.0.0.1)
- `BACKEND_PORT`: Backend port (default: 8000)
- `LOG_LEVEL`: Logging level (default: INFO)

## Deployment Notes

### Backend Deployment

For production, replace `uvicorn --reload` with:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend Deployment

Deploy Streamlit using Streamlit Cloud or Docker:

```bash
docker build -t property-copilot .
docker run -p 8501:8501 property-copilot
```

## Performance Considerations

1. **Financial calculations**: O(1) complexity - instant
2. **AI analysis**: 1-2 seconds for OpenAI API call
3. **Frontend**: Async API calls prevent UI blocking

## Security

1. API keys stored in environment variables (never in code)
2. CORS enabled for local dev (restrict in production)
3. Input validation on all endpoints
4. No sensitive data logged

## Future Improvements

- [ ] Add property image analysis
- [ ] Compare multiple properties
- [ ] Save analysis history
- [ ] Add property market data integration
- [ ] Implement caching for API responses
- [ ] Add multi-user support with auth
- [ ] Deploy to AWS/GCP/Azure
