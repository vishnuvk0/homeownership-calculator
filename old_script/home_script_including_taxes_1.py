import math
import matplotlib.pyplot as plt

# This code is a step-by-step projection for a 3-year period (36 months).
# The goal is to compare the cost/benefit of buying a $900,000 home vs. renting at $2,400/mo.
# It factors in mortgage costs, tax deductions, property tax, maintenance, insurance, HOA, 
# and opportunity cost investments. It also considers annual growth rates for rent, home value, 
# and alternative investments.

# ----------------------------
# Given assumptions
# ----------------------------
home_price = 900_000
down_payment_pct = 0.20
mortgage_rate_annual = 0.06
mortgage_term_years = 30
property_tax_rate_annual = 0.011  # 1.1% property tax
maintenance_annual = 5000
insurance_annual = 3500
hoa_monthly = 300
closing_costs_buy = 0.04 * home_price
closing_costs_sell_pct = 0.06

rent_current = 2400
rent_growth_annual = 0.04

alt_invest_growth_annual = 0.16     # Opportunity cost growth rate
monthly_invest_growth_annual = 0.15 # Investment growth rate for monthly difference between costs

home_appreciation_annual = 0.08
tax_rate = 0.30
property_tax_deduction_cap = 10_000

months = 36

# ----------------------------
# Derived values
# ----------------------------
down_payment = home_price * down_payment_pct
loan_amount = home_price - down_payment

# Monthly mortgage parameters: standard amortization formula for fixed-rate loan
monthly_interest_rate = mortgage_rate_annual / 12
num_payments = mortgage_term_years * 12
monthly_mortgage_payment = (loan_amount * monthly_interest_rate) / (1 - (1 + monthly_interest_rate)**(-num_payments))

# Calculate monthly costs for owning
# Monthly property tax
property_tax_annual = home_price * property_tax_rate_annual
property_tax_monthly = property_tax_annual / 12

maintenance_monthly = maintenance_annual / 12
insurance_monthly = insurance_annual / 12

# Initial Conditions
remaining_principal = loan_amount

# For rent scenario: 
# Rent increases each year by 4%. To get monthly rent for each month:
# For simplicity, assume rent changes once per year:
# Year 1: 2400/mo
# Year 2: 2400 * 1.04
# Year 3: 2400 * 1.04^2

monthly_rent = []
for m in range(1, months+1):
    year = math.ceil(m/12)
    current_rent = 2400 * ((1 + rent_growth_annual)**(year-1))
    monthly_rent.append(current_rent)

# Tracking
monthly_interest_paid = []
monthly_principal_paid = []
monthly_total_home_cost = []
monthly_tax_savings = []
monthly_investment_contribution = []
monthly_alternative_cost_contribution = []

# For opportunity cost calculation:
# The opportunity cost includes:
# 1) The initial down payment not being invested at 16% YOY for 3 years.
# 2) The principal portion of each monthly payment also not being invested at 16% YOY over time.
# We will track how much would have been invested in the 16% vehicle over 3 years.

# We’ll do a month-by-month simulation.

def future_value(lump_sum, annual_rate, years):
    return lump_sum * ((1 + annual_rate)**years)

def monthly_growth_investment(contributions, monthly_rate):
    # contributions is a list of monthly amounts invested at end of each month
    # monthly_rate is derived from annual_rate for monthly compounding
    # This will compound each monthly contribution until the end.
    total = 0.0
    # We'll add each contribution and grow forward
    for i, c in enumerate(contributions):
        months_left = len(contributions) - (i+1)
        # growth over remaining months
        total += c * ((1+monthly_rate)**(months_left))
    return total

# Convert annual growth rates to monthly
alt_invest_monthly_rate = (1+alt_invest_growth_annual)**(1/12)-1
monthly_invest_monthly_rate = (1+monthly_invest_growth_annual)**(1/12)-1

# Track how much principal + down payment is locked:
principal_locked_contributions = [down_payment]  # down payment upfront at month 0
monthly_principal_contributions = []

