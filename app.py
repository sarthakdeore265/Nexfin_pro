import streamlit as st
import pandas as pd
import os
import plotly.express as px # Added for better charts
from datetime import datetime

from database import create_table
from expense_manager import add_expense, get_expenses
from ml_model import predict_spending

# 1. Page Configuration
st.set_page_config(
    page_title="SolarShield Expense Pro", 
    page_icon="💰", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize DB
if not os.path.exists("expenses.db"):
    create_table()

# --- SIDEBAR: Input Section ---
with st.sidebar:
    st.title("➕ Management")
    st.markdown("Enter your transaction details below.")
    
    with st.form("expense_form", clear_on_submit=True):
        date = st.date_input("Transaction Date", value=datetime.now())
        category = st.selectbox("Category", ["Food", "Travel", "Shopping", "Bills", "Business", "Other"])
        amount = st.number_input("Amount (₹)", min_value=0.0, step=10.0)
        description = st.text_input("Note/Description", placeholder="e.g. Lunch with team")
        
        submitted = st.form_submit_button("Add to Ledger")
        if submitted:
            if amount > 0:
                add_expense(str(date), category, amount, description)
                st.success("Transaction recorded!")
                st.rerun() # Refresh to update dashboard immediately
            else:
                st.error("Please enter an amount greater than 0.")

# --- MAIN PAGE: Dashboard ---
st.title("📊 Smart Expense Analytics")
st.markdown("---")

df = get_expenses()

if df is not None and not df.empty:
    # Ensure date conversion
    df['date'] = pd.to_datetime(df['date'])
    
    # 2. Key Metrics Row
    total_spent = df['amount'].sum()
    prediction = predict_spending(df)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Expenditure", f"₹{total_spent:,.2f}")
    col2.metric("Predicted Next Month", f"₹{prediction:,.2f}", delta=f"{((prediction-total_spent)/total_spent)*100:.1f}%" if total_spent != 0 else None, delta_color="inverse")
    col3.metric("Top Category", df.groupby("category")["amount"].sum().idxmax())

    st.markdown("### Visual Insights")
    
    # 3. Layout: Charts in Columns
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.subheader("Spending by Category")
        category_data = df.groupby("category")["amount"].sum().reset_index()
        # Using Plotly for interactive pie charts
        fig_pie = px.pie(category_data, values='amount', names='category', hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig_pie, use_container_width=True)

    with chart_col2:
        st.subheader("Monthly Trend")
        df['month'] = df['date'].dt.strftime('%b %Y')
        monthly = df.groupby('month')['amount'].sum().reset_index()
        st.line_chart(monthly.set_index('month'))

    # 4. Detailed Logs & Alerts
    st.markdown("---")
    tab1, tab2 = st.tabs(["📝 Transaction Logs", "⚠️ Budget Alerts"])
    
    with tab1:
        st.dataframe(df.sort_values(by="date", ascending=False), use_container_width=True)
    
    with tab2:
        max_cat_spend = df.groupby("category")["amount"].sum().max()
        if max_cat_spend > 5000:
            st.warning(f"**Budget Alert:** You've spent over ₹5,000 in your '{df.groupby('category')['amount'].sum().idxmax()}' category. Consider reviewing these costs.")
        else:
            st.info("All spending is within normal thresholds.")

else:
    st.info("No data available yet. Use the sidebar to add your first expense!")
