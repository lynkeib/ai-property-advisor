"""Example API request for quick testing."""

import requests
import json

# Configuration
BACKEND_URL = "http://localhost:8000"
API_ENDPOINT = f"{BACKEND_URL}/api/analyze"

# Example property analysis request
example_request = {
    "price": 500000,
    "down_payment": 100000,
    "interest_rate": 6.5,
    "hoa": 250,
    "property_tax_rate": 0.015,
    "insurance": 150,
    "rent_estimate": 2500
}

print("=" * 60)
print("Property Copilot - Example API Request")
print("=" * 60)
print(f"\nEndpoint: {API_ENDPOINT}")
print(f"\nRequest Body:")
print(json.dumps(example_request, indent=2))
print("\n" + "=" * 60)

try:
    print("\nSending request...")
    response = requests.post(API_ENDPOINT, json=example_request, timeout=30)
    response.raise_for_status()
    
    result = response.json()
    
    print("\n✅ Success!\n")
    print("Response:")
    print(json.dumps(result, indent=2))
    
    # Extract key metrics
    metrics = result["metrics"]
    print("\n" + "=" * 60)
    print("Key Metrics:")
    print("=" * 60)
    print(f"Loan Amount:           ${metrics['loan_amount']:>12,.2f}")
    print(f"Monthly Mortgage:      ${metrics['monthly_mortgage_payment']:>12,.2f}")
    print(f"Monthly Property Tax:  ${metrics['monthly_property_tax']:>12,.2f}")
    print(f"Total Monthly Cost:    ${metrics['monthly_total_cost']:>12,.2f}")
    print(f"10-Year Buy Cost:      ${metrics['total_cost_10_years']:>12,.2f}")
    print(f"10-Year Rent Cost:     ${metrics['total_rent_10_years']:>12,.2f}")
    print(f"Buy vs Rent (10yr):    ${metrics['buy_vs_rent_delta']:>12,.2f}")
    print("=" * 60)
    print("\nAI Analysis:")
    print("-" * 60)
    print(result["ai_analysis"])
    print("=" * 60)
    
except requests.exceptions.ConnectionError:
    print("\n❌ Error: Cannot connect to backend")
    print(f"Make sure the backend is running at {BACKEND_URL}")
    print("\nTo start the backend, run:")
    print("  python -m uvicorn backend.main:app --reload")
except requests.exceptions.RequestException as e:
    print(f"\n❌ Error: {e}")
except Exception as e:
    print(f"\n❌ Unexpected error: {e}")
