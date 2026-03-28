"""Streamlit frontend for property-copilot."""

import logging
import requests
import streamlit as st
from typing import Optional

# Configure page
st.set_page_config(
    page_title="Property Copilot",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Backend API configuration
BACKEND_URL = "http://localhost:8000"
API_ENDPOINT = f"{BACKEND_URL}/api/analyze"
METRICS_ENDPOINT = f"{BACKEND_URL}/api/metrics"
MODELS_ENDPOINT = f"{BACKEND_URL}/api/models"

# Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)


def validate_inputs(
    price: float,
    down_payment: float,
    interest_rate: float,
    rent_estimate: float
) -> Optional[str]:
    """Validate user inputs and return error message if invalid."""
    
    if price <= 0:
        return "Property price must be greater than 0"
    if down_payment < 0 or down_payment > price:
        return "Down payment must be between 0 and property price"
    if interest_rate < 0 or interest_rate > 15:
        return "Interest rate must be between 0% and 15%"
    if rent_estimate <= 0:
        return "Rent estimate must be greater than 0"
    
    return None


def call_backend_api(data: dict) -> Optional[dict]:
    """Call backend analyze API and return response."""
    
    try:
        response = requests.post(API_ENDPOINT, json=data, timeout=60)
        if response.status_code != 200:
            detail = ""
            try:
                detail = response.json()
            except Exception:
                detail = response.text
            st.error(f"❌ API error {response.status_code}: {detail}")
            st.write(f"Request body: {data}")
            return None
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error(f"❌ Cannot connect to backend at {BACKEND_URL}")
        st.info("Make sure the backend is running: `python -m uvicorn backend.main:app --reload`")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"❌ API error: {str(e)}")
        return None


def call_metrics_api(data: dict) -> Optional[dict]:
    """Call backend metrics API and return response."""
    try:
        response = requests.post(METRICS_ENDPOINT, json=data, timeout=30)
        if response.status_code != 200:
            detail = ""
            try:
                detail = response.json()
            except Exception:
                detail = response.text
            st.error(f"❌ Metrics API error {response.status_code}: {detail}")
            return None
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error(f"❌ Cannot connect to backend at {BACKEND_URL}")
        st.info("Make sure the backend is running: `python -m uvicorn backend.main:app --reload`")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Metrics API error: {str(e)}")
        return None


