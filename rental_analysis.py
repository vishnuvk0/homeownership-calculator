from financial_utils import project_rent_values

class RentalScenario:
    def __init__(self, property_costs, months_live_in, months_rent_out,
                 rent_while_out, rent_collected_home, rent_growth_annual, rent_current):
        self.months_live_in = months_live_in
        self.months_rent_out = months_rent_out
        self.rent_while_out = rent_while_out
        self.rent_collected_home = rent_collected_home
        self.rent_growth_annual = rent_growth_annual
        
        # Calculate all rent progressions
        total_months = months_live_in + months_rent_out
        
        # 1. Calculate rent progression if not buying (starts from rent_current)
        self.monthly_rent_if_no_buy = []
        for month in range(total_months):
            month_fraction = month / 12
            growth_factor = (1 + rent_growth_annual) ** month_fraction
            self.monthly_rent_if_no_buy.append(rent_current * growth_factor)
        
        # 2. Calculate rental income progression (starts from rent_collected_home)
        self.monthly_rent_collected = []
        for month in range(total_months):
            month_fraction = month / 12
            growth_factor = (1 + rent_growth_annual) ** month_fraction
            self.monthly_rent_collected.append(rent_collected_home * growth_factor)
            
        # 3. Calculate rent paid while out progression (starts from rent_while_out)
        self.monthly_rent_while_out = []
        for month in range(total_months):
            month_fraction = month / 12
            growth_factor = (1 + rent_growth_annual) ** month_fraction
            self.monthly_rent_while_out.append(rent_while_out * growth_factor)

    def calculate_monthly_cashflow(self, month):
        # During living in period, only consider the opportunity cost of rent
        if month <= self.months_live_in:
            return -self.monthly_rent_if_no_buy[month-1]
        else:
            # After moving out, consider both collected rent and paid rent with growth
            rent_month_idx = month - 1
            return self.monthly_rent_collected[rent_month_idx] - self.monthly_rent_while_out[rent_month_idx]