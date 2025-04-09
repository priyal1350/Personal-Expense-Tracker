import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

st.set_page_config(page_title="Expense Tracker", layout="wide")
st.title("💰 Personal Expense Tracker")

# --- Session State Initialization ---
if 'expenses' not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Description'])

if 'file_loaded' not in st.session_state:
    st.session_state.file_loaded = False

if 'budgets' not in st.session_state:
    st.session_state.budgets = {
        "Food": 0.0,
        "Transport": 0.0,
        "Entertainment": 0.0,
        "Utilities": 0.0,
        "Other": 0.0
    }

# --- Sidebar Inputs ---
st.sidebar.header("➕ Add Expense")
date = st.sidebar.date_input("Date", datetime.today())
category = st.sidebar.selectbox("Category", ["Food", "Transport", "Entertainment", "Utilities", "Other"])
amount = st.sidebar.number_input("Amount", min_value=0.0, step=1.0)
description = st.sidebar.text_input("Description")

if st.sidebar.button("Add"):
    new_entry = pd.DataFrame({
        'Date': [date],
        'Category': [category],
        'Amount': [amount],
        'Description': [description]
    })
    st.session_state.expenses = pd.concat([st.session_state.expenses, new_entry], ignore_index=True)
    st.sidebar.success("Expense added!")

# --- File Upload / Load Expenses ---
st.sidebar.subheader("📁 File Operations")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")

if uploaded_file and not st.session_state.file_loaded:
    st.session_state.expenses = pd.read_csv(uploaded_file)
    st.session_state.file_loaded = True
    st.sidebar.success("File loaded!")

# --- Save to CSV ---
if st.sidebar.button("💾 Save Expenses"):
    st.session_state.expenses.to_csv("expenses_saved.csv", index=False)
    st.sidebar.success("Saved to expenses_saved.csv")

# --- Budget Settings ---
st.sidebar.header("💸 Set Monthly Budgets")
for cat in st.session_state.budgets:
    st.session_state.budgets[cat] = st.sidebar.number_input(f"{cat} Budget", min_value=0.0, value=st.session_state.budgets[cat], step=500.0)

if st.sidebar.button("💾 Save Budgets"):
    pd.DataFrame(list(st.session_state.budgets.items()), columns=["Category", "Budget"]).to_csv("budgets.csv", index=False)
    st.sidebar.success("Budgets saved to budgets.csv")

# --- Load Budgets ---
load_budget = st.sidebar.file_uploader("📤 Load Budget CSV", type="csv")
if load_budget:
    loaded_budget_df = pd.read_csv(load_budget)
    for _, row in loaded_budget_df.iterrows():
        st.session_state.budgets[row["Category"]] = row["Budget"]
    st.sidebar.success("Budgets loaded!")

# --- Date Range Filter ---
st.subheader("📄 Expense Table")
min_date = pd.to_datetime(st.session_state.expenses['Date']).min() if not st.session_state.expenses.empty else datetime.today()
max_date = pd.to_datetime(st.session_state.expenses['Date']).max() if not st.session_state.expenses.empty else datetime.today()
start_date, end_date = st.date_input("📅 Filter by Date Range", [min_date, max_date])

# --- Filtered Data ---
filtered_df = st.session_state.expenses.copy()
filtered_df['Date'] = pd.to_datetime(filtered_df['Date'])
filtered_df = filtered_df[(filtered_df['Date'] >= pd.to_datetime(start_date)) & (filtered_df['Date'] <= pd.to_datetime(end_date))]

st.dataframe(filtered_df, use_container_width=True)

# --- Budget Alerts ---
st.subheader("🚨 Budget Alerts")
alerts = []
for cat in st.session_state.budgets:
    spent = filtered_df[filtered_df['Category'] == cat]['Amount'].sum()
    budget = st.session_state.budgets[cat]
    if spent > budget and budget > 0:
        alerts.append(f"⚠️ You have exceeded the budget for **{cat}**! Spent ₹{spent:.2f} / Budget ₹{budget:.2f}")

if alerts:
    for alert in alerts:
        st.warning(alert)
else:
    st.success("✅ All expenses are within your budget limits.")

# --- Summary ---
st.subheader("📊 Expense Summary")
total = filtered_df['Amount'].sum()
top_category = filtered_df.groupby('Category')['Amount'].sum().idxmax() if not filtered_df.empty else 'N/A'
st.metric("Total Expenses", f"₹{total:.2f}")
st.metric("Top Category", top_category)

# --- Charts ---
st.subheader("📈 Visualizations")

# --- Bar Chart ---
if st.button("📊 Show Bar Chart"):
    if not filtered_df.empty:
        chart_data = filtered_df.groupby('Category')['Amount'].sum()

        # Create a bar chart using Matplotlib for better control
        fig, ax = plt.subplots()
        bars = ax.bar(chart_data.index, chart_data.values, color='cornflowerblue')
        ax.set_title("Expenses by Category", fontsize=14)
        ax.set_xlabel("Category", fontsize=12)
        ax.set_ylabel("Total Amount (₹)", fontsize=12)
        ax.set_xticks(range(len(chart_data.index)))
        ax.set_xticklabels(chart_data.index, rotation=0, fontsize=10)

        # Add value labels on top of bars
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2.0, yval + 10, f'₹{yval:.0f}', ha='center', va='bottom', fontsize=10)

        st.pyplot(fig)
    else:
        st.info("No data to display!")

# --- Pie Chart ---
if st.button("🥧 Show Pie Chart"):
    if not filtered_df.empty:
        chart_data = filtered_df.groupby('Category')['Amount'].sum()
        fig, ax = plt.subplots()
        ax.pie(chart_data, labels=chart_data.index, autopct='%1.1f%%')
        ax.set_title("Expense Distribution by Category", fontsize=14)
        st.pyplot(fig)
    else:
        st.info("No data to display!")