# Monthly breakdown
for m in range(1, months+1):
    # Interest portion of mortgage for this month:
    interest_for_this_month = remaining_principal * monthly_interest_rate
    principal_for_this_month = monthly_mortgage_payment - interest_for_this_month
    remaining_principal -= principal_for_this_month

    # Costs this month owning:
    # Mortgage payment + property tax + insurance + maintenance + HOA
    month_home_cost = monthly_mortgage_payment + property_tax_monthly + insurance_monthly + maintenance_monthly + hoa_monthly

    # Record interest and principal
    monthly_interest_paid.append(interest_for_this_month)
    monthly_principal_paid.append(principal_for_this_month)
    monthly_total_home_cost.append(month_home_cost)

    # Tax deduction calculations:
    # Deductible = mortgage interest + property taxes (capped at 10k/yr)
    # Let's assume we spread property tax monthly. We'll sum interest + property_tax this month.
    monthly_deductible = interest_for_this_month + property_tax_monthly
    # But property tax deduction is capped at 10k/year. For simplicity, 
    # do an approximate treatment: 
    # Over the whole year property_tax_annual = 9900 (since 1.1% of 900k = 9900)
    # That's under the 10k limit. Mortgage interest is fully deductible.
    # Actually, note that SALT limit of 10k applies to property+state taxes combined. 
    # We’ll assume full interest + property tax is deductible (as a simplification given the problem states I "get to deduct"). 
    # Real scenario is more complex, but let's follow given instructions.
    
    tax_saving_this_month = monthly_deductible * tax_rate
    monthly_tax_savings.append(tax_saving_this_month)

    # Compare to renting:
    # The difference (month_home_cost - rent_this_month) if positive, 
    # that difference does NOT get invested. If negative, that "savings" invests at 15% YOY.

    # Wait, instructions say:
    # "any remaining amount of the monthly payment that is not part of the principal (and is above what i pay in rent) 
    # is automatically invested." This means:
    # If the cost of owning (excluding principal?) Let's clarify:
    # The instructions: 
    # "{monthly payment towards mortgage interest and expenses} - {the cost of rent} = amount invested at 15% YOY"
    # Note: This suggests principal is building home equity, not counted as "expense" that would be invested. 
    # So let's define: 
    # Expenses for comparison: interest + property tax + insurance + maintenance + HOA (no principal).
    # We'll just exclude the principal portion from the cost for this calculation.

    monthly_expenses_ex_interest = property_tax_monthly + insurance_monthly + maintenance_monthly + hoa_monthly
    monthly_non_principal_expenses = interest_for_this_month + monthly_expenses_ex_interest

    invest_contribution = max(0, monthly_non_principal_expenses - monthly_rent[m-1])
    # If non_principal_expenses < rent, then no positive difference to invest 
    # because we assume we're forced to pay these costs anyway. The scenario is a bit ambiguous,
    # but from the description:
    # If monthly_non_principal_expenses are GREATER than rent, that difference goes into investment.
    # If they are not greater, then invest_contribution = 0.
    # Double check instructions:
    # "assume any remaining amount of the monthly payment that is not part of the principal (and is above what i pay in rent) 
    # is automatically invested."
    # This reads as: if (non_principal_expenses > rent), invest difference; else 0.
    
    monthly_investment_contribution.append(invest_contribution)

    # Also track principal contributions for opportunity cost (money tied up in equity):
    # Each month we add the principal_for_this_month to the locked equity.
    monthly_principal_contributions.append(principal_for_this_month)

# After 3 years, let's evaluate the final scenario:
# Home value after 3 years:
home_value_after_3 = home_price * ((1+home_appreciation_annual)**3)

# Selling costs at the end:
selling_costs = home_value_after_3 * closing_costs_sell_pct

# Net equity if sold after 3 years:
final_equity = home_value_after_3 - selling_costs - remaining_principal

# Total costs paid for owning:
total_down_payment = down_payment
total_monthly_paid = sum(monthly_total_home_cost)
total_tax_savings = sum(monthly_tax_savings)  # This is a reduction in effective cost
total_buying_cost = total_down_payment + closing_costs_buy + total_monthly_paid - total_tax_savings
# Note: The final_equity returned to you at the end offsets your total cost.

# Effective net cost after selling:
net_cost_after_selling = total_buying_cost - final_equity

# Total rent paid over 3 years:
total_rent_paid = sum(monthly_rent)

# Calculate the value of the monthly investment contributions at 15% YOY, contributed monthly:
# We'll compound monthly at monthly_invest_monthly_rate:
# Future value of monthly_investment_contributions at end of 36 months:
# Each contribution grows for the remaining months.
fv_monthly_invest = 0.0
for i, c in enumerate(monthly_investment_contribution):
    months_left = len(monthly_investment_contribution) - (i+1)
    fv_monthly_invest += c * ((1+monthly_invest_monthly_rate)**(months_left))

# Opportunity cost of down payment + principal:
# If that money were invested at 16% YOY, what would it be worth in 3 years?
# For simplicity, treat all principal as contributed at month midpoints:
# We'll approximate by calculating the future value of the down payment and the monthly principal at the end of 3 years.
fv_down_payment = future_value(down_payment, alt_invest_growth_annual, 3)

# For monthly principal contributions, grow each principal amount from its month until month 36:
fv_principal_opportunity = 0.0
for i, p in enumerate(monthly_principal_contributions):
    months_left = (months - (i+1))
    # monthly growth for alt investment:
    fv_principal_opportunity += p * ((1+alt_invest_monthly_rate)**(months_left))

# Compare scenarios:
# Renting scenario total cost = total_rent_paid (no home ownership),
# But you would have invested the down payment and principal at 16% YOY (opportunity scenario).
# The value of these investments at the end of 3 years if renting:
fv_invest_if_rent = fv_down_payment # from down payment alternative
# Add principal each month (which you wouldn't pay if renting)
fv_invest_if_rent += fv_principal_opportunity

# Owning scenario:
# Net cost after selling is net_cost_after_selling
# Plus, you have the fv_monthly_invest (the monthly difference that got invested at 15%).

