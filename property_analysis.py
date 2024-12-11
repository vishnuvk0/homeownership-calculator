from financial_utils import calculate_mortgage_payment

class PropertyCosts:
    def __init__(self, home_price, down_payment_pct, mortgage_rate_annual, 
                 mortgage_term_years, property_tax_rate_annual, maintenance_annual,
                 insurance_annual, hoa_monthly):
        self.home_price = home_price
        self.down_payment = home_price * down_payment_pct
        self.loan_amount = home_price - self.down_payment
        
        # Monthly costs
        self.mortgage_payment = calculate_mortgage_payment(
            self.loan_amount, mortgage_rate_annual, mortgage_term_years)
        self.property_tax = (home_price * property_tax_rate_annual) / 12
        self.maintenance = maintenance_annual / 12
        self.insurance = insurance_annual / 12
        self.hoa = hoa_monthly

    def get_monthly_costs(self):
        """Return total monthly costs of property ownership."""
        return (self.mortgage_payment + self.property_tax + 
                self.maintenance + self.insurance + self.hoa)

    def calculate_monthly_mortgage_split(self, remaining_principal, mortgage_rate_annual):
        """Calculate interest and principal portions of mortgage payment."""
        monthly_rate = mortgage_rate_annual / 12
        interest = remaining_principal * monthly_rate
        principal = self.mortgage_payment - interest
        return principal, interest 