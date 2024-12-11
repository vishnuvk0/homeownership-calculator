from financial_utils import project_rent_values

class RentalScenario:
    def __init__(self, property_costs, months_live_in, months_rent_out,
                 rent_while_out, rent_collected_home, rent_growth_annual):
        self.property_costs = property_costs
        self.months_live_in = months_live_in
        self.months_rent_out = months_rent_out
        self.total_months = months_live_in + months_rent_out
        self.rent_while_out = rent_while_out
        self.rent_collected_home = rent_collected_home
        
        # Project rent values for comparison scenario
        self.monthly_rent_if_no_buy = project_rent_values(
            rent_while_out, self.total_months, rent_growth_annual)

    def calculate_monthly_cashflow(self, month):
        """Calculate monthly cash flow for given month."""
        monthly_costs = self.property_costs.get_monthly_costs()
        
        if month <= self.months_live_in:
            # Living in period
            return -monthly_costs
        else:
            # Renting out period
            rental_income = self.rent_collected_home
            rent_paid = self.rent_while_out
            return rental_income - monthly_costs - rent_paid 