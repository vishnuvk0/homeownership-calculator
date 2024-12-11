from simulation import simulate_scenario

def input_with_default(prompt, default, value_type=float):
    """Get user input with a default value and type conversion."""
    user_input = input(f"{prompt} (default: {default}): ").strip()
    try:
        return value_type(user_input) if user_input else value_type(default)
    except ValueError:
        print(f"Invalid input. Using default value: {default}")
        return value_type(default)

def main():
    # Property details
    home_price = input_with_default("Enter the home price (e.g. 900000)", "900000")
    down_payment_pct = input_with_default("Enter the down payment percentage (e.g. 0.20 for 20%)", "0.20")
    mortgage_rate_annual = input_with_default("Enter the annual mortgage interest rate (e.g. 0.06 for 6%)", "0.06")
    mortgage_term_years = input_with_default("Enter the mortgage term in years (e.g. 30)", "30", int)
    property_tax_rate_annual = input_with_default("Enter the annual property tax rate (e.g. 0.011 for 1.1%)", "0.011")
    maintenance_annual = input_with_default("Enter the annual maintenance cost (e.g. 5000)", "5000")
    insurance_annual = input_with_default("Enter the annual insurance cost (e.g. 3500)", "3500")
    hoa_monthly = input_with_default("Enter the monthly HOA fee (e.g. 300)", "300")

    # Transaction costs
    closing_costs_buy_pct = input_with_default("Enter the buyer closing costs percentage (e.g. 0.04 for 4%)", "0.04")
    closing_costs_sell_pct = input_with_default("Enter the selling closing costs percentage (e.g. 0.06 for 6%)", "0.06")

    # Rent details
    rent_current = input_with_default("Enter your current monthly rent (e.g. 2400)", "2400")
    rent_growth_annual = input_with_default("Enter the annual rent growth rate (e.g. 0.04 for 4%)", "0.04")

    # Investment rates
    alt_invest_growth_annual = input_with_default("Enter the opportunity cost annual growth rate (e.g. 0.16 for 16%)", "0.16")
    monthly_invest_growth_annual = input_with_default("Enter the monthly difference investment annual growth rate (e.g. 0.15 for 15%)", "0.15")

    # Market conditions
    home_appreciation_annual = input_with_default("Enter the home appreciation annual growth rate (e.g. 0.08 for 8%)", "0.08")
    tax_rate = input_with_default("Enter the tax rate (e.g. 0.30 for 30%)", "0.30")
    property_tax_deduction_cap = input_with_default("Enter the property tax deduction cap (e.g. 10000)", "10000")

    # Living situation
    months_live_in = input_with_default("Enter the number of months you plan to live in the home (e.g. 36)", "36", int)
    months_rent_out = input_with_default("Enter the number of months you plan to rent out the home after living (e.g. 36)", "36", int)
    
    # Only ask for these values if months_rent_out > 0
    if months_rent_out > 0:
        rent_while_out = input_with_default("Enter the monthly rent you will pay elsewhere after moving out (e.g. 2500)", "2500")
        rent_collected_home = input_with_default("Enter the monthly rent you expect to collect from the home (e.g. 3500)", "3500")
    else:
        rent_while_out = 0
        rent_collected_home = 0

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

if __name__ == "__main__":
    main()