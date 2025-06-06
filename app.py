
import streamlit as st
import pandas as pd
import re
from datetime import datetime
import io

st.title("Υπολογισμός Ανθρωπομηνών (με βάση τις ημέρες)")

def parse_period(period_str):
    matches = re.findall(r'(\d{1,2}/\d{1,2}/\d{4}|\d{1,2}/\d{4})', period_str)
    if len(matches) != 2:
        return None, None
    try:
        # Επεξεργασία για συμπλήρωση ημερών αν λείπουν
        def fix_date(d):
            parts = d.split('/')
            if len(parts) == 2:  # Μορφή ΜΜ/ΕΕΕΕ
                return f"01/{d}"  # Αρχή μήνα
            return d

        start = pd.to_datetime(fix_date(matches[0]), dayfirst=True)
        end = pd.to_datetime(fix_date(matches[1]), dayfirst=True)

        if start > end:
            start, end = end, start
        return start, end
    except:
        return None, None

uploaded_file = st.file_uploader("Ανεβάστε το αρχείο Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, engine="openpyxl")
    human_months_list = []

    new_df = df.copy()
    total_days = 0

    for idx, row in df.iterrows():
        total_row_days = 0
        for col in df.columns:
            val = str(row[col])
            if "-" in val:
                start, end = parse_period(val)
                if start and end:
                    days = (end - start).days + 1
                    total_row_days += days
        human_months = round(total_row_days / 30, 2)
        human_months_list.append(human_months)
        total_days += total_row_days

    new_df["Ανθρωπομήνες"] = human_months_list

    total_human_months = round(total_days / 30, 2)
    st.write("🧮 Σύνολο Ανθρωπομηνών:", total_human_months)

    total_row = pd.DataFrame([["" for _ in range(len(new_df.columns) - 1)] + [total_human_months]], columns=new_df.columns)
    new_df = pd.concat([new_df, total_row], ignore_index=True)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        new_df.to_excel(writer, index=False)
    st.download_button("⬇️ Κατεβάστε το αρχείο με Ανθρωπομήνες", data=output.getvalue(),
                       file_name="ανθρωπομήνες_ημερες.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
