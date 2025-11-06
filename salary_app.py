# salary_app.py
import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

# -----------------------------
# Example dataset
# -----------------------------
data = {
    'LEVEL': [
        'A','A','A','A','A','A','A','A',
        'B','B','B','B','B','B',
        'C','C','C','C','C','C',
        'D','D','D','D',
        'E'
    ],
    'Base Level': [
        'Base','Base +1','Base +2','Base +3','Base +4','Base +5','Base +6','Base +7',
        'Base','Base +1','Base +2','Base +3','Base +4','Base +5',
        'Base','Base +1','Base +2','Base +3','Base +4','Base +5',
        'Base','Base +1','Base +2','Base +3',
        'Base'
    ],
    'Yearly Salary': [
        78092.13,82474.71,86856.20,91242.03,94802.19,98366.69,101926.86,105483.78,
        110966.87,115078.92119,182.31,123295.44,127404.24,131514.13,
        135620.77,139733.90,143838.37,147952.58,152055.98,156172.35,
        163016.75,168495.51,173973.19,179451.96,
        209591.11
    ]
}


df = pd.DataFrame(data)

# -----------------------------
# Configuration
# -----------------------------
WORKING_DAYS_PER_YEAR = 247
ON_COST_RATE = 0.377
SALARY_INCREASE_DATE = datetime(2026,7,1)
SALARY_INCREASE_RATE = 0.052

df['Daily Salary'] = df['Yearly Salary'] / WORKING_DAYS_PER_YEAR
df['Daily Salary (with on-costs)'] = df['Daily Salary'] * (1 + ON_COST_RATE)

# -----------------------------
# Salary calculation function
# -----------------------------
def calculate_salary(level, base_level, start_date, end_date, fte=1.0):
    row = df[(df['LEVEL'] == level.upper()) & (df['Base Level'] == base_level.title())]
    if row.empty:
        return {"Error": "No matching LEVEL and Base Level found."}
    
    daily_salary = row['Daily Salary (with on-costs)'].values[0]
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    if end_date < SALARY_INCREASE_DATE:
        days_before = (end_date - start_date).days + 1
        days_after = 0
    elif start_date >= SALARY_INCREASE_DATE:
        days_before = 0
        days_after = (end_date - start_date).days + 1
    else:
        days_before = (SALARY_INCREASE_DATE - start_date).days
        days_after = (end_date - SALARY_INCREASE_DATE).days + 1
    
    salary_before = days_before * daily_salary * fte
    salary_after = days_after * daily_salary * (1 + SALARY_INCREASE_RATE) * fte
    total_salary = salary_before + salary_after
    
    return {
        "Level": level,
        "Base Level": base_level,
        "Start Date": start_date.date(),
        "End Date": end_date.date(),
        "FTE": fte,
        "Days Before 1 Jul 2026": days_before,
        "Days After 1 Jul 2026": days_after,
        "Daily Salary (with costs)": round(daily_salary,2),
        "Total Salary": round(total_salary,2)
    }

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("Interactive Salary Calculator (2025–2026)")

level = st.selectbox("Select LEVEL:", sorted(df['LEVEL'].unique()))
base_level = st.selectbox("Select Base Level:", sorted(df['Base Level'].unique()))
start_date = st.date_input("Start Date", datetime(2026,3,1))
end_date = st.date_input("End Date", datetime(2026,9,30))
fte = st.slider("FTE (Full-time equivalent)", 0.1, 1.0, 1.0, 0.05)

if st.button("Calculate Salary"):
    result = calculate_salary(level, base_level, start_date, end_date, fte)
    st.write("### Salary Details")
    st.json(result)
    
    # Optional: CSV download
    df_result = pd.DataFrame([result])
    buffer = BytesIO()
    df_result.to_csv(buffer, index=False)
    buffer.seek(0)
    st.download_button(
        label="Download Salary Details as CSV",
        data=buffer,
        file_name="salary_details.csv",
        mime="text/csv"
    )

