import matplotlib.pyplot as plt
from tabulate import tabulate
from financial_utils import (future_value, calculate_future_monthly_investments, 
                           project_rent_values)
from property_analysis import PropertyCosts
from rental_analysis import RentalScenario

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
    months_live_in,
    months_rent_out,
    rent_while_out,
    rent_collected_home
):
    # Initialize property costs
    property_costs = PropertyCosts(
        home_price, down_payment_pct, mortgage_rate_annual, mortgage_term_years,
        property_tax_rate_annual, maintenance_annual, insurance_annual, hoa_monthly
    )

    # Initialize rental scenario
    rental_scenario = RentalScenario(
        property_costs, months_live_in, months_rent_out,
        rent_while_out, rent_collected_home, rent_growth_annual
    )

    total_months = months_live_in + months_rent_out
    closing_costs_buy = closing_costs_buy_pct * home_price
    
    # Track monthly values
    monthly_interest_paid = []
    monthly_principal_paid = []
    monthly_total_home_cost = []
    monthly_tax_savings = []
    monthly_investment_contribution = []
    monthly_home_value = []
    monthly_equity = []
    monthly_cash_flow_post_move = []

    remaining_principal = property_costs.loan_amount
    alt_invest_monthly_rate = (1 + alt_invest_growth_annual)**(1/12) - 1
    monthly_invest_monthly_rate = (1 + monthly_invest_growth_annual)**(1/12) - 1

    # Process each month
    for m in range(1, total_months + 1):
        # Calculate mortgage split
        principal_paid, interest_paid = property_costs.calculate_monthly_mortgage_split(
            remaining_principal, mortgage_rate_annual)
        remaining_principal -= principal_paid

        # Get monthly costs and cash flow
        month_home_cost = property_costs.get_monthly_costs()
        cash_flow = rental_scenario.calculate_monthly_cashflow(m)

        # Tax calculations
        monthly_deductible = interest_paid + property_costs.property_tax
        tax_saving_this_month = monthly_deductible * tax_rate

        # Investment calculations
        rent_if_no_buy = rental_scenario.monthly_rent_if_no_buy[m-1]
        if m <= months_live_in:
            monthly_non_principal_expenses = (month_home_cost - principal_paid)
            invest_contribution = max(0, monthly_non_principal_expenses - rent_if_no_buy)
        else:
            invest_contribution = max(0, -cash_flow - rent_if_no_buy)

        # Home value and equity calculations
        month_fraction_years = m/12
        home_value_now = home_price * ((1 + home_appreciation_annual)**month_fraction_years)
        current_equity = home_value_now - remaining_principal

        # Store monthly values
        monthly_interest_paid.append(interest_paid)
        monthly_principal_paid.append(principal_paid)
        monthly_total_home_cost.append(month_home_cost)
        monthly_tax_savings.append(tax_saving_this_month)
        monthly_investment_contribution.append(invest_contribution)
        monthly_home_value.append(home_value_now)
        monthly_equity.append(current_equity)
        if m > months_live_in:
            monthly_cash_flow_post_move.append(-cash_flow)

    # Calculate final results
    home_value_after = monthly_home_value[-1]
    selling_costs = home_value_after * closing_costs_sell_pct
    final_equity = home_value_after - selling_costs - remaining_principal

    total_monthly_paid = sum(monthly_total_home_cost)
    total_tax_savings = sum(monthly_tax_savings)
    total_rent_no_buy = sum(rental_scenario.monthly_rent_if_no_buy)

    # Investment calculations
    fv_monthly_invest = calculate_future_monthly_investments(
        monthly_investment_contribution, monthly_invest_monthly_rate, total_months)
    
    fv_down_payment = future_value(property_costs.down_payment, 
                                 alt_invest_growth_annual, total_months/12)
    fv_principal_opportunity = calculate_future_monthly_investments(
        monthly_principal_paid, alt_invest_monthly_rate, total_months)

    # Final comparisons
    total_buying_cost = (property_costs.down_payment + closing_costs_buy + 
                        total_monthly_paid - total_tax_savings)
    net_cost_after_selling = total_buying_cost - final_equity
    fv_invest_if_rent = fv_down_payment + fv_principal_opportunity

    owning_effective_net = fv_monthly_invest - net_cost_after_selling
    renting_effective_net = fv_invest_if_rent - total_rent_no_buy

    # Display results
    display_results(
        home_value_after, remaining_principal, selling_costs, final_equity,
        property_costs.down_payment, closing_costs_buy, total_monthly_paid,
        total_tax_savings, net_cost_after_selling, total_rent_no_buy,
        fv_monthly_invest, fv_invest_if_rent, owning_effective_net,
        renting_effective_net, monthly_principal_paid, monthly_interest_paid,
        total_months
    )

    # Create and display plots
    create_comparison_plots(
        total_months, rental_scenario.monthly_rent_if_no_buy,
        monthly_total_home_cost, monthly_investment_contribution,
        monthly_equity, monthly_invest_monthly_rate
    )

