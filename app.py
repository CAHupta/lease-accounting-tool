import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="Lease Accounting Tool - Ind AS 116", layout="centered")
st.title("📊 Lease Accounting Tool (Ind AS 116)")

with st.form("lease_form"):
    lease_start = st.date_input("Lease Start Date", datetime(2025, 1, 1))
    lease_duration_months = st.number_input("Lease Duration (in months)", value=60, min_value=1)
    frequency = st.selectbox("Payment Frequency", ["Monthly", "Quarterly", "Semi-Annually", "Annually"])
    rent_amount = st.number_input("Initial Rent Amount (₹)", value=100000.0)
    escalation_freq = st.number_input("Escalation Frequency (in months)", value=12, min_value=1)
    escalation_rate = st.number_input("Escalation Rate (%)", value=5.0)
    escalation_base = st.selectbox("Escalation Applied On", ["Initial", "Last"])
    rent_free_months = st.number_input("Rent-Free Period (months)", value=3, min_value=0)
    down_payment = st.number_input("Down Payment (₹)", value=500000.0)
    down_adj_months = st.number_input("Down Payment Adjustment Period (months)", value=12, min_value=1)
    security_deposit = st.number_input("Refundable Security Deposit (₹)", value=1000000.0)
    discount_rate = st.number_input("Discount Rate for PV Calculations (%)", value=8.0)

    submitted = st.form_submit_button("Generate Payment Schedule")

if submitted:
    freq_map = {"Monthly": 1, "Quarterly": 3, "Semi-Annually": 6, "Annually": 12}
    freq_months = freq_map[frequency]
    total_periods = lease_duration_months // freq_months
    escalation_steps = escalation_freq // freq_months
    start_date = lease_start + relativedelta(months=+rent_free_months)
    down_adj_per_period = down_payment / (down_adj_months // freq_months) if down_payment > 0 else 0

    rent = rent_amount
    schedule = []

    for i in range(total_periods):
        payment_date = start_date + relativedelta(months=+(i * freq_months))

        if i > 0 and escalation_steps > 0 and i % escalation_steps == 0:
            if escalation_base == "Initial":
                rent = rent_amount * ((1 + escalation_rate / 100) ** (i // escalation_steps))
            else:
                rent *= (1 + escalation_rate / 100)

        rent_net = rent - down_adj_per_period if i < (down_adj_months // freq_months) else rent
        schedule.append([payment_date.strftime('%d-%m-%Y'), rent_net])

    df = pd.DataFrame(schedule, columns=["Payment Date", "Payment Amount (₹)"])

    st.subheader("📅 Lease Payment Schedule")
    st.dataframe(df, use_container_width=True)

    output_excel = df.to_excel("Lease_Payment_Schedule.xlsx", index=False, engine='openpyxl')
    with open("Lease_Payment_Schedule.xlsx", "rb") as f:
        st.download_button("📥 Download Excel", f, file_name="Lease_Payment_Schedule.xlsx")
