import math
import matplotlib.pyplot as plt

# Prompt user for inputs:
home_price = float(input("Enter the home price (e.g. 900000): "))
down_payment_pct = float(input("Enter the down payment percentage (e.g. 0.20 for 20%): "))
mortgage_rate_annual = float(input("Enter the annual mortgage interest rate (e.g. 0.06 for 6%): "))
mortgage_term_years = int(input("Enter the mortgage term in years (e.g. 30): "))
property_tax_rate_annual = float(input("Enter the annual property tax rate (e.g. 0.011 for 1.1%): "))
maintenance_annual = float(input("Enter the annual maintenance cost (e.g. 5000): "))
insurance_annual = float(input("Enter the annual insurance cost (e.g. 3500): "))
hoa_monthly = float(input("Enter the monthly HOA fee (e.g. 300): "))
closing_costs_buy_pct = float(input("Enter the buyer closing costs percentage (e.g. 0.04 for 4%): "))
closing_costs_sell_pct = float(input("Enter the selling closing costs percentage (e.g. 0.06 for 6%): "))

rent_current = float(input("Enter the current monthly rent (e.g. 2400): "))
rent_growth_annual = float(input("Enter the annual rent growth rate (e.g. 0.04 for 4%): "))

alt_invest_growth_annual = float(input("Enter the opportunity cost annual growth rate (e.g. 0.16 for 16%): "))
monthly_invest_growth_annual = float(input("Enter the monthly difference investment annual growth rate (e.g. 0.15 for 15%): "))

home_appreciation_annual = float(input("Enter the home appreciation annual growth rate (e.g. 0.08 for 8%): "))
tax_rate = float(input("Enter the tax rate (e.g. 0.30 for 30%): "))
property_tax_deduction_cap = float(input("Enter the property tax deduction cap (e.g. 10000): "))
months = int(input("Enter the number of months to consider (e.g. 36 for 3 years): "))

# Derived values
down_payment = home_price * down_payment_pct
loan_amount = home_price - down_payment
closing_costs_buy = closing_costs_buy_pct * home_price

monthly_interest_rate = mortgage_rate_annual / 12
num_payments = mortgage_term_years * 12
monthly_mortgage_payment = (loan_amount * monthly_interest_rate) / (1 - (1 + monthly_interest_rate)**(-num_payments))

# Monthly costs for owning
property_tax_annual = home_price * property_tax_rate_annual
property_tax_monthly = property_tax_annual / 12
maintenance_monthly = maintenance_annual / 12
insurance_monthly = insurance_annual / 12

# Rent changes each year
monthly_rent = []
for m in range(1, months+1):
    year = math.ceil(m/12)
    current_rent = rent_current * ((1 + rent_growth_annual)**(year-1))
    monthly_rent.append(current_rent)

monthly_interest_paid = []
monthly_principal_paid = []
monthly_total_home_cost = []
monthly_tax_savings = []
monthly_investment_contribution = []
monthly_home_value = []
monthly_equity = []

remaining_principal = loan_amount

alt_invest_monthly_rate = (1+alt_invest_growth_annual)**(1/12)-1
monthly_invest_monthly_rate = (1+monthly_invest_growth_annual)**(1/12)-1

monthly_principal_contributions = []

for m in range(1, months+1):
    # Interest portion this month
    interest_for_this_month = remaining_principal * monthly_interest_rate
    principal_for_this_month = monthly_mortgage_payment - interest_for_this_month
    remaining_principal -= principal_for_this_month

    # Total monthly home costs:
    month_home_cost = (monthly_mortgage_payment 
                       + property_tax_monthly 
                       + insurance_monthly 
                       + maintenance_monthly 
                       + hoa_monthly)

    monthly_interest_paid.append(interest_for_this_month)
    monthly_principal_paid.append(principal_for_this_month)
    monthly_total_home_cost.append(month_home_cost)

    # Tax deduction (assuming full mortgage interest & property tax are deductible):
    monthly_deductible = interest_for_this_month + property_tax_monthly
    tax_saving_this_month = monthly_deductible * tax_rate
    monthly_tax_savings.append(tax_saving_this_month)

    # Calculate monthly difference investment:
    # Non-principal expenses = interest + property tax + insurance + maintenance + HOA
    monthly_expenses_ex_interest = property_tax_monthly + insurance_monthly + maintenance_monthly + hoa_monthly
    monthly_non_principal_expenses = interest_for_this_month + monthly_expenses_ex_interest
    invest_contribution = max(0, monthly_non_principal_expenses - monthly_rent[m-1])
    monthly_investment_contribution.append(invest_contribution)

    monthly_principal_contributions.append(principal_for_this_month)

    # Calculate monthly home value:
    month_fraction_years = m/12
    home_value_now = home_price * ((1+home_appreciation_annual)**month_fraction_years)
    monthly_home_value.append(home_value_now)
    # Equity = home value now - remaining principal
    current_equity = home_value_now - remaining_principal
    monthly_equity.append(current_equity)

