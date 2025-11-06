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
        110966.87,115078.92,119182.31,123295.44,127404.24,131514.13,
        135620.77,139733.90,143838.37,147952.58,152055.98,156172.35,
        163016.75,168495.51,173973.19,179451.96,
        209591.11
    ]
}
df = pd.DataFrame(data)

# -----------------------------
# Constants
# -----------------------------
ON_COST_RATE = 0.377
SALARY_INCREASE_DATE = datetime(2026,7,1)
SALARY_INCREASE_RATE = 0.052   # 5.2% increase
WORKING_DAYS_PER_YEAR = 227
ANNUAL_LEAVE_DAYS_PER_YEAR = 20
TOTAL_PAID_DAYS_PER_YEAR = WORKING_DAYS_PER_YEAR + ANNUAL_LEAVE_DAYS_PER_YEAR

# -----------------------------
# Salary Calculation Function
# -----------------------------
def calculate_salary(level, base_level, start_date, end_date, fte=1.0):
    row = df[(df['LEVEL'] == level.upper()) & (df['Base Level'] == base_level.title())]
    if row.empty:
        return {"Error": "No matching LEVEL and Base Level found."}

    yearly_salary = row['Yearly Salary'].values[0]
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    total_days = (end_date - start_date).days + 1
    if total_days <= 0:
        return {"Error": "End date must be after start date."}

    # Split duration relative to salary increase date
    if end_date < SALARY_INCREASE_DATE:
        days_before, days_after = total_days, 0
    elif start_date >= SALARY_INCREASE_DATE:
        days_before, days_after = 0, total_days
    else:
        days_before = (SALARY_INCREASE_DATE - start_date).days
        days_after = total_days - days_before

    # Daily rate (with on-costs)
    daily_rate_with_costs = (yearly_salary / WORKING_DAYS_PER_YEAR) * (1 + ON_COST_RATE)

    # Proportion of year worked before and after increase
    year_fraction_before = days_before / 365
    year_fraction_after = days_after / 365

    # Working and annual leave days (pro-rated)
    working_days_before = WORKING_DAYS_PER_YEAR * year_fraction_before
    working_days_after = WORKING_DAYS_PER_YEAR * year_fraction_after
    annual_leave_before = ANNUAL_LEAVE_DAYS_PER_YEAR * year_fraction_before
    annual_leave_after = ANNUAL_LEAVE_DAYS_PER_YEAR * year_fraction_after

    # Paid days
    paid_days_before = working_days_before + annual_leave_before
    paid_days_after = working_days_after + annual_leave_after
    total_paid_days = paid_days_before + paid_days_after

    # Salaries
    salary_before = paid_days_before * daily_rate_with_costs * fte
    salary_after = paid_days_after * daily_rate_with_costs * (1 + SALARY_INCREASE_RATE) * fte
    total_salary = salary_before + salary_after

    return {
        "Level": level,
        "Base Level": base_level,
        "Start Date": start_date.date(),
        "End Date": end_date.date(),
        "FTE": fte,
        "Days Before 1 Jul 2026": days_before,
        "Days After 1 Jul 2026": days_after,
        "Working Days Before": round(working_days_before, 2),
        "Working Days After": round(working_days_after, 2),
        "Annual Leave Before": round(annual_leave_before, 2),
        "Annual Leave After": round(annual_leave_after, 2),
        "Paid Days Total": round(total_paid_days, 2),
        "Daily Salary (with costs)": round(daily_rate_with_costs, 2),
        "Total Salary ($)": round(total_salary, 2)
    }

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("Salary Calculator – 5.2% Increase on 1 July 2026 (with Annual Leave)")

level = st.selectbox("Select LEVEL:", sorted(df['LEVEL'].unique()))
base_level = st.selectbox("Select Base Level:", sorted(df['Base Level'].unique()))
start_date = st.date_input("Start Date", datetime(2026,3,1))
end_date = st.date_input("End Date", datetime(2027,3,1))
fte = st.slider("FTE (Full-time equivalent)", 0.1, 1.0, 1.0, 0.05)

if st.button("Calculate Salary"):
    result = calculate_salary(level, base_level, start_date, end_date, fte)
    st.write("### Salary Details")
    st.json(result)

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


