import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")

st.set_page_config(page_title="AI Bank Analyzer", page_icon="🏦", layout="wide")

# Custom CSS for Vault & Vignette: Illustrated Neo-Vintage theme
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800&family=JetBrains+Mono:wght@500&family=Literata:wght@400;700&display=swap');

    .stApp {
        background-color: #fff8f5;
        color: #291806;
        font-family: 'Literata', serif;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Bricolage Grotesque', sans-serif !important;
        color: #1a1a1a !important;
        letter-spacing: -0.02em;
    }
    
    h1 { font-weight: 800 !important; }
    h2, h3 { font-weight: 700 !important; }

    /* Comic Panel Style for Metric Cards */
    .comic-panel {
        background-color: #fff1e7;
        border: 3px solid #1a1a1a;
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        box-shadow: 4px 4px 0px #d4af37; /* Hard offset shadow */
        margin-bottom: 24px;
        transition: transform 0.1s, box-shadow 0.1s;
    }
    
    .comic-panel:hover {
        transform: translate(2px, 2px);
        box-shadow: 2px 2px 0px #d4af37;
    }

    .metric-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #4d4635;
        margin-bottom: 8px;
    }

    .metric-value {
        font-family: 'Bricolage Grotesque', sans-serif;
        font-size: 24px;
        font-weight: 800;
        color: #1a1a1a;
    }

    /* Buttons */
    .stButton>button {
        background-color: #d4af37 !important;
        color: #1a1a1a !important;
        border: 3px solid #1a1a1a !important;
        border-radius: 8px !important;
        font-family: 'Bricolage Grotesque', sans-serif !important;
        font-weight: 700 !important;
        box-shadow: 4px 4px 0px #1a1a1a !important;
        transition: transform 0.1s, box-shadow 0.1s !important;
    }

    .stButton>button:hover {
        transform: translate(2px, 2px) !important;
        box-shadow: 2px 2px 0px #1a1a1a !important;
    }
    
    .stButton>button:active {
        transform: translate(4px, 4px) !important;
        box-shadow: 0px 0px 0px #1a1a1a !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border: 2px solid transparent;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-family: 'Bricolage Grotesque', sans-serif;
        font-weight: 700;
        color: #4d4635;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #ffeada;
        border: 2px solid #1a1a1a;
        border-bottom: none;
        color: #1a1a1a;
    }
    
    /* Insights Alert Box (Bubble style) */
    .insight-bubble {
        background-color: #e4e4cc;
        border: 2px dashed #1a1a1a;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        font-family: 'Literata', serif;
        font-size: 16px;
        color: #1b1d0e;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏦 Vault & Vignette Ledger")

if 'session_id' not in st.session_state:
    st.session_state['session_id'] = None

with st.sidebar:
    st.markdown("### 📜 The Statement Deposit")
    uploaded_file = st.file_uploader("Drop your CSV or Excel ledger here", type=["csv", "xls", "xlsx"])
    if uploaded_file is not None:
        if st.button("Analyze Ledger"):
            with st.spinner("Deciphering transactions..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/octet-stream")}
                response = requests.post(f"{API_BASE_URL}/upload", files=files)
                if response.status_code == 200:
                    st.session_state['session_id'] = response.json()["session_id"]
                    st.success(f"Success! Detected Bank: {response.json()['bank_name']}")
                else:
                    st.error(f"Error: {response.text}")

