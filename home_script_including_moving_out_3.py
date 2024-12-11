import math
import matplotlib.pyplot as plt
from tabulate import tabulate

def future_value(lump_sum, annual_rate, years):
    return lump_sum * ((1 + annual_rate)**years)

def input_with_default(prompt, default):
    user_input = input(f"{prompt} (default: {default}): ").strip()
    return default if user_input == "" else user_input

def simulate_scenario(
    home_price,
    down_payment_pct,
    mortgage_rate_annual,
    mortgage_term_years,
    property_tax_rate_annual,
    maintenance_annual,
    insurance_annual,
    hoa_monthly,
    closing_costs_buy_pct,
    closing_costs_sell_pct,
    rent_current,
    rent_growth_annual,
    alt_invest_growth_annual,
    monthly_invest_growth_annual,
    home_appreciation_annual,
    tax_rate,
    property_tax_deduction_cap,
    months_live_in,           # period user lives in home
    months_rent_out,          # period user rents out the home after living
    rent_while_out,           # rent they pay elsewhere after moving out
    rent_collected_home       # rent they collect from home when renting it out
):
    # Total months considered:
    # Scenario 1: Buy -> live in for 'months_live_in' -> rent out for 'months_rent_out'
    total_months = months_live_in + months_rent_out

    # Scenario 2: Just rent the entire 'total_months'
    # We'll compare both scenarios.

    # ----------------------------
    # Derived values
    # ----------------------------
    down_payment = home_price * down_payment_pct
    loan_amount = home_price - down_payment
    closing_costs_buy = closing_costs_buy_pct * home_price

    monthly_interest_rate = mortgage_rate_annual / 12
    num_payments = mortgage_term_years * 12
    monthly_mortgage_payment = (loan_amount * monthly_interest_rate) / (1 - (1 + monthly_interest_rate)**(-num_payments))

    property_tax_annual = home_price * property_tax_rate_annual
    property_tax_monthly = property_tax_annual / 12
    maintenance_monthly = maintenance_annual / 12
    insurance_monthly = insurance_annual / 12

    # Rent changes each year for scenario where we would have just rented:
    # We'll assume the user would rent at the current rent rate if they never bought.
    monthly_rent_if_no_buy = []
    for m in range(1, total_months+1):
        year = math.ceil(m/12)
        current_rent_no_buy = rent_current * ((1 + rent_growth_annual)**(year-1))
        monthly_rent_if_no_buy.append(current_rent_no_buy)

    # Prepare to simulate month-by-month
    monthly_interest_paid = []
    monthly_principal_paid = []
    monthly_total_home_cost = []
    monthly_tax_savings = []
    monthly_investment_contribution = []
    monthly_home_value = []
    monthly_equity = []
    monthly_cash_flow_post_move = []  # Cash flow during the rental-out period

    remaining_principal = loan_amount

    alt_invest_monthly_rate = (1+alt_invest_growth_annual)**(1/12)-1
    monthly_invest_monthly_rate = (1+monthly_invest_growth_annual)**(1/12)-1

    monthly_principal_contributions = []

    # Phase 1: Living in the home (months_live_in)
    # During this phase, scenario matches the previous logic
    for m in range(1, months_live_in+1):
        # Mortgage calculations
        interest_for_this_month = remaining_principal * monthly_interest_rate
        principal_for_this_month = monthly_mortgage_payment - interest_for_this_month
        remaining_principal -= principal_for_this_month

        # Total monthly home costs when living in:
        month_home_cost = (monthly_mortgage_payment 
                           + property_tax_monthly 
                           + insurance_monthly 
                           + maintenance_monthly 
                           + hoa_monthly)

        monthly_interest_paid.append(interest_for_this_month)
        monthly_principal_paid.append(principal_for_this_month)
        monthly_total_home_cost.append(month_home_cost)

        # Tax deduction
        # For simplicity, assume full interest + property tax deductible
        monthly_deductible = interest_for_this_month + property_tax_monthly
        tax_saving_this_month = monthly_deductible * tax_rate
        monthly_tax_savings.append(tax_saving_this_month)

        # Non-principal expenses for difference investing:
        monthly_expenses_ex_interest = property_tax_monthly + insurance_monthly + maintenance_monthly + hoa_monthly
        monthly_non_principal_expenses = interest_for_this_month + monthly_expenses_ex_interest

        # Compare non-principal expenses to renting cost for the same month if we had not bought:
        # The instructions originally: 
        # difference = (non_principal_expenses) - (rent_if_no_buy_this_month), if positive invest difference
        invest_contribution = max(0, monthly_non_principal_expenses - monthly_rent_if_no_buy[m-1])
        monthly_investment_contribution.append(invest_contribution)

        monthly_principal_contributions.append(principal_for_this_month)

        # Home value and equity
        month_fraction_years = m/12
        home_value_now = home_price * ((1+home_appreciation_annual)**month_fraction_years)
        monthly_home_value.append(home_value_now)
        current_equity = home_value_now - remaining_principal
        monthly_equity.append(current_equity)

    # Phase 2: Renting out the home (months_rent_out)
    # After living in the house, the user moves out and rents another place for 'rent_while_out' monthly
    # The house is rented to tenants at 'rent_collected_home' monthly.

    for m in range(months_live_in+1, total_months+1):
        interest_for_this_month = remaining_principal * monthly_interest_rate
        principal_for_this_month = monthly_mortgage_payment - interest_for_this_month
        remaining_principal -= principal_for_this_month

        # Costs remain the same for the property:
        month_home_cost = (monthly_mortgage_payment 
                           + property_tax_monthly 
                           + insurance_monthly 
                           + maintenance_monthly 
                           + hoa_monthly)

        # But now we have rental income from the home:
        monthly_rental_income = rent_collected_home

        # The user pays rent elsewhere:
        monthly_user_rent_elsewhere = rent_while_out

        # Net cash flow during rental period:
        # House cash flow = rental income - home costs (interest+principal+tax+ins+maint+hoa)
        # But principal contributes to equity, so for pure cash flow, let's consider:
        # Actually, for consistency, let's define net monthly cost now as:
        # (house expenses) - (rental income) + (rent elsewhere)
        # The user must pay rent elsewhere and gets rental income from their property.
        # If total (house cost - rental income + rent elsewhere) > rent_if_no_buy_that_month, difference invests or not?

        # Let's still follow original investing logic:
        # The difference investing logic was for when living in the home. Now, scenario changes:
        # It's more complex. Let's just consider a similar logic:
        # The user is now comparing this scenario to simply renting for the entire period.
        # So the baseline "rent if no buy" is monthly_rent_if_no_buy[m-1].
        # The user now actually pays: (rent elsewhere + any net deficit from the property).
        # Net monthly cost to user now: 
        #   user_out_of_pocket = rent_elsewhere + (house cost - rental income)
        # If (user_out_of_pocket) > (rent_if_no_buy), difference invested.

        user_out_of_pocket = monthly_user_rent_elsewhere + (month_home_cost - monthly_rental_income)

        monthly_interest_paid.append(interest_for_this_month)
        monthly_principal_paid.append(principal_for_this_month)
        monthly_total_home_cost.append(month_home_cost) 
        # note: monthly_total_home_cost now includes entire period costs

        # Tax savings:
        monthly_deductible = interest_for_this_month + property_tax_monthly
        tax_saving_this_month = monthly_deductible * tax_rate
        monthly_tax_savings.append(tax_saving_this_month)

        # Investment difference:
        invest_contribution = max(0, user_out_of_pocket - monthly_rent_if_no_buy[m-1])
        monthly_investment_contribution.append(invest_contribution)

        monthly_principal_contributions.append(principal_for_this_month)

        # Home value and equity:
        month_fraction_years = m/12
        home_value_now = home_price * ((1+home_appreciation_annual)**month_fraction_years)
        monthly_home_value.append(home_value_now)
        current_equity = home_value_now - remaining_principal
        monthly_equity.append(current_equity)

        monthly_cash_flow_post_move.append(user_out_of_pocket)

    # After total_months, sell the home:
    home_value_after = monthly_home_value[-1]
    selling_costs = home_value_after * closing_costs_sell_pct
    final_equity = home_value_after - selling_costs - remaining_principal

    total_down_payment = down_payment
    total_monthly_paid = sum(monthly_total_home_cost)
    total_tax_savings = sum(monthly_tax_savings)

    total_buying_cost = total_down_payment + closing_costs_buy + total_monthly_paid - total_tax_savings
    net_cost_after_selling = total_buying_cost - final_equity

    total_rent_no_buy = sum(monthly_rent_if_no_buy) # If never bought and rented the whole time

    # Future value of monthly investments
    fv_monthly_invest = 0.0
    for i, c in enumerate(monthly_investment_contribution):
        months_left = (total_months - (i+1))
        fv_monthly_invest += c * ((1+monthly_invest_monthly_rate)**(months_left))

    # Opportunity cost:
    fv_down_payment = future_value(down_payment, alt_invest_growth_annual, total_months/12)
    fv_principal_opportunity = 0.0
    for i, p in enumerate(monthly_principal_contributions):
        months_left = (total_months - (i+1))
        fv_principal_opportunity += p * ((1+alt_invest_monthly_rate)**(months_left))

    fv_invest_if_rent = fv_down_payment + fv_principal_opportunity

    owning_effective_net = fv_monthly_invest - net_cost_after_selling
    renting_effective_net = fv_invest_if_rent - total_rent_no_buy

    # Yearly amortization table
    # Break down by year: principal paid, interest paid
    principal_by_year = {}
    interest_by_year = {}
    for i in range(total_months):
        year = (i // 12) + 1
        if year not in principal_by_year:
            principal_by_year[year] = 0
        if year not in interest_by_year:
            interest_by_year[year] = 0
        principal_by_year[year] += monthly_principal_paid[i]
        interest_by_year[year] += monthly_interest_paid[i]

    amort_table = []
    for y in sorted(principal_by_year.keys()):
        amort_table.append([y,
                            f"${principal_by_year[y]:,.2f}",
                            f"${interest_by_year[y]:,.2f}"])

    # Print summary
    print("\n--------------- SUMMARY AFTER PERIOD ---------------")
    print(f"Home value after {total_months/12:.1f} years: ${home_value_after:,.2f}")
    print(f"Remaining loan principal: ${remaining_principal:,.2f}")
    print(f"Selling costs: ${selling_costs:,.2f}")
    print(f"Final Equity if sold: ${final_equity:,.2f}")

    print("\n--- Costs of Owning Scenario ---")
    print(f"Down payment: ${down_payment:,.2f}")
    print(f"Closing costs on buying: ${closing_costs_buy:,.2f}")
    print(f"Total monthly paid (over entire {total_months} months): ${total_monthly_paid:,.2f}")
    print(f"Total tax savings: ${total_tax_savings:,.2f}")
    print(f"Net cost after selling: ${net_cost_after_selling:,.2f}")

    print("\n--- Rent Scenario (No Buy) ---")
    print(f"Total rent paid (for {total_months} months if never bought): ${total_rent_no_buy:,.2f}")

    print("\n--- Investment Calculations ---")
    print(f"Value of monthly difference investment: ${fv_monthly_invest:,.2f}")
    print(f"Value if renting and investing principal/down payment: ${fv_invest_if_rent:,.2f}")

    print("\n--- Final Comparison ---")
    print(f"Owning effective net position: ${owning_effective_net:,.2f}")
    print(f"Renting effective net position: ${renting_effective_net:,.2f}")

    if owning_effective_net > renting_effective_net:
        print("Conclusion: Buying and then renting out is more favorable.")
    else:
        print("Conclusion: Renting the entire period is more favorable.")

    # Print amortization table
    print("\n--- Amortization by Year ---")
    print(tabulate(amort_table, headers=["Year", "Principal Paid", "Interest Paid"], tablefmt="pretty"))

    # Plotting
    # We'll plot multiple things:
    # 1) Cumulative rent if no buy
    # 2) Cumulative costs if buy scenario
    # 3) Equity line
    # 4) Investment balance line

    cumulative_rent_no_buy = []
    cumulative_home_cost = []
    cumulative_investment_balance = []
    cumulative_equity = []

    running_rent = 0
    running_home_cost = 0
    invested_amounts = []

    for i in range(total_months):
        running_rent += monthly_rent_if_no_buy[i]
        cumulative_rent_no_buy.append(running_rent)

        running_home_cost += monthly_total_home_cost[i]
        cumulative_home_cost.append(running_home_cost)
        invested_amounts.append(monthly_investment_contribution[i])

        # Compute FV of monthly investments at this point
        current_fv = 0.0
        for j, c in enumerate(invested_amounts):
            months_of_growth = (i - j)
            current_fv += c * ((1+monthly_invest_monthly_rate)**(months_of_growth))
        cumulative_investment_balance.append(current_fv)

        cumulative_equity.append(monthly_equity[i])

    plt.figure(figsize=(10,6))
    plt.plot(range(1, total_months+1), cumulative_rent_no_buy, label='Cumulative Rent (No Buy)', color='red')
    plt.plot(range(1, total_months+1), cumulative_home_cost, label='Cumulative Home Cost (No Equity Offset)', color='blue')
    plt.plot(range(1, total_months+1), cumulative_investment_balance, label='Investment from Monthly Diff', color='green')
    plt.plot(range(1, total_months+1), cumulative_equity, label='Home Equity', color='purple')

    plt.title("Cumulative Comparison Over Time")
    plt.xlabel("Month")
    plt.ylabel("USD")
    plt.legend()
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    # Ask user for inputs
    home_price = float(input_with_default("Enter the home price (e.g. 900000)", "900000"))
    down_payment_pct = float(input_with_default("Enter the down payment percentage (e.g. 0.20 for 20%)", "0.20"))
    mortgage_rate_annual = float(input_with_default("Enter the annual mortgage interest rate (e.g. 0.06 for 6%)", "0.06"))
    mortgage_term_years = int(input_with_default("Enter the mortgage term in years (e.g. 30)", "30"))
    property_tax_rate_annual = float(input_with_default("Enter the annual property tax rate (e.g. 0.011 for 1.1%)", "0.011"))
    maintenance_annual = float(input_with_default("Enter the annual maintenance cost (e.g. 5000)", "5000"))
    insurance_annual = float(input_with_default("Enter the annual insurance cost (e.g. 3500)", "3500"))
    hoa_monthly = float(input_with_default("Enter the monthly HOA fee (e.g. 300)", "300"))
    closing_costs_buy_pct = float(input_with_default("Enter the buyer closing costs percentage (e.g. 0.04 for 4%)", "0.04"))
    closing_costs_sell_pct = float(input_with_default("Enter the selling closing costs percentage (e.g. 0.06 for 6%)", "0.06"))

    rent_current = float(input_with_default("Enter the current monthly rent (e.g. 2400)", "2400"))
    rent_growth_annual = float(input_with_default("Enter the annual rent growth rate (e.g. 0.04 for 4%)", "0.04"))

    alt_invest_growth_annual = float(input_with_default("Enter the opportunity cost annual growth rate (e.g. 0.16 for 16%)", "0.16"))
    monthly_invest_growth_annual = float(input_with_default("Enter the monthly difference investment annual growth rate (e.g. 0.15 for 15%)", "0.15"))

    home_appreciation_annual = float(input_with_default("Enter the home appreciation annual growth rate (e.g. 0.08 for 8%)", "0.08"))
    tax_rate = float(input_with_default("Enter the tax rate (e.g. 0.30 for 30%)", "0.30"))
    property_tax_deduction_cap = float(input_with_default("Enter the property tax deduction cap (e.g. 10000)", "10000"))

    months_live_in = int(input_with_default("Enter the number of months you plan to live in the home (e.g. 36)", "36"))
    months_rent_out = int(input_with_default("Enter the number of months you plan to rent out the home after living (e.g. 36)", "36"))
    rent_while_out = float(input_with_default("Enter the monthly rent you will pay elsewhere after moving out (e.g. 2500)", "2500"))
    rent_collected_home = float(input_with_default("Enter the monthly rent you expect to collect from the home (e.g. 3500)", "3500"))


    # Run the scenario simulation
    simulate_scenario(
        home_price,
        down_payment_pct,
        mortgage_rate_annual,
        mortgage_term_years,
        property_tax_rate_annual,
        maintenance_annual,
        insurance_annual,
        hoa_monthly,
        closing_costs_buy_pct,
        closing_costs_sell_pct,
        rent_current,
        rent_growth_annual,
        alt_invest_growth_annual,
        monthly_invest_growth_annual,
        home_appreciation_annual,
        tax_rate,
        property_tax_deduction_cap,
        months_live_in,
        months_rent_out,
        rent_while_out,
        rent_collected_home
    )

