import streamlit as st
import pandas as pd
import os

from database import create_table
from expense_manager import add_expense, get_expenses
from ml_model import predict_spending

# =========================
# 🎨 PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Smart Expense Analyzer",
    page_icon="💰",
    layout="wide"
)

# =========================
# 🎨 CUSTOM CSS (MODERN LOOK)
# =========================
st.markdown("""
<style>
body {
    background-color: #0E1117;
    color: white;
}
.stMetric {
    background-color: #1c1f26;
    padding: 15px;
    border-radius: 10px;
}
.stButton>button {
    background-color: #4CAF50;
    color: white;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 🗄 DATABASE INIT
# =========================
if not os.path.exists("expenses.db"):
    create_table()

# =========================
# 📌 SIDEBAR
# =========================
st.sidebar.title("💸 Expense Tracker")
st.sidebar.markdown("Track • Analyze • Save")

menu = ["Dashboard", "Add Expense", "Insights"]
choice = st.sidebar.radio("Navigation", menu)

st.title("💰 Smart Expense Analyzer")

# =========================
# ➕ ADD EXPENSE
# =========================
if choice == "Add Expense":
    st.subheader("➕ Add New Expense")

    col1, col2 = st.columns(2)

    with col1:
        date = st.date_input("Date")
        category = st.selectbox("Category", ["Food", "Travel", "Shopping", "Bills", "Other"])

    with col2:
        amount = st.number_input("Amount", min_value=0)
        description = st.text_input("Description")

    if st.button("Add Expense"):
        add_expense(str(date), category, amount, description)
        st.success("✅ Expense Added Successfully!")

# =========================
# 📊 DASHBOARD
# =========================
elif choice == "Dashboard":
    st.subheader("📊 Financial Overview")

    df = get_expenses()

    if df is not None and not df.empty:
        df['date'] = pd.to_datetime(df['date'])

        # 🔹 Metrics Cards
        total = df["amount"].sum()
        avg = df["amount"].mean()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("💸 Total Spending", f"₹{total}")

        with col2:
            st.metric("📊 Average Expense", f"₹{avg:.2f}")

        with col3:
            st.metric("🧾 Transactions", len(df))

        st.markdown("---")

        # 🔹 Filters
        col1, col2 = st.columns(2)

        with col1:
            start = st.date_input("Start Date")

        with col2:
            end = st.date_input("End Date")

        df = df[(df['date'] >= str(start)) & (df['date'] <= str(end))]

        # 🔹 Charts
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📂 Category Breakdown")
            category_data = df.groupby("category")["amount"].sum()
            st.bar_chart(category_data)

        with col2:
            st.subheader("📈 Monthly Trend")
            df['month'] = df['date'].dt.to_period('M')
            monthly = df.groupby('month')['amount'].sum()
            st.line_chart(monthly)

        st.markdown("---")

        # 🔹 Data Table
        st.subheader("📋 All Transactions")
        st.dataframe(df)

        # 🔹 Download
        st.download_button(
            "⬇ Download Report",
            df.to_csv(index=False),
            "expenses.csv"
        )

    else:
        st.info("No data yet. Add some expenses!")

# =========================
# 🤖 INSIGHTS
# =========================
elif choice == "Insights":
    st.subheader("🤖 Smart Insights")

    df = get_expenses()

    if df is not None and not df.empty:
        prediction = predict_spending(df)

        st.metric("🔮 Predicted Next Month", f"₹{prediction}")

        category_data = df.groupby("category")["amount"].sum()
        total = df["amount"].sum()

        st.markdown("---")

        # 🔹 Smart Alerts
        if category_data.max() > (total * 0.4):
            st.warning("⚠ High spending detected in one category!")

        # 🔹 AI-like Insight
        st.info(f"💡 You have spent ₹{total} so far. Try reducing unnecessary expenses.")

    else:
        st.info("Add data to see insights")
