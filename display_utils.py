import matplotlib.pyplot as plt
from tabulate import tabulate
from financial_utils import calculate_future_monthly_investments

def display_results(
    home_value_after, remaining_principal, selling_costs, final_equity,
    down_payment, closing_costs_buy, total_monthly_paid, total_tax_savings,
    net_cost_after_selling, total_rent_no_buy, fv_monthly_invest,
    fv_invest_if_rent, owning_effective_net, renting_effective_net,
    monthly_principal_paid, monthly_interest_paid, total_months
):
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

    print_amortization_table(monthly_principal_paid, monthly_interest_paid)

def print_amortization_table(monthly_principal_paid, monthly_interest_paid):
    """Print amortization schedule by year."""
    principal_by_year = {}
    interest_by_year = {}
    
    for i, (principal, interest) in enumerate(zip(monthly_principal_paid, monthly_interest_paid)):
        year = (i // 12) + 1
        if year not in principal_by_year:
            principal_by_year[year] = 0
            interest_by_year[year] = 0
        principal_by_year[year] += principal
        interest_by_year[year] += interest

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

def display_monthly_payments(
    property_costs,
    rental_scenario,
    tax_rate,
    months_live_in,
    months_rent_out,
    rent_while_out
):
    print("\n--------------- MONTHLY PAYMENT BREAKDOWN ---------------")
    
    monthly_principal, monthly_interest = property_costs.calculate_monthly_mortgage_split(
        property_costs.loan_amount, property_costs.mortgage_rate_annual)
    
    monthly_tax_insurance = (property_costs.property_tax + 
                           property_costs.insurance_annual/12)
    monthly_maintenance = property_costs.maintenance_annual/12
    monthly_hoa = property_costs.hoa_monthly
    
    monthly_deductible = monthly_interest + property_costs.property_tax
    monthly_tax_savings = monthly_deductible * tax_rate

    total_monthly = (monthly_principal + monthly_interest + monthly_tax_insurance + 
                    monthly_maintenance + monthly_hoa - monthly_tax_savings)

    print("\nWHILE LIVING IN THE HOUSE (First {} months):".format(months_live_in))
    payment_breakdown = [
        ["Principal", f"${monthly_principal:,.2f}"],
        ["Interest", f"${monthly_interest:,.2f}"],
        ["Property Tax + Insurance", f"${monthly_tax_insurance:,.2f}"],
        ["Maintenance", f"${monthly_maintenance:,.2f}"],
        ["HOA", f"${monthly_hoa:,.2f}"],
        ["Tax Savings", f"-${monthly_tax_savings:,.2f}"],
        ["", ""],
        ["Total Monthly Payment", f"${total_monthly:,.2f}"]
    ]
    print(tabulate(payment_breakdown, tablefmt="pretty"))

    if months_rent_out > 0:
        print("\nAFTER MOVING OUT (Next {} months):".format(months_rent_out))
        rental_income = rental_scenario.rent_collected_home
        new_payment_breakdown = [
            ["Original Monthly Payment", f"${total_monthly:,.2f}"],
            ["Rental Income", f"-${rental_income:,.2f}"],
            ["Your New Rent Payment", f"${rent_while_out:,.2f}"],
            ["", ""],
            ["Net Monthly Payment", 
             f"${total_monthly - rental_income + rent_while_out:,.2f}"]
        ]
        print(tabulate(new_payment_breakdown, tablefmt="pretty"))

    print("\nIF RENTING ONLY:")
    initial_rent = rental_scenario.monthly_rent_if_no_buy[0]
    final_rent = rental_scenario.monthly_rent_if_no_buy[-1]
    rent_breakdown = [
        ["Initial Monthly Rent", f"${initial_rent:,.2f}"],
        ["Final Monthly Rent", f"${final_rent:,.2f}"]
    ]
    print(tabulate(rent_breakdown, tablefmt="pretty")) 