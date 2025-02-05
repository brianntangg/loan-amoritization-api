from fastapi import HTTPException

def generate_amortization_schedule(amount: float, interest_rate: float, term_months: int):
    # Calculate monthly interest rate
    monthly_rate = (interest_rate / 100) / 12

    # Calculate the monthly payment based on the loan amount, interest rate, and term
    monthly_payment = (amount * monthly_rate) / (1 - (1 + monthly_rate) ** -term_months)

    schedule = []
    remaining_balance = amount

    for month in range(1, term_months + 1):
        # Calculate interest for the current month
        interest = remaining_balance * monthly_rate

        # Calculate principal payment for the current month
        principal = monthly_payment - interest

        # Reduce remaining balance by the principal amount
        remaining_balance -= principal
        
        # Append the month’s information to the schedule
        schedule.append({
            "month": month,
            "remaining_balance": round(remaining_balance, 2),
            "monthly_payment": round(monthly_payment, 2)
        })

    return schedule


def calculate_loan_summary(amount: float, annual_interest_rate: float, loan_term_months: int, month: int):
    # Ensure the month is valid (within the loan term)
    if month < 1 or month > loan_term_months:
        raise HTTPException(status_code=400, detail="Invalid month requested")

    # Calculate the monthly interest rate
    monthly_interest_rate = (annual_interest_rate / 100) / 12

    # Calculate the monthly payment using the same formula as in the amortization function
    monthly_payment = (amount * monthly_interest_rate) / (1 - (1 + monthly_interest_rate) ** -loan_term_months)

    total_principal_paid = 0
    total_interest_paid = 0
    remaining_balance = amount

    for m in range(1, month + 1):
        # Calculate interest payment for the current month
        interest_payment = remaining_balance * monthly_interest_rate

        # Calculate principal payment for the current month
        principal_payment = monthly_payment - interest_payment

        # Reduce remaining balance by the principal payment
        remaining_balance -= principal_payment

        # Accumulate the total principal and interest paid
        total_principal_paid += principal_payment
        total_interest_paid += interest_payment

    # Return a dictionary with the loan summary for the specified month
    return {
        "month": month,
        "current_principal_balance": max(0, remaining_balance),  # Ensure the balance doesn't go below 0
        "total_principal_paid": total_principal_paid,
        "total_interest_paid": total_interest_paid
    }