# Final values after months:
home_value_after = monthly_home_value[-1]
selling_costs = home_value_after * closing_costs_sell_pct
final_equity = home_value_after - selling_costs - remaining_principal

total_down_payment = down_payment
total_monthly_paid = sum(monthly_total_home_cost)
total_tax_savings = sum(monthly_tax_savings)

total_buying_cost = total_down_payment + closing_costs_buy + total_monthly_paid - total_tax_savings
net_cost_after_selling = total_buying_cost - final_equity

total_rent_paid = sum(monthly_rent)

def future_value(lump_sum, annual_rate, years):
    return lump_sum * ((1 + annual_rate)**years)

# Future value of monthly investments at monthly_invest_monthly_rate:
fv_monthly_invest = 0.0
for i, c in enumerate(monthly_investment_contribution):
    months_left = (months - (i+1))
    fv_monthly_invest += c * ((1+monthly_invest_monthly_rate)**(months_left))

# Opportunity cost:
# Down payment + principal at 16% YOY
fv_down_payment = future_value(down_payment, alt_invest_growth_annual, months/12)

fv_principal_opportunity = 0.0
for i, p in enumerate(monthly_principal_contributions):
    months_left = (months - (i+1))
    fv_principal_opportunity += p * ((1+alt_invest_monthly_rate)**(months_left))

fv_invest_if_rent = fv_down_payment + fv_principal_opportunity

owning_effective_net = fv_monthly_invest - net_cost_after_selling
renting_effective_net = fv_invest_if_rent - total_rent_paid

# Print summary
print("\n--------------- SUMMARY AFTER PERIOD ---------------")
print(f"Home value after {months/12:.1f} years: ${home_value_after:,.2f}")
print(f"Remaining loan principal: ${remaining_principal:,.2f}")
print(f"Selling costs: ${selling_costs:,.2f}")
print(f"Final Equity if sold: ${final_equity:,.2f}")

print("\n--- Costs of Owning ---")
print(f"Down payment: ${down_payment:,.2f}")
print(f"Closing costs on buying: ${closing_costs_buy:,.2f}")
print(f"Total monthly paid: ${total_monthly_paid:,.2f}")
print(f"Total tax savings: ${total_tax_savings:,.2f}")
print(f"Net cost after selling: ${net_cost_after_selling:,.2f}")

print("\n--- Rent Scenario ---")
print(f"Total rent paid: ${total_rent_paid:,.2f}")

print("\n--- Investment Calculations ---")
print(f"Value of monthly difference investment (at {monthly_invest_growth_annual*100:.2f}% YOY): ${fv_monthly_invest:,.2f}")
print(f"Value if renting and investing principal/down payment (at {alt_invest_growth_annual*100:.2f}% YOY): ${fv_invest_if_rent:,.2f}")

print("\n--- Final Comparison ---")
print(f"Owning effective net position: ${owning_effective_net:,.2f}")
print(f"Renting effective net position: ${renting_effective_net:,.2f}")

if owning_effective_net > renting_effective_net:
    print("Conclusion: Buying is more favorable.")
else:
    print("Conclusion: Renting is more favorable.")

# Plot
cumulative_rent = []
cumulative_home_cost = []
cumulative_investment_balance = []
cumulative_equity = []

running_rent = 0
running_home_cost = 0
invested_amounts = []

for i in range(months):
    running_rent += monthly_rent[i]
    cumulative_rent.append(running_rent)

    running_home_cost += monthly_total_home_cost[i]
    cumulative_home_cost.append(running_home_cost)
    invested_amounts.append(monthly_investment_contribution[i])

    # Compute FV of monthly investments at this point
    current_fv = 0.0
    for j, c in enumerate(invested_amounts):
        months_of_growth = (i - j)
        current_fv += c * ((1+monthly_invest_monthly_rate)**(months_of_growth))
    cumulative_investment_balance.append(current_fv)

    # Equity over time
    cumulative_equity.append(monthly_equity[i])

plt.figure(figsize=(10,6))
plt.plot(range(1, months+1), cumulative_rent, label='Cumulative Rent Paid', color='red')
plt.plot(range(1, months+1), cumulative_home_cost, label='Cumulative Home Cost (No Equity Offset)', color='blue')
plt.plot(range(1, months+1), cumulative_investment_balance, label='Investment from Monthly Difference', color='green')
plt.plot(range(1, months+1), cumulative_equity, label='Home Equity', color='purple')

plt.title("Monthly Comparison Over Time")
plt.xlabel("Month")
plt.ylabel("USD")
plt.legend()
plt.grid(True)
plt.show()

