from financial_utils import calculate_mortgage_payment

class PropertyCosts:
    def __init__(self, home_price, down_payment_pct, mortgage_rate_annual, 
                 mortgage_term_years, property_tax_rate_annual, maintenance_annual,
                 insurance_annual, hoa_monthly):
        self.home_price = home_price
        self.down_payment = home_price * down_payment_pct
        self.loan_amount = home_price * (1 - down_payment_pct)
        self.property_tax_annual = home_price * property_tax_rate_annual
        self.maintenance_annual = maintenance_annual
        self.insurance_annual = insurance_annual
        self.hoa_monthly = hoa_monthly
        self.mortgage_term_years = mortgage_term_years
        self.mortgage_rate_annual = mortgage_rate_annual

    def calculate_monthly_payment(self, mortgage_rate_annual):
        """Calculate the monthly mortgage payment."""
        r = mortgage_rate_annual / 12  # Monthly interest rate
        n = self.mortgage_term_years * 12  # Total number of payments
        
        # Using the mortgage payment formula: P = L[r(1 + r)^n]/[(1 + r)^n - 1]
        # where P = payment, L = loan amount, r = monthly interest rate, n = number of payments
        if r == 0:
            return self.loan_amount / n
        monthly_payment = self.loan_amount * (r * (1 + r)**n) / ((1 + r)**n - 1)
        return monthly_payment

    def calculate_monthly_mortgage_split(self, remaining_principal, mortgage_rate_annual):
        """Calculate the split between principal and interest for a given month."""
        monthly_rate = mortgage_rate_annual / 12
        monthly_payment = self.calculate_monthly_payment(mortgage_rate_annual)
        
        interest = remaining_principal * monthly_rate
        principal = monthly_payment - interest
        
        return principal, interest

    def get_monthly_costs(self):
        """Calculate total monthly costs including mortgage, taxes, insurance, maintenance, and HOA."""
        return (self.calculate_monthly_payment(self.mortgage_rate_annual) +
                self.property_tax_annual/12 + 
                self.maintenance_annual/12 + 
                self.insurance_annual/12 + 
                self.hoa_monthly)