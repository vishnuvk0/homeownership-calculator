from financial_utils import (future_value, calculate_future_monthly_investments)
from property_analysis import PropertyCosts
from rental_analysis import RentalScenario
from display_utils import (display_results, create_comparison_plots, 
                         display_monthly_payments)

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
    property_costs.mortgage_rate_annual = mortgage_rate_annual

    # Initialize rental scenario with proper rent values even when not renting out
    rental_scenario = RentalScenario(
        property_costs, 
        months_live_in, 
        months_rent_out,
        rent_while_out if months_rent_out > 0 else 0,  # Only set if renting out
        rent_collected_home if months_rent_out > 0 else 0,  # Only set if renting out
        rent_growth_annual,
        rent_current
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

    remaining_principal = property_costs.loan_amount
    alt_invest_monthly_rate = (1 + alt_invest_growth_annual)**(1/12) - 1
    monthly_invest_monthly_rate = (1 + monthly_invest_growth_annual)**(1/12) - 1

    # Calculate monthly savings for buying vs renting
    monthly_savings_buy = 0  # Initialize savings variables
    monthly_savings_rent = 0
    
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
        monthly_deductible = min(interest_paid + property_costs.property_tax_annual/12,
                               property_tax_deduction_cap/12)
        tax_saving_this_month = monthly_deductible * tax_rate
    
        # Calculate monthly savings
        if m <= months_live_in:
            # During living in period, savings is the difference between rent we would pay and home costs
            monthly_savings_buy = rental_scenario.monthly_rent_if_no_buy[m-1] - month_home_cost
            monthly_savings_rent = 0
        else:
            # During rental period, savings includes rental income minus costs and rent paid elsewhere
            monthly_savings_buy = cash_flow
            monthly_savings_rent = 0

        # Investment calculations
        monthly_total_cost = (principal_paid + interest_paid + 
                             property_costs.property_tax_annual/12 + 
                             property_costs.maintenance_annual/12 + 
                             property_costs.insurance_annual/12 + 
                             property_costs.hoa_monthly - 
                             tax_saving_this_month)
        invest_contribution = max(0, monthly_total_cost - rental_scenario.monthly_rent_if_no_buy[m-1])

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

    # Calculate final results
    home_value_after = monthly_home_value[-1]
    selling_costs = home_value_after * closing_costs_sell_pct
    final_equity = home_value_after - selling_costs - remaining_principal

    total_monthly_paid = sum(monthly_total_home_cost)
    total_tax_savings = sum(monthly_tax_savings)
    total_rent_no_buy = sum(rental_scenario.monthly_rent_if_no_buy[:months_live_in])
    if months_rent_out > 0:
        total_rent_no_buy += sum(rental_scenario.monthly_rent_if_no_buy[months_live_in:])

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
        total_months, rental_scenario
    )

    # Create and display plots
    create_comparison_plots(
        total_months, rental_scenario.monthly_rent_if_no_buy,
        monthly_total_home_cost, monthly_investment_contribution,
        monthly_equity, monthly_invest_monthly_rate
    )

    # Calculate monthly mortgage payment for display
    monthly_payment = property_costs.calculate_monthly_payment(mortgage_rate_annual)
    
    # Display monthly payments with the calculated savings
    display_monthly_payments(
        property_costs,
        monthly_payment,
        monthly_savings_buy,
        monthly_savings_rent,
        rent_while_out,
        mortgage_rate_annual,
        rent_collected_home
    ) 