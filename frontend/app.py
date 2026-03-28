"""Streamlit frontend for property-copilot."""

import logging
import calendar
import re
from datetime import date
import pandas as pd
import requests
import streamlit as st
from typing import Optional

try:
    import plotly.graph_objects as go
except Exception:
    go = None

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
    .amort-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 10px;
        padding: 12px 14px;
        margin: 6px 0;
    }
    .amort-card-label {
        font-size: 0.9rem;
        opacity: 0.8;
        margin-bottom: 6px;
    }
    .amort-card-value {
        font-size: clamp(1.4rem, 2.6vw, 2rem);
        font-weight: 700;
        line-height: 1.15;
        white-space: normal;
        overflow-wrap: anywhere;
        word-break: break-word;
    }
</style>
""", unsafe_allow_html=True)


def validate_inputs(
    price: float,
    down_payment: float,
    interest_rate: float,
    zip_code: str,
) -> Optional[str]:
    """Validate user inputs and return error message if invalid."""
    
    if price <= 0:
        return "Property price must be greater than 0"
    if down_payment < 0 or down_payment > price:
        return "Down payment must be between 0 and property price"
    if interest_rate < 0 or interest_rate > 15:
        return "Interest rate must be between 0% and 15%"
    if not re.fullmatch(r"\d{5}(?:-\d{4})?", zip_code.strip()):
        return "ZIP code must be 5 digits or ZIP+4 (e.g., 94110 or 94110-1234)"
    
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

    def render_value_card(label: str, value: str) -> None:
        st.markdown(
            f"""
            <div class="amort-card">
                <div class="amort-card-label">{label}</div>
                <div class="amort-card-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    col1, col2 = st.columns(2)
    
    with col1:
        render_value_card("Loan Amount", format_currency(metrics['loan_amount']))
        render_value_card("Monthly Mortgage", format_currency(metrics['monthly_mortgage_payment']))
        render_value_card("Monthly Property Tax", format_currency(metrics['monthly_property_tax']))
        render_value_card("Total Monthly Cost", format_currency(metrics['monthly_total_cost']))
    
    with col2:
        render_value_card("30-Year Principal", format_currency(metrics['total_principal_30_years']))
        render_value_card("30-Year Interest", format_currency(metrics['total_interest_30_years']))
        render_value_card(
            "30-Year Total Cost (excl. principal)",
            format_currency(metrics['total_cost_30_years_excluding_principal'])
        )


def add_years(start_date: date, years: int) -> date:
    """Add years to a date while handling leap-year edge cases."""
    try:
        return start_date.replace(year=start_date.year + years)
    except ValueError:
        return start_date.replace(month=2, day=28, year=start_date.year + years)


def add_months(start_date: date, months: int) -> date:
    """Add months to a date while keeping day-in-month valid."""
    month_index = (start_date.month - 1) + months
    year = start_date.year + (month_index // 12)
    month = (month_index % 12) + 1
    last_day = calendar.monthrange(year, month)[1]
    day = min(start_date.day, last_day)
    return date(year, month, day)


def build_amortization_schedule(
    loan_amount: float,
    annual_interest_rate: float,
    monthly_payment: float,
    total_months: int = 360,
) -> list[dict]:
    """Build cumulative amortization values for each month."""
    monthly_rate = annual_interest_rate / 100 / 12
    balance = loan_amount
    cumulative_principal = 0.0
    cumulative_interest = 0.0

    schedule = [{
        "month": 0,
        "principal_paid": 0.0,
        "interest_paid": 0.0,
        "loan_balance": round(balance, 2),
    }]

    for month in range(1, total_months + 1):
        if balance <= 0:
            schedule.append({
                "month": month,
                "principal_paid": round(cumulative_principal, 2),
                "interest_paid": round(cumulative_interest, 2),
                "loan_balance": 0.0,
            })
            continue

        if monthly_rate == 0:
            interest_payment = 0.0
            principal_payment = min(balance, monthly_payment)
        else:
            interest_payment = round(balance * monthly_rate, 2)
            principal_payment = round(monthly_payment - interest_payment, 2)
            if principal_payment > balance:
                principal_payment = balance
            if principal_payment < 0:
                principal_payment = 0.0

        balance = max(0.0, round(balance - principal_payment, 2))
        cumulative_principal = round(cumulative_principal + principal_payment, 2)
        cumulative_interest = round(cumulative_interest + interest_payment, 2)

        schedule.append({
            "month": month,
            "principal_paid": cumulative_principal,
            "interest_paid": cumulative_interest,
            "loan_balance": balance,
        })

    return schedule


def display_amortization_summary(metrics: dict, loan_start_date: date, annual_interest_rate: float) -> None:
    """Display amortization summary with monthly interactive chart."""
    payoff_date = add_years(loan_start_date, 30)
    total_cost_of_loan = metrics['total_principal_30_years'] + metrics['total_interest_30_years']
    schedule = build_amortization_schedule(
        loan_amount=metrics['loan_amount'],
        annual_interest_rate=annual_interest_rate,
        monthly_payment=metrics['monthly_mortgage_payment'],
        total_months=360,
    )

    monthly_points = []
    for point in schedule:
        month_idx = point["month"]
        monthly_points.append({
            "Date": add_months(loan_start_date, month_idx),
            "Principal paid": point["principal_paid"],
            "Interest paid": point["interest_paid"],
            "Loan balance": point["loan_balance"],
        })

    chart_df = pd.DataFrame(monthly_points)

    st.markdown("### Amortization for Mortgage Loan")
    st.caption(
        "Interactive chart: hover to inspect values, zoom/pan to explore, and toggle lines in legend."
    )

    top_row_col1, top_row_col2 = st.columns(2)
    with top_row_col1:
        st.markdown(
            f"""
            <div class="amort-card">
                <div class="amort-card-label">Loan amount</div>
                <div class="amort-card-value">{format_currency(metrics['loan_amount'])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with top_row_col2:
        st.markdown(
            f"""
            <div class="amort-card">
                <div class="amort-card-label">Total interest paid</div>
                <div class="amort-card-value">{format_currency(metrics['total_interest_30_years'])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    bottom_row_col1, bottom_row_col2 = st.columns(2)
    with bottom_row_col1:
        st.markdown(
            f"""
            <div class="amort-card">
                <div class="amort-card-label">Total cost of loan</div>
                <div class="amort-card-value">{format_currency(total_cost_of_loan)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with bottom_row_col2:
        st.markdown(
            f"""
            <div class="amort-card">
                <div class="amort-card-label">Payoff date</div>
                <div class="amort-card-value">{payoff_date.strftime('%b %Y')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    x_dates = chart_df["Date"].tolist()
    principal_series = chart_df["Principal paid"].tolist()
    interest_series = chart_df["Interest paid"].tolist()
    balance_series = chart_df["Loan balance"].tolist()

    if go is None:
        st.warning(
            "Interactive chart requires plotly. Install with: python -m pip install plotly==5.24.1"
        )
        st.line_chart(chart_df, height=420)
        return

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x_dates,
            y=principal_series,
            mode="lines",
            name="Principal paid",
            line=dict(color="#4c9aff", width=3),
            hovertemplate="%{x|%b %Y}<br>Principal paid: $%{y:,.2f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x_dates,
            y=interest_series,
            mode="lines",
            name="Interest paid",
            line=dict(color="#67c587", width=3),
            hovertemplate="%{x|%b %Y}<br>Interest paid: $%{y:,.2f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x_dates,
            y=balance_series,
            mode="lines",
            name="Loan balance",
            line=dict(color="#1545a6", width=3),
            hovertemplate="%{x|%b %Y}<br>Loan balance: $%{y:,.2f}<extra></extra>",
        )
    )

    fig.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=10, b=10),
        hovermode="x unified",
        xaxis_title="Year",
        yaxis_title="Amount (USD)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    fig.update_yaxes(tickprefix="$", separatethousands=True)

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": True, "scrollZoom": True},
    )


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
    if "zip_code_input" not in st.session_state:
        st.session_state.zip_code_input = "94110"

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

        zip_code = st.text_input(
            "ZIP Code",
            key="zip_code_input",
            help="Used in AI analysis context",
        ).strip()
        
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
        st.subheader("AI Analysis Settings")
        
        selected_model = st.selectbox(
            "AI Model",
            options=available_models,
            index=0 if available_models else 0,
            help="Choose the AI model for property analysis"
        )
        selected_analysis_language = st.selectbox(
            "Analysis Language",
            options=[
                "English",
                "Spanish",
                "Chinese (Simplified)",
                "Chinese (Traditional)",
                "Japanese",
                "Korean",
                "French",
                "German",
                "Portuguese",
            ],
            index=0,
            help="Choose the language for AI analysis output",
        )

    
    # Main content area
    st.markdown("---")
    
    # Validate and analyze
    error = validate_inputs(price, down_payment, interest_rate, zip_code)

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
            "zip_code": zip_code,
            "model": selected_model,
            "analysis_language": selected_analysis_language,
        }

        # Show financial metrics immediately (no AI needed)
        metrics_result = call_metrics_api(request_data_base)

        if "ai_analysis" not in st.session_state:
            st.session_state.ai_analysis = None

        payment_tab, amortization_tab = st.tabs(["Payment breakdown", "Amortization"])

        with payment_tab:
            if metrics_result:
                st.markdown("## 📈 Financial Metrics")
                display_metrics(metrics_result)
            else:
                st.warning("⚠️ Could not calculate metrics yet. Check your input or backend availability.")

            col_analyze, col_clear = st.columns([4, 1])

            with col_analyze:
                if st.button("🤖 Generate AI Analysis", type="primary", use_container_width=True):
                    with st.spinner("Generating AI analysis..."):
                        result = call_backend_api(request_data_base)
                        if result:
                            st.success("✅ AI analysis complete!")
                            st.session_state.ai_analysis = result.get("ai_analysis")
                            st.session_state.metrics = result.get("metrics")

            # Show AI analysis after user clicks Analyze
            if st.session_state.ai_analysis:
                st.markdown("## 🤖 AI Investment Analysis")
                st.markdown(st.session_state.ai_analysis)

        with amortization_tab:
            st.markdown("## 🧮 Amortization")
            loan_start_date = st.date_input("Loan start date", value=date.today(), key="loan_start_date")
            if metrics_result:
                display_amortization_summary(metrics_result, loan_start_date, interest_rate)
            else:
                st.warning("⚠️ Amortization summary is unavailable until metrics can be calculated.")

    # Footer
    st.markdown("---")
    st.markdown(
        "Built with ❤️ using FastAPI + Streamlit | "
        "[GitHub](https://github.com) | "
        "[Docs](http://localhost:8000/docs)"
    )


if __name__ == "__main__":
    main()