def fetch_available_models() -> Optional[dict]:
    """Fetch available AI models from backend."""
    try:
        response = requests.get(MODELS_ENDPOINT, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            st.warning(f"⚠️ Could not fetch models (status {response.status_code})")
            return None
    except Exception as e:
        st.warning(f"⚠️ Could not fetch models: {str(e)}")
        return None


def format_currency(amount: float) -> str:
    """Formats a float as a USD currency string."""
    return f"${amount:,.2f}"


def parse_currency_input(value: str, default: float = 0.0) -> float:
    """Parse a currency string into a float.

    Accepts values like 500000, 500,000, $500,000, 500000.00.
    """
    if isinstance(value, (int, float)):
        return float(value)

    try:
        sanitized = str(value).strip().replace("$", "").replace(",", "")
        if sanitized == "":
            return default
        return float(sanitized)
    except ValueError:
        return default


def refresh_currency_field(field_name: str, default: float = 0.0) -> None:
    """Parse the raw text input and update with formatted currency text."""
    raw_value = st.session_state.get(field_name, "")
    parsed = parse_currency_input(raw_value, default=default)
    st.session_state[field_name] = format_currency(parsed)


def display_metrics(metrics: dict) -> None:
    """Display financial metrics in a formatted way."""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Loan Amount", format_currency(metrics['loan_amount']))
        st.metric("Monthly Mortgage", format_currency(metrics['monthly_mortgage_payment']))
        st.metric("Monthly Property Tax", format_currency(metrics['monthly_property_tax']))
        st.metric("Total Monthly Cost", format_currency(metrics['monthly_total_cost']))
    
    with col2:
        st.metric("10-Year Cost (excl. principal)", format_currency(metrics['total_cost_10_years']))
        st.metric("10-Year Rent Cost", format_currency(metrics['total_rent_10_years']))
        st.metric("Buy vs Rent (10yr)", format_currency(metrics['buy_vs_rent_delta']))
        st.metric("Total Principal Paid (10yr)", format_currency(metrics.get('total_principal_paid_10_years', 0)))
        st.metric("Total Interest Paid (10yr)", format_currency(metrics.get('total_interest_paid_10_years', 0)))
        
        break_even = metrics.get('break_even_months')
        if break_even:
            st.metric("Break-Even Months", f"{break_even:.1f}")
        else:
            st.metric("Break-Even", "Rent is cheaper")


def main():
    """Main Streamlit application."""
    
    # Header
    st.title("🏡 Property Copilot")
    st.markdown("AI-powered real estate investment analysis")
    
    # Fetch available models
    models_data = fetch_available_models()
    available_models = []
    if models_data and 'generate_content_models' in models_data:
        available_models = models_data['generate_content_models']
    else:
        # Fallback to default models if API fails
        available_models = ["gemini-1.5-flash", "gemini-1.5-pro"]
    
    # Sidebar for inputs
    # Initialize session state to avoid widget key-value conflict warnings
    if "price_input" not in st.session_state:
        st.session_state.price_input = format_currency(500000.0)
    if "down_payment_input" not in st.session_state:
        st.session_state.down_payment_input = format_currency(100000.0)
    if "hoa_input" not in st.session_state:
        st.session_state.hoa_input = format_currency(250.0)
    if "insurance_input" not in st.session_state:
        st.session_state.insurance_input = format_currency(150.0)
    if "rent_estimate_input" not in st.session_state:
        st.session_state.rent_estimate_input = format_currency(2500.0)

    with st.sidebar:
        st.header("Property Details")
        
        # Basic property info with formatted dollar text input
        st.text_input(
            "Property Price ($)",
            key="price_input",
            on_change=refresh_currency_field,
            args=("price_input", 500000.0),
        )
        price = parse_currency_input(st.session_state.price_input, default=500000.0)
        
        st.text_input(
            "Down Payment ($)",
            key="down_payment_input",
            on_change=refresh_currency_field,
            args=("down_payment_input", 100000.0),
        )
        down_payment = parse_currency_input(st.session_state.down_payment_input, default=100000.0)
        
        # Interest rate numeric input (as requested)
        interest_rate = st.number_input(
            "Interest Rate (%)",
            min_value=0.0,
            max_value=15.0,
            value=6.5,
            step=0.01,
            format="%.2f"
        )
        
        st.markdown("---")
        st.subheader("Monthly Costs")
        
        st.text_input(
            "HOA Fees ($/month)",
            key="hoa_input",
            on_change=refresh_currency_field,
            args=("hoa_input", 250.0),
        )
        hoa = parse_currency_input(st.session_state.hoa_input, default=250.0)
        
        property_tax_rate_pct = st.number_input(
            "Property Tax Rate (annual %)",
            min_value=0.0,
            max_value=10.0,
            value=1.5,
            step=0.01,
            format="%.2f"
        )
        property_tax_rate = property_tax_rate_pct / 100
        
        st.text_input(
            "Home Insurance ($/month)",
            key="insurance_input",
            on_change=refresh_currency_field,
            args=("insurance_input", 150.0),
        )
        insurance = parse_currency_input(st.session_state.insurance_input, default=150.0)
        
        st.markdown("---")
        
        st.text_input(
            "Estimated Monthly Rent ($)",
            key="rent_estimate_input",
            on_change=refresh_currency_field,
            args=("rent_estimate_input", 2500.0),
        )
        rent_estimate = parse_currency_input(st.session_state.rent_estimate_input, default=2500.0)
        
        st.markdown("---")
        st.subheader("AI Analysis Settings")
        
        selected_model = st.selectbox(
            "AI Model",
            options=available_models,
            index=0 if available_models else 0,
            help="Choose the AI model for property analysis"
        )

    
    # Main content area
    st.markdown("---")
    
    # Validate and analyze
    error = validate_inputs(price, down_payment, interest_rate, rent_estimate)

    if error:
        st.error(f"⚠️ {error}")
    else:
        request_data_base = {
            "price": price,
            "down_payment": down_payment,
            "interest_rate": interest_rate,
            "hoa": hoa,
            "property_tax_rate": property_tax_rate,
            "insurance": insurance,
            "rent_estimate": rent_estimate,
            "model": selected_model
        }

        # Show financial metrics immediately (no AI needed)
        metrics_result = call_metrics_api(request_data_base)
        if metrics_result:
            st.markdown("## 📈 Financial Metrics")
            display_metrics(metrics_result)
        else:
            st.warning("⚠️ Could not calculate metrics yet. Check your input or backend availability.")

        if "ai_analysis" not in st.session_state:
            st.session_state.ai_analysis = None

        col_analyze, col_clear = st.columns([4, 1])

        with col_analyze:
            if st.button("📊 Analyze Property", type="primary", use_container_width=True):
                with st.spinner("Analyzing property..."):
                    result = call_backend_api(request_data_base)
                    if result:
                        st.success("✅ Analysis complete!")
                        st.session_state.ai_analysis = result.get("ai_analysis")
                        st.session_state.metrics = result.get("metrics")

        # Show AI analysis after user clicks Analyze
        if st.session_state.ai_analysis:
            st.markdown("## 🤖 AI Investment Analysis")
            st.markdown(st.session_state.ai_analysis)

    # Footer
    st.markdown("---")
    st.markdown(
        "Built with ❤️ using FastAPI + Streamlit | "
        "[GitHub](https://github.com) | "
        "[Docs](http://localhost:8000/docs)"
    )


if __name__ == "__main__":
    main()