def display_results(
    home_value_after, remaining_principal, selling_costs, final_equity,
    down_payment, closing_costs_buy, total_monthly_paid, total_tax_savings,
    net_cost_after_selling, total_rent_no_buy, fv_monthly_invest,
    fv_invest_if_rent, owning_effective_net, renting_effective_net,
    monthly_principal_paid, monthly_interest_paid, total_months
):
    # Print summary
    print("\n--------------- SUMMARY AFTER PERIOD ---------------")
    print(f"Home value after {total_months/12:.1f} years: ${home_value_after:,.2f}")
    print(f"Remaining loan principal: ${remaining_principal:,.2f}")
    print(f"Selling costs: ${selling_costs:,.2f}")
    print(f"Final Equity if sold: ${final_equity:,.2f}")

    print("\n--- Costs of Owning Scenario ---")
    print(f"Down payment: ${down_payment:,.2f}")
    print(f"Closing costs on buying: ${closing_costs_buy:,.2f}")
    print(f"Total monthly paid: ${total_monthly_paid:,.2f}")
    print(f"Total tax savings: ${total_tax_savings:,.2f}")
    print(f"Net cost after selling: ${net_cost_after_selling:,.2f}")

    print("\n--- Rent Scenario (No Buy) ---")
    print(f"Total rent paid: ${total_rent_no_buy:,.2f}")

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
    print_amortization_table(monthly_principal_paid, monthly_interest_paid)

def print_amortization_table(monthly_principal_paid, monthly_interest_paid):
    """Print amortization schedule by year."""
    principal_by_year = {}
    interest_by_year = {}
    
    # Group payments by year (1-based)
    for i, (principal, interest) in enumerate(zip(monthly_principal_paid, monthly_interest_paid)):
        year = (i // 12) + 1  # Convert 0-based month to 1-based year
        if year not in principal_by_year:
            principal_by_year[year] = 0
            interest_by_year[year] = 0
        principal_by_year[year] += principal
        interest_by_year[year] += interest

    # Create table rows
    amort_table = []
    for year in sorted(principal_by_year.keys()):
        amort_table.append([
            year,
            f"${principal_by_year[year]:,.2f}",
            f"${interest_by_year[year]:,.2f}"
        ])
    
    print("\n--- Amortization by Year ---")
    print(tabulate(amort_table, 
                  headers=["Year", "Principal Paid", "Interest Paid"], 
                  tablefmt="pretty"))

def create_comparison_plots(
    total_months, monthly_rent_no_buy, monthly_total_home_cost,
    monthly_investment_contribution, monthly_equity, monthly_invest_rate
):
    cumulative_rent_no_buy = []
    cumulative_home_cost = []
    cumulative_investment_balance = []
    
    running_rent = 0
    running_home_cost = 0
    invested_amounts = []

    for i in range(total_months):
        running_rent += monthly_rent_no_buy[i]
        running_home_cost += monthly_total_home_cost[i]
        invested_amounts.append(monthly_investment_contribution[i])

        current_fv = calculate_future_monthly_investments(
            invested_amounts, monthly_invest_rate, i+1)

        cumulative_rent_no_buy.append(running_rent)
        cumulative_home_cost.append(running_home_cost)
        cumulative_investment_balance.append(current_fv)

    plt.figure(figsize=(10,6))
    months = range(1, total_months+1)
    plt.plot(months, cumulative_rent_no_buy, label='Cumulative Rent (No Buy)', color='red')
    plt.plot(months, cumulative_home_cost, label='Cumulative Home Cost', color='blue')
    plt.plot(months, cumulative_investment_balance, label='Investment from Monthly Diff', color='green')
    plt.plot(months, monthly_equity, label='Home Equity', color='purple')

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