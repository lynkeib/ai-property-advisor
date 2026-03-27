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
    """Call backend API and return response."""
    
    try:
        response = requests.post(API_ENDPOINT, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error(f"❌ Cannot connect to backend at {BACKEND_URL}")
        st.info("Make sure the backend is running: `python -m uvicorn backend.main:app --reload`")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"❌ API error: {str(e)}")
        return None


def display_metrics(metrics: dict) -> None:
    """Display financial metrics in a formatted way."""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Loan Amount", f"${metrics['loan_amount']:,.2f}")
        st.metric("Monthly Mortgage", f"${metrics['monthly_mortgage_payment']:,.2f}")
        st.metric("Monthly Property Tax", f"${metrics['monthly_property_tax']:,.2f}")
        st.metric("Total Monthly Cost", f"${metrics['monthly_total_cost']:,.2f}")
    
    with col2:
        st.metric("10-Year Buy Cost", f"${metrics['total_cost_10_years']:,.2f}")
        st.metric("10-Year Rent Cost", f"${metrics['total_rent_10_years']:,.2f}")
        st.metric("Buy vs Rent (10yr)", f"${metrics['buy_vs_rent_delta']:,.2f}")
        
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
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("Property Details")
        
        # Basic property info
        price = st.number_input(
            "Property Price ($)",
            min_value=1000.0,
            value=500000.0,
            step=10000.0
        )
        
        down_payment = st.number_input(
            "Down Payment ($)",
            min_value=0.0,
            value=100000.0,
            step=10000.0
        )
        
        interest_rate = st.slider(
            "Interest Rate (%)",
            min_value=0.0,
            max_value=15.0,
            value=6.5,
            step=0.1
        )
        
        st.markdown("---")
        st.subheader("Monthly Costs")
        
        hoa = st.number_input(
            "HOA Fees ($)",
            min_value=0.0,
            value=250.0,
            step=50.0
        )
        
        property_tax_rate = st.slider(
            "Property Tax Rate (annual %)",
            min_value=0.0,
            max_value=10.0,
            value=1.5,
            step=0.1
        ) / 100
        
        insurance = st.number_input(
            "Home Insurance ($)",
            min_value=0.0,
            value=150.0,
            step=10.0
        )
        
        st.markdown("---")
        
        rent_estimate = st.number_input(
            "Estimated Monthly Rent ($)",
            min_value=100.0,
            value=2500.0,
            step=100.0
        )
    
    # Main content area
    st.markdown("---")
    
    # Validate and analyze
    error = validate_inputs(price, down_payment, interest_rate, rent_estimate)
    
    if error:
        st.error(f"⚠️ {error}")
    else:
        col_analyze, col_clear = st.columns([4, 1])
        
        with col_analyze:
            if st.button("📊 Analyze Property", type="primary", use_container_width=True):
                with st.spinner("Analyzing property..."):
                    
                    request_data = {
                        "price": price,
                        "down_payment": down_payment,
                        "interest_rate": interest_rate,
                        "hoa": hoa,
                        "property_tax_rate": property_tax_rate,
                        "insurance": insurance,
                        "rent_estimate": rent_estimate
                    }
                    
                    result = call_backend_api(request_data)
                    
                    if result:
                        st.success("✅ Analysis complete!")
                        
                        # Display metrics section
                        st.markdown("## 📈 Financial Metrics")
                        display_metrics(result["metrics"])
                        
                        # Display AI analysis section
                        st.markdown("## 🤖 AI Investment Analysis")
                        st.markdown(result["ai_analysis"])
                        
                        # Store in session state for reference
                        st.session_state.last_analysis = result
    
    # Footer
    st.markdown("---")
    st.markdown(
        "Built with ❤️ using FastAPI + Streamlit | "
        "[GitHub](https://github.com) | "
        "[Docs](http://localhost:8000/docs)"
    )


if __name__ == "__main__":
    main()
