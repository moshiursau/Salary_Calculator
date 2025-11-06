# salary_app.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
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
        110966.87,115078.92,119182.31,123295.44,127404.24,131514.13,
        135620.77,139733.90,143838.37,147952.58,152055.98,156172.35,
        163016.75,168495.51,173973.19,179451.96,
        209591.11
    ]
}

df = pd.DataFrame(data)

# -----------------------------
# Configuration
# -----------------------------
ON_COST_RATE = 0.377
SALARY_INCREASE_DATE = datetime(2026,7,1)
SALARY_INCREASE_RATE = 0.052
ANNUAL_LEAVE_DAYS = 20
WORKING_DAYS_PER_YEAR = 227  # Base for daily salary calculation

# Example 13 public holidays (unpaid)
PUBLIC_HOLIDAYS = [
    (1,1), (26,1), (3,4), (6,4), (25,4), (8,6),
    (3,8), (5,10), (25,12), (28,12),
    (29,12), (30,12), (31,12)
]

# -----------------------------
# Helper: calculate paid working days (excluding public holidays, adding annual leave)
# -----------------------------
def calculate_paid_days(start_date, end_date, public_holidays=PUBLIC_HOLIDAYS, annual_leave=ANNUAL_LEAVE_DAYS):
    all_days = pd.date_range(start=start_date, end=end_date, freq='D')
    weekdays = all_days[all_days.weekday < 5]  # Mon-Fri
    
    # Remove public holidays
    holidays_dates = [d for d in weekdays if (d.day, d.month) in public_holidays]
    working_days = [d for d in weekdays if d not in holidays_dates]
    
    # Total paid days = working days + annual leave
    total_paid_days = len(working_days) + annual_leave
    
    return len(working_days), total_paid_days

# -----------------------------
# Salary calculation function
# -----------------------------
def calculate_salary(level, base_level, start_date, end_date, fte=1.0):
    row = df[(df['LEVEL'] == level.upper()) & (df['Base Level'] == base_level.title())]
    if row.empty:
        return {"Error": "No matching LEVEL and Base Level found."}
    
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    # Calculate working days and total paid days before and after salary increase
    if end_date < SALARY_INCREASE_DATE:
        work_before, paid_before = calculate_paid_days(start_date, end_date)
        work_after, paid_after = 0, 0
    elif start_date >= SALARY_INCREASE_DATE:
        work_before, paid_before = 0, 0
        work_after, paid_after = calculate_paid_days(start_date, end_date)
    else:
        work_before, paid_before = calculate_paid_days(start_date, SALARY_INCREASE_DATE - timedelta(days=1))
        work_after, paid_after = calculate_paid_days(SALARY_INCREASE_DATE, end_date)
    
    # Daily salary with on-costs
    yearly_salary = row['Yearly Salary'].values[0]
    daily_salary = (yearly_salary / WORKING_DAYS_PER_YEAR) * (1 + ON_COST_RATE)
    
    # Calculate salary
    salary_before = paid_before * daily_salary * fte
    salary_after = paid_after * daily_salary * (1 + SALARY_INCREASE_RATE) * fte
    total_salary = salary_before + salary_after
    
    return {
        "Level": level,
        "Base Level": base_level,
        "Start Date": start_date.date(),
        "End Date": end_date.date(),
        "FTE": fte,
        "Working Days Before Increase": work_before,
        "Working Days After Increase": work_after,
        "Paid Days Before Increase": paid_before,
        "Paid Days After Increase": paid_after,
        "Daily Salary (with costs)": round(daily_salary,2),
        "Total Salary": round(total_salary,2)
    }

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("Interactive Salary Calculator (Annual Leave Paid, Holidays Excluded)")

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






