from financial_utils import project_rent_values

class RentalScenario:
    def __init__(self, property_costs, months_live_in, months_rent_out,
                 rent_while_out, rent_collected_home, rent_growth_annual):
        self.property_costs = property_costs
        self.months_live_in = months_live_in
        self.months_rent_out = months_rent_out
        self.total_months = months_live_in + months_rent_out
        self.rent_while_out = rent_while_out if months_rent_out > 0 else 0
        self.rent_collected_home = rent_collected_home if months_rent_out > 0 else 0
        
        # Project rent values for comparison scenario - this should always be calculated
        # even if not renting out, as it represents what you would pay in rent if you didn't buy
        self.monthly_rent_if_no_buy = project_rent_values(
            rent_while_out, self.total_months, rent_growth_annual)

    def calculate_monthly_cashflow(self, month):
        """Calculate monthly cash flow for given month."""
        monthly_costs = self.property_costs.get_monthly_costs()
        
        if month <= self.months_live_in or self.months_rent_out == 0:
            # Living in period or never renting out
            return -monthly_costs
        else:
            # Renting out period
            rental_income = self.rent_collected_home
            rent_paid = self.rent_while_out
            return rental_income - monthly_costs - rent_paid