
import streamlit as st
import pandas as pd
import re
from dateutil.relativedelta import relativedelta
from datetime import datetime
import io

st.title("Υπολογισμός Ανθρωπομηνών από Περιόδους Excel")

def parse_period(period_str):
    matches = re.findall(r'(\d{1,2}/\d{1,2}/\d{4}|\d{1,2}/\d{4})', period_str)
    if len(matches) != 2:
        return None, None
    try:
        start = pd.to_datetime(matches[0], dayfirst=True)
        end = pd.to_datetime(matches[1], dayfirst=True)
        if start > end:
            start, end = end, start
        return start, end
    except:
        return None, None

def generate_month_set(start, end):
    months = set()
    current = datetime(start.year, start.month, 1)
    end = datetime(end.year, end.month, 1)
    while current <= end:
        months.add(current.strftime("%Y-%m"))
        current += relativedelta(months=1)
    return months

uploaded_file = st.file_uploader("Ανεβάστε το αρχείο Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, engine="openpyxl")
    all_months = set()
    human_months_list = []

    new_df = df.copy()

    for idx, row in df.iterrows():
        row_months = set()
        for col in df.columns:
            val = str(row[col])
            if "-" in val:
                start, end = parse_period(val)
                if start and end:
                    months = generate_month_set(start, end)
                    row_months.update(months)
        human_months_list.append(len(row_months))
        all_months.update(row_months)

    new_df["Ανθρωπομήνες"] = human_months_list

    st.write("🧮 Σύνολο Ανθρωπομηνών:", len(all_months))

    total_row = pd.DataFrame([["" for _ in range(len(new_df.columns) - 1)] + [len(all_months)]], columns=new_df.columns)
    new_df = pd.concat([new_df, total_row], ignore_index=True)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        new_df.to_excel(writer, index=False)
    st.download_button("⬇️ Κατεβάστε το αρχείο με Ανθρωπομήνες", data=output.getvalue(),
                       file_name="ανθρωπομήνες.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