if st.session_state['session_id']:
    try:
        analytics = requests.get(f"{API_BASE_URL}/analyze/{st.session_state['session_id']}").json()
        txns = requests.get(f"{API_BASE_URL}/transactions/{st.session_state['session_id']}").json()
    except Exception as e:
        st.error("Failed to fetch analytics from backend. Ensure FastAPI server is running.")
        st.stop()

    summary = analytics["summary"]

    tab_dash, tab_txns, tab_insights = st.tabs(["📊 The Dashboard", "🧾 Ledger Entries", "💡 Vignette Insights"])

    with tab_dash:
        # Metric Cards
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"<div class='comic-panel'><div class='metric-title'>Total Income</div><div class='metric-value'>₹{summary['total_income']:,.2f}</div></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='comic-panel'><div class='metric-title'>Total Expense</div><div class='metric-value'>₹{summary['total_expense']:,.2f}</div></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='comic-panel'><div class='metric-title'>Net Savings</div><div class='metric-value'>₹{summary['net_savings']:,.2f}</div></div>", unsafe_allow_html=True)
        with col4:
            savings_rate_str = "--" if summary['savings_rate'] < 0 else f"{summary['savings_rate']}%"
            st.markdown(f"<div class='comic-panel'><div class='metric-title'>Savings Rate</div><div class='metric-value'>{savings_rate_str}</div></div>", unsafe_allow_html=True)
            
        st.markdown("---")

        # Per-category color map matching analytics.xlsx
        category_colors = {
            'Food': '#d4af37',
            'Rent': '#98ff98',
            'Travel': '#c41e3a',
            'Others': '#e9c349',
            'Grocery': '#77dc7a',
            'Donation': '#ffdad6',
            'Shopping': '#90f691',
            'local commute': '#ffe088',
            'Coffee': '#d3b88c',
            'Utilities': '#ffffff',
            'Entertainment': '#f0c070',
            'Personal': '#c8a2c8',
            'EMI/Loans': '#a0d2db',
            'Self-Transfers': '#b0c4de',
            'Investments': '#8fbc8f',
            'Salary/Income': '#ffd700',
        }
        
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.markdown("### Spending by Category")
            cat_df = pd.DataFrame(analytics["category_breakdown"])
            if not cat_df.empty:
                fig = px.pie(cat_df, values='amount', names='category', hole=0.4,
                             color='category',
                             color_discrete_map=category_colors)
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family="Literata", color='#1a1a1a'))
                # Add borders to pie slices
                fig.update_traces(marker=dict(line=dict(color='#1a1a1a', width=2)))
                st.plotly_chart(fig, use_container_width=True)

        with col_chart2:
            st.markdown("### Daily Spending Trend")
            daily_df = pd.DataFrame(analytics["daily_spending"])
            if not daily_df.empty:
                fig2 = px.area(daily_df, x='date', y='amount', 
                               color_discrete_sequence=['#c0c0c0'])
                fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family="Literata", color='#1a1a1a'))
                # Add thick black line on top of grey fill
                fig2.update_traces(line=dict(color='#1a1a1a', width=3))
                st.plotly_chart(fig2, use_container_width=True)

        st.markdown("### Avoidable vs Unavoidable Spending")
        av_split = analytics["avoidable_split"]
        av_df = pd.DataFrame({
            "Type": ["Avoidable", "Unavoidable"],
            "Amount": [av_split["avoidable"], av_split["unavoidable"]]
        })
        fig3 = px.bar(av_df, x="Amount", y="Type", color="Type", orientation='h',
                      color_discrete_map={"Avoidable": "#ffdad6", "Unavoidable": "#98ff98"})
        fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family="Literata", color='#1a1a1a'), showlegend=False)
        fig3.update_traces(marker=dict(line=dict(color='#1a1a1a', width=2)))
        st.plotly_chart(fig3, use_container_width=True)

    with tab_txns:
        st.markdown("### Detailed Transaction Ledger")
        df_txns = pd.DataFrame(txns)
        if not df_txns.empty:
            df_txns = df_txns[['date', 'description', 'amount', 'type', 'category', 'category_confidence', 'is_anomaly', 'is_avoidable']]
            
            # Export Button
            csv = df_txns.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Ledger to CSV",
                data=csv,
                file_name="vault_ledger_export.csv",
                mime="text/csv",
            )
            
            # Use Streamlit's native dataframe which will pick up font styles from config
            st.dataframe(df_txns, use_container_width=True, height=600)

    with tab_insights:
        st.markdown("### Automated Ledger Insights")
        for insight in analytics["insights"]:
            st.markdown(f"<div class='insight-bubble'><strong>{insight['emoji']}</strong> {insight['text']}</div>", unsafe_allow_html=True)

else:
    st.info("👈 Upload a bank ledger from the sidebar to begin your journey into the vault.")
