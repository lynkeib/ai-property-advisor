# Quick Start Guide

Get Property Copilot running in 5 minutes.

## Prerequisites

- Python 3.11+
- Google Gemini API key (free tier available)

## Setup

### 1. Install Dependencies (1 min)

```bash
# Create & activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Configure API Key (1 min)

```bash
# Create environment file
cp .env.example .env

# Edit .env and add your Gemini API key
# Get one free at: https://aistudio.google.com/app/apikey
```

Example `.env`:
```
GEMINI_API_KEY=your-gemini-api-key-here
```

### 3. Start Backend (1 min)

```bash
# Terminal 1
python -m uvicorn backend.main:app --reload
```

You'll see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

✓ Backend is ready at `http://localhost:8000`

### 4. Start Frontend (1 min)

```bash
# Terminal 2 (with same venv activated)
streamlit run frontend/app.py
```

You'll see:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

✓ Frontend opens automatically

### 5. Try It Out! (1 min)

1. Open http://localhost:8501
2. Enter property details:
   - Price: $500,000
   - Down Payment: $100,000
   - Interest Rate: 6.5%
   - HOA: $250/month
   - Property Tax: 1.5% annual
   - Insurance: $150/month
   - Rent Estimate: $2,500/month
3. Click "Analyze Property"
4. View metrics and AI analysis

## Test via API

For quick API testing:

```bash
python example_request.py
```

Or use curl:

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

## Docs

- API Docs: http://localhost:8000/docs
- Full README: See [README.md](README.md)

## Troubleshooting

**Backend won't start?**
- Make sure port 8000 is free
- Try: `python -m uvicorn backend.main:app --reload --port 8001`

**Frontend can't reach backend?**
- Check backend is running
- Check CORS is enabled (it is by default)

**Gemini API error?**
- Verify API key in `.env`
- Check: https://status.generativeai.google

## Next Steps

1. Read [README.md](README.md) for full documentation
2. Check [example_request.py](example_request.py) for API examples
3. Explore code in `backend/` and `frontend/`
4. Run tests: `pytest`

---

That's it! You're running a full-stack AI application. 🚀