# Let's summarize:
print("--------------- SUMMARY AFTER 3 YEARS ---------------")
print(f"Initial home price: ${home_price:,.2f}")
print(f"Home value after 3 years @8% YOY: ${home_value_after_3:,.2f}")
print(f"Remaining loan principal after 3 years: ${remaining_principal:,.2f}")
print(f"Selling costs @6%: ${selling_costs:,.2f}")
print(f"Final Equity if sold: ${final_equity:,.2f}")

print("\n--- Costs of Owning ---")
print(f"Down payment: ${down_payment:,.2f}")
print(f"Closing costs on buying @4%: ${closing_costs_buy:,.2f}")
print(f"Total monthly paid (mortgage+tax+ins+maint+HOA): ${total_monthly_paid:,.2f}")
print(f"Total tax savings from deductions: ${total_tax_savings:,.2f}")
print(f"Net cost after selling = Total costs - Equity: ${net_cost_after_selling:,.2f}")

print("\n--- Rent Scenario ---")
print(f"Total rent paid over 3 years: ${total_rent_paid:,.2f}")

print("\n--- Investment Calculations ---")
print("If buying: monthly difference invested at 15% YOY final value:")
print(f"Value of monthly difference investment: ${fv_monthly_invest:,.2f}")

print("\nIf renting: down payment + principal invested at 16% YOY final value:")
print(f"Value if renting and investing principal/down payment: ${fv_invest_if_rent:,.2f}")

# Determine which is better: 
# For owning: 
# Your final position = final_equity - (total cost of ownership excluding equity) + fv_monthly_invest
# Actually, we calculated net_cost_after_selling = total_buying_cost - final_equity,
# So total effective cost of owning after selling = net_cost_after_selling
# But we have fv_monthly_invest from monthly difference.

# Net position if owning:
# Money out: net_cost_after_selling (if positive, means net cost; if negative, means net gain)
# Money gained from monthly investments: fv_monthly_invest
# Effective net = fv_monthly_invest - net_cost_after_selling

# Net position if renting:
# Money out: total_rent_paid
# Money gained from investing at 16%: fv_invest_if_rent
# Effective net = fv_invest_if_rent - total_rent_paid

owning_effective_net = fv_monthly_invest - net_cost_after_selling
renting_effective_net = fv_invest_if_rent - total_rent_paid

print("\n--- Final Comparison ---")
print(f"Owning effective net position: ${owning_effective_net:,.2f}")
print(f"Renting effective net position: ${renting_effective_net:,.2f}")

if owning_effective_net > renting_effective_net:
    print("\nConclusion: Buying is more favorable after 3 years.")
else:
    print("\nConclusion: Renting is more favorable after 3 years.")

# ----------------------------
# Plotting a graph for monthly breakdown:
# We'll plot 3 lines:
# 1) Cumulative owning costs minus tax savings minus equity gained (net position over time)
# 2) Cumulative rent
# 3) Growth of investments

# For a simple graph, let's track cumulative rent vs. cumulative home cost over time.
cumulative_rent = []
cumulative_home_cost = []
cumulative_tax_savings = []
cumulative_interest = []
cumulative_principal = []
cumulative_investment_balance = []

running_rent = 0
running_home_cost = 0
running_tax_savings = 0
running_interest = 0
running_principal = 0

# For investment growth, we should apply monthly compounding to see its value each month
# It's simpler to just track contributions and compute partial FV month by month:
invested_amounts = []
for i in range(months):
    running_rent += monthly_rent[i]
    cumulative_rent.append(running_rent)

    running_home_cost += monthly_total_home_cost[i]
    running_tax_savings += monthly_tax_savings[i]
    running_interest += monthly_interest_paid[i]
    running_principal += monthly_principal_paid[i]
    cumulative_home_cost.append(running_home_cost)
    cumulative_tax_savings.append(running_tax_savings)
    cumulative_interest.append(running_interest)
    cumulative_principal.append(running_principal)

    # Track monthly investment contributions over time:
    invested_amounts.append(monthly_investment_contribution[i])

    # Compute the FV of the monthly investments up to this month
    # by compounding each previous contribution forward to this month:
    current_fv = 0.0
    for j, c in enumerate(invested_amounts):
        months_of_growth = (i - j)
        current_fv += c * ((1+monthly_invest_monthly_rate)**(months_of_growth))
    cumulative_investment_balance.append(current_fv)

plt.figure(figsize=(10,6))
plt.plot(range(1, months+1), cumulative_rent, label='Cumulative Rent Paid', color='red')
plt.plot(range(1, months+1), cumulative_home_cost, label='Cumulative Home Cost (no equity offset)', color='blue')
plt.plot(range(1, months+1), cumulative_investment_balance, label='Investment Balance (from monthly diff)', color='green')
plt.title("Monthly Comparison: Owning vs Renting (3 Years)")
plt.xlabel("Month")
plt.ylabel("USD")
plt.legend()
plt.grid(True)
plt.show()

