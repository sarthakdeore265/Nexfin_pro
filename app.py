import streamlit as st
import pandas as pd
import os

from database import create_table
from expense_manager import add_expense, get_expenses
from ml_model import predict_spending

# ✅ Page config (ONLY once and at top)
st.set_page_config(
    page_title="Smart Expense Analyzer",
    page_icon="💰",
    layout="wide"
)

# ✅ Initialize DB
if not os.path.exists("expenses.db"):
    create_table()

# ✅ Sidebar
st.sidebar.title("💸 Expense App")
menu = ["Dashboard", "Add Expense", "Insights"]
choice = st.sidebar.selectbox("Menu", menu)

st.title("💰 Smart Expense Analyzer")

# =========================
# ➕ ADD EXPENSE SECTION
# =========================
if choice == "Add Expense":
    st.header("➕ Add Expense")

    date = st.date_input("Date")
    category = st.selectbox("Category", ["Food", "Travel", "Shopping", "Bills", "Other"])
    amount = st.number_input("Amount")
    description = st.text_input("Description")

    if st.button("Add Expense"):
        add_expense(str(date), category, amount, description)
        st.success("Expense Added!")

# =========================
# 📊 DASHBOARD SECTION
# =========================
elif choice == "Dashboard":
    st.header("📊 Dashboard")

    df = get_expenses()

    if df is not None and not df.empty:
        df['date'] = pd.to_datetime(df['date'])

        # 🔹 Metrics
        total = df["amount"].sum()
        avg = df["amount"].mean()

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Spending", f"₹{total}")
        with col2:
            st.metric("Average Spending", f"₹{avg:.2f}")

        st.markdown("---")

        # 🔹 Date Filter
        start = st.date_input("Start Date")
        end = st.date_input("End Date")

        df = df[(df['date'] >= str(start)) & (df['date'] <= str(end))]

        st.write(df)

        # 🔹 Category-wise spending
        st.subheader("Category-wise Spending")
        category_data = df.groupby("category")["amount"].sum()
        st.bar_chart(category_data)

        # 🔹 Monthly spending
        st.subheader("Monthly Spending")
        df['month'] = df['date'].dt.to_period('M')
        monthly = df.groupby('month')['amount'].sum()
        st.line_chart(monthly)

        # 🔹 Download Button
        st.download_button(
            "Download CSV",
            df.to_csv(index=False),
            "expenses.csv"
        )

    else:
        st.info("No data yet. Add some expenses!")

# =========================
# 🤖 INSIGHTS SECTION
# =========================
elif choice == "Insights":
    st.header("🤖 Insights")

    df = get_expenses()

    if df is not None and not df.empty:
        prediction = predict_spending(df)
        st.metric("Next Month Prediction", f"₹{prediction}")

        category_data = df.groupby("category")["amount"].sum()
        total = df["amount"].sum()

        st.markdown("---")

        # 🔹 Smart Alert
        if category_data.max() > (total * 0.4):
            st.warning("⚠ You are spending too much in one category!")

    else:
        st.info("Add data to see insights")
