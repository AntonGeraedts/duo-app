import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def format_currency(amount):
    """Format number as European currency (28.405)"""
    return f"{round(amount):,}".replace(",", ".")

st.title("Duo Studieschuld Terugbetalen")

# st.write("How much do you owe Duo? (Or how much do you expect to owe Duo?)")
debt = st.number_input("Debt", value=0, min_value=0, step=100)

# st.write("Annual debt interest rate:")
debt_interest_rate = st.number_input("Debt Interest Rate (%)", value=2.57, min_value=0.0, step=0.01) / 100

# st.write("How much do you earn per month? (Or how much do you expect to earn per month?)")
monthly_income = st.number_input("Income per month (now)", value=0, min_value=0, step=100)

# Salary growth options
salary_option = st.radio("Choose salary projection method:", ["Percentage growth", "Target end salary"])

if salary_option == "Percentage growth":
    # st.write("Annual salary increase percentage:")
    salary_growth = st.number_input("Salary Growth (%)", value=2.0, min_value=0.0, step=0.1) / 100
    target_salary = None
else:
    # st.write("Target salary in 35 years:")
    target_salary = st.number_input("Target Monthly Salary in 35 Years (€)", value=5000, min_value=0, step=100)
    salary_growth = None

# st.write("Annual minimum wage increase percentage:")
min_wage_growth = st.number_input("Minimum Wage Growth (%)", value=1.0, min_value=0.0, step=0.1) / 100


st.title("Draagkracht")
st.write("Duo calculates the amount you need to pay back per month based on your draagkracht. Your draagkracht is determined by the amount you earn per month compared to the minimum wage.")

st.write("For this example, we will use a minimum wage of €2.367 per month. We will take a loan with 35 years to pay back the debt.")

st.markdown('"U hoeft nooit meer dan 4% van uw inkomen boven de draagkrachtvrije voet te betalen. Bent u alleenstaand zonder kinderen, dan is de draagkrachtvrije voet 100% van het minimumloon. In alle andere gevallen is het 143%." - Duo')

st.write("The ''draagkrachtvrije voet'' is the part of your salary of which you never have to pay back a percentage. i.e. you will always get at least the minimum wage, and over the rest which you get above that, you will be charged maximum 4%. For married couples or people with children, this becomes 140% of the minimum wage.")

st.write("Draagkrachtvrije voet = € 28.405,73")

draagkrachtvrije_voet = 28405.73

amount_above_draagkrachtvrije_voet = max(0, monthly_income - draagkrachtvrije_voet/12)

monthly_payment = amount_above_draagkrachtvrije_voet*0.04


# Create time series for 35 years
st.title("Payment Evolution Over Time")

if monthly_income > 0:
    # Show calculated growth rate if using target salary
    if salary_option == "Target end salary" and target_salary > monthly_income:
        calculated_growth_rate = (target_salary / monthly_income) ** (1/35) - 1
        st.info(f"To reach €{format_currency(target_salary)} in 35 years, your salary needs to grow by {calculated_growth_rate*100:.2f}% annually.")
    
    # Create time series data
    years = np.arange(0, 35.1, 0.5)  # Every 6 months for 35 years
    monthly_salaries = []
    monthly_payments = []
    monthly_min_wages = []
    
    for year in years:
        # Calculate salary for this year
        if salary_option == "Percentage growth":
            current_salary = monthly_income * (1 + salary_growth) ** year
        else:
            # Calculate compound growth rate needed to reach target salary
            if target_salary > monthly_income:
                growth_rate = (target_salary / monthly_income) ** (1/35) - 1
                current_salary = monthly_income * (1 + growth_rate) ** year
            else:
                current_salary = monthly_income  # No growth if target is lower than current
        
        # Calculate minimum wage for this year
        current_min_wage = 2367 * (1 + min_wage_growth) ** year  # Starting from €2,367
        
        # Calculate draagkrachtvrije voet (143% of minimum wage for non-single)
        draagkrachtvrije_voet_monthly = current_min_wage
        
        # Calculate payment
        amount_above_threshold = max(0, current_salary - draagkrachtvrije_voet_monthly)
        payment = amount_above_threshold * 0.04
        
        monthly_salaries.append(current_salary)
        monthly_payments.append(payment)
        monthly_min_wages.append(current_min_wage)
    
    # Create DataFrame for plotting
    df = pd.DataFrame({
        'Year': years,
        'Monthly Salary': monthly_salaries,
        'Monthly Payment': monthly_payments,
        'Minimum Wage': monthly_min_wages
    })
    
    # Create the plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Plot salary and minimum wage
    ax1.plot(df['Year'], df['Monthly Salary'], label='Your Monthly Salary', linewidth=2, color='blue')
    ax1.plot(df['Year'], df['Minimum Wage'], label='Minimum Wage', linewidth=2, color='red')
    ax1.set_xlabel('Years')
    ax1.set_ylabel('Monthly Amount (€)')
    ax1.set_title('Salary vs Minimum Wage Evolution')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot monthly payment
    ax2.plot(df['Year'], df['Monthly Payment'], label='Monthly DUO Payment', linewidth=2, color='green')
    ax2.set_xlabel('Years')
    ax2.set_ylabel('Monthly Payment (€)')
    ax2.set_title('DUO Payment Evolution')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    st.pyplot(fig)
    
    # Calculate debt value at the end of 35 years
    debt_at_end = debt * (1 + debt_interest_rate) ** 35
    
    # Calculate total payments and discounted value
    total_payment = sum(monthly_payments) * 2  # *2 because we calculated every 6 months
    
    # Calculate discounted value of payments (present value)
    # Using a discount rate of 2.5% (typical for long-term financial calculations)
    discount_rate = 0.025
    discounted_payments = 0
    for i, payment in enumerate(monthly_payments):
        # Each payment occurs every 6 months, so discount by (1 + rate)^(i*0.5)
        discounted_payments += payment / ((1 + discount_rate) ** (i * 0.5))
    discounted_payments *= 2  # *2 because we calculated every 6 months
    
    # Payment Evolution Section
    st.subheader("Payment Evolution")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Starting Monthly Payment", f"€{format_currency(monthly_payments[0])}")
    with col2:
        st.metric("Final Monthly Payment", f"€{format_currency(monthly_payments[-1])}")
    with col3:
        st.metric("Total Paid Over 35 Years", f"€{format_currency(total_payment)}")
    
    # Financial Summary Section
    st.subheader("Financial Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Starting Debt", f"€{format_currency(debt)}")
    with col2:
        st.metric("Total Payments (Nominal)", f"€{format_currency(total_payment)}")
    with col3:
        st.metric("Total Payments (Today's Value)", f"€{format_currency(discounted_payments)}")

st.link_button("Visit Duo", "https://duo.nl/particulier/studieschuld-terugbetalen/berekening-maandbedrag.jsp")


