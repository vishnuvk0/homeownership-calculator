from financial_utils import (future_value, calculate_future_monthly_investments)
from property_analysis import PropertyCosts
from rental_analysis import RentalScenario

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

    # Initialize rental scenario
    rental_scenario = RentalScenario(
        property_costs, 
        months_live_in, 
        months_rent_out,
        rent_while_out if months_rent_out > 0 else 0,
        rent_collected_home if months_rent_out > 0 else 0,
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
    monthly_rental_income = []
    monthly_rent_paid_out = []
    
    # Track cumulative values for graphs
    cumulative_rent_no_buy = []
    cumulative_home_cost = []
    cumulative_investment_balance = []
    cumulative_equity = []

    remaining_principal = property_costs.loan_amount
    alt_invest_monthly_rate = (1 + alt_invest_growth_annual)**(1/12) - 1
    monthly_invest_monthly_rate = (1 + monthly_invest_growth_annual)**(1/12) - 1

    running_rent = 0
    running_home_cost = 0
    invested_amounts = []
    
    # Track yearly tax deductions
    yearly_tax_data = {}
    
    # Process each month
    for m in range(1, total_months + 1):
        year = (m - 1) // 12 + 1
        if year not in yearly_tax_data:
            yearly_tax_data[year] = {
                'mortgage_interest': 0,
                'property_tax': 0,
                'total_deductions': 0,
                'tax_savings': 0
            }

        # Calculate mortgage split
        principal_paid, interest_paid = property_costs.calculate_monthly_mortgage_split(
            remaining_principal, mortgage_rate_annual)
        remaining_principal -= principal_paid

        # Get monthly costs and cash flow
        month_home_cost = property_costs.get_monthly_costs()
        cash_flow = rental_scenario.calculate_monthly_cashflow(m)

        # Tax calculations - accumulate yearly data
        yearly_tax_data[year]['mortgage_interest'] += interest_paid
        yearly_tax_data[year]['property_tax'] += property_costs.property_tax_annual / 12
        
        # Calculate monthly tax savings based on current month's deductions
        monthly_deductible = min(interest_paid + property_costs.property_tax_annual/12,
                               property_tax_deduction_cap/12)
        tax_saving_this_month = monthly_deductible * tax_rate

        # Calculate rental income and costs for this month
        if m <= months_live_in:
            rental_income = 0
            rent_paid = 0
        else:
            rental_income = rent_collected_home * (1 + rent_growth_annual)**((m-months_live_in)/12)
            rent_paid = rent_while_out * (1 + rent_growth_annual)**((m-months_live_in)/12)

        monthly_rental_income.append(float(rental_income))
        monthly_rent_paid_out.append(float(rent_paid))

        # Investment calculations
        monthly_total_cost = (month_home_cost - tax_saving_this_month)
        if m <= months_live_in:
            # During living period, invest the difference if monthly costs > rent
            invest_contribution = max(0, monthly_total_cost - rental_scenario.monthly_rent_if_no_buy[m-1])
        else:
            # During rental period, invest the difference if net costs > rent would have been
            net_cost = monthly_total_cost - rental_income + rent_paid
            invest_contribution = max(0, net_cost - rental_scenario.monthly_rent_if_no_buy[m-1])

        # Home value and equity calculations
        month_fraction_years = m/12
        home_value_now = home_price * ((1 + home_appreciation_annual)**month_fraction_years)
        current_equity = home_value_now - remaining_principal

        # Store monthly values
        monthly_interest_paid.append(float(interest_paid))
        monthly_principal_paid.append(float(principal_paid))
        monthly_total_home_cost.append(float(month_home_cost))
        monthly_tax_savings.append(float(tax_saving_this_month))
        monthly_investment_contribution.append(float(invest_contribution))
        monthly_home_value.append(float(home_value_now))
        monthly_equity.append(float(current_equity))

        # Calculate cumulative values for graphs
        running_rent += rental_scenario.monthly_rent_if_no_buy[m-1]
        running_home_cost += month_home_cost
        invested_amounts.append(invest_contribution)
        
        # Compute future value of investments at this point
        current_fv = 0.0
        for j, c in enumerate(invested_amounts):
            months_of_growth = (m - j - 1)
            current_fv += c * ((1 + monthly_invest_monthly_rate)**(months_of_growth))
            
        cumulative_rent_no_buy.append(float(running_rent))
        cumulative_home_cost.append(float(running_home_cost))
        cumulative_investment_balance.append(float(current_fv))
        cumulative_equity.append(float(current_equity))

    # Calculate total rental values
    total_rental_income = sum(monthly_rental_income)
    total_rent_paid_out = sum(monthly_rent_paid_out)

    # After the loop, calculate yearly tax savings
    total_mortgage_interest = 0
    total_property_tax = 0
    total_deductions = 0
    total_tax_savings = 0
    yearly_savings = []

    for year, data in yearly_tax_data.items():
        # Calculate deductions considering property tax cap
        property_tax_deduction = min(data['property_tax'], property_tax_deduction_cap)
        total_deductions_this_year = data['mortgage_interest'] + property_tax_deduction
        tax_savings_this_year = total_deductions_this_year * tax_rate
        
        yearly_savings.append({
            'year': year,
            'mortgage_interest': data['mortgage_interest'],
            'property_tax': data['property_tax'],
            'total_deductions': total_deductions_this_year,
            'tax_savings': tax_savings_this_year
        })
        
        total_mortgage_interest += data['mortgage_interest']
        total_property_tax += data['property_tax']
        total_deductions += total_deductions_this_year
        total_tax_savings += tax_savings_this_year

    # Calculate monthly costs breakdown
    monthly_costs = {
        'mortgage': property_costs.calculate_monthly_payment(mortgage_rate_annual),
        'property_tax': property_costs.property_tax_annual / 12,
        'insurance': property_costs.insurance_annual / 12,
        'maintenance': property_costs.maintenance_annual / 12,
        'hoa': property_costs.hoa_monthly,
        'total': property_costs.get_monthly_costs(),
        'tax_savings': total_tax_savings / total_months  # Average monthly tax savings
    }

    # Update rental analysis with monthly values
    rental_analysis = {
        'monthly_rent_collected': rent_collected_home,
        'monthly_rent_paid': rent_while_out,
        'monthly_net_income': rent_collected_home - rent_while_out,
        'total_months_renting': months_rent_out,
        'total_rental_income': total_rental_income,
        'total_rent_paid_out': total_rent_paid_out,
        'net_rental_income': total_rental_income - total_rent_paid_out
    }

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

    owning_effective_net = fv_monthly_invest - net_cost_after_selling + total_rental_income - total_rent_paid_out
    renting_effective_net = fv_invest_if_rent - total_rent_no_buy

    # Calculate monthly mortgage payment
    monthly_payment = property_costs.calculate_monthly_payment(mortgage_rate_annual)

    # Prepare amortization data
    amortization_data = []
    for i in range(total_months):
        year = (i // 12) + 1
        if i % 12 == 0:  # Only add yearly data
            amortization_data.append({
                "year": year,
                "principal_paid": sum(monthly_principal_paid[i:i+12]),
                "interest_paid": sum(monthly_interest_paid[i:i+12])
            })

    # Return results as a dictionary
    return {
        "summary": {
            "home_value_after": float(home_value_after),
            "remaining_principal": float(remaining_principal),
            "selling_costs": float(selling_costs),
            "final_equity": float(final_equity)
        },
        "costs": {
            "down_payment": float(property_costs.down_payment),
            "closing_costs_buy": float(closing_costs_buy),
            "total_monthly_paid": float(total_monthly_paid),
            "total_tax_savings": float(total_tax_savings),
            "net_cost_after_selling": float(net_cost_after_selling)
        },
        "rent_comparison": {
            "total_rent_no_buy": float(total_rent_no_buy),
            "monthly_payment": float(monthly_payment),
            "current_monthly_rent": float(rent_current),
            "payment_difference": float(monthly_payment - rent_current)
        },
        "investment_analysis": {
            "down_payment_investment": float(fv_down_payment),
            "monthly_investment_value": float(fv_monthly_invest),
            "rent_investment_value": float(fv_invest_if_rent)
        },
        "rental_analysis": {
            "total_rental_income": float(total_rental_income),
            "total_rent_paid_out": float(total_rent_paid_out),
            "net_rental_income": float(total_rental_income - total_rent_paid_out)
        },
        "final_comparison": {
            "owning_effective_net": float(owning_effective_net),
            "renting_effective_net": float(renting_effective_net),
            "recommendation": "Buying and then renting out is more favorable" if owning_effective_net > renting_effective_net else "Renting the entire period is more favorable"
        },
        "graph_data": {
            "months": list(range(1, total_months + 1)),
            "cumulative_rent": [float(x) for x in cumulative_rent_no_buy],
            "cumulative_home_cost": [float(x) for x in cumulative_home_cost],
            "cumulative_investment": [float(x) for x in cumulative_investment_balance],
            "cumulative_equity": [float(x) for x in cumulative_equity]
        },
        "monthly_data": {
            "interest_paid": [float(x) for x in monthly_interest_paid],
            "principal_paid": [float(x) for x in monthly_principal_paid],
            "total_home_cost": [float(x) for x in monthly_total_home_cost],
            "tax_savings": [float(x) for x in monthly_tax_savings],
            "investment_contribution": [float(x) for x in monthly_investment_contribution],
            "home_value": [float(x) for x in monthly_home_value],
            "equity": [float(x) for x in monthly_equity],
            "rental_income": [float(x) for x in monthly_rental_income],
            "rent_paid_out": [float(x) for x in monthly_rent_paid_out],
            "rent_if_no_buy": [float(x) for x in rental_scenario.monthly_rent_if_no_buy]
        },
        "amortization": amortization_data,
        "monthly_costs": monthly_costs,
        "rental_analysis": rental_analysis,
        "tax_analysis": {
            "yearly_savings": yearly_savings,
            "total_mortgage_interest": total_mortgage_interest,
            "total_property_tax": total_property_tax,
            "total_deductions": total_deductions,
            "total_tax_savings": total_tax_savings
        }
    }