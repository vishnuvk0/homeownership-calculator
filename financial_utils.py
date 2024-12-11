import math

def future_value(lump_sum, annual_rate, years):
    """Calculate future value of a lump sum investment."""
    return lump_sum * ((1 + annual_rate)**years)

def calculate_mortgage_payment(loan_amount, annual_rate, term_years):
    """Calculate monthly mortgage payment."""
    monthly_rate = annual_rate / 12
    num_payments = term_years * 12
    return (loan_amount * monthly_rate) / (1 - (1 + monthly_rate)**(-num_payments))

def calculate_future_monthly_investments(contributions, monthly_rate, total_months):
    """Calculate future value of series of monthly investments."""
    fv = 0.0
    for i, contribution in enumerate(contributions):
        months_left = (total_months - (i+1))
        fv += contribution * ((1 + monthly_rate)**(months_left))
    return fv

def project_rent_values(initial_rent, months, annual_growth_rate):
    """Project monthly rent values with annual growth."""
    monthly_rents = []
    current_rent = initial_rent
    
    for m in range(1, months+1):
        if m > 1 and (m-1) % 12 == 0:
            current_rent *= (1 + annual_growth_rate)
        monthly_rents.append(current_rent)
    
    return monthly_rents 