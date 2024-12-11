# Home Ownership Calculator

A web application to help you decide between buying and renting a home by analyzing various financial factors and scenarios.

## Features

- Compare buying vs renting scenarios
- Calculate mortgage payments and amortization
- Analyze investment opportunities
- Consider tax implications
- Evaluate rental income potential
- Visualize trends with interactive charts

## Installation

1. Clone the repository
2. Install the requirements:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the Flask server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

## How to Use

The calculator takes into account various factors:

### Property Details
- Home price
- Down payment percentage
- Mortgage interest rate
- Mortgage term

### Property Costs
- Property tax rate
- Annual maintenance costs
- Insurance costs
- HOA fees

### Transaction Costs
- Buyer closing costs
- Seller closing costs

### Rent Details
- Current monthly rent
- Expected rent growth rate

### Investment Rates
- Alternative investment growth rate (for down payment if not buying)
- Monthly investment growth rate (for monthly payment differences)

### Market Conditions
- Home appreciation rate
- Tax rate
- Property tax deduction cap

### Living Situation
- Months planning to live in the home
- Months planning to rent out the home
- Expected rent while living elsewhere
- Expected rental income from the property

## Assumptions

1. This calculator is designed for first-time homebuyers
2. If buying, you plan to live in the home for at least 2 years
3. Down payment amount would be invested in alternative assets if renting
4. If planning to rent out your home, you will rent elsewhere

## Results

The calculator provides:
- Final recommendation (buy vs rent)
- Detailed property value analysis
- Cost breakdown
- Investment comparisons
- Monthly payment analysis
- Amortization schedule
- Interactive charts showing value trends

## Contributing

Feel free to submit issues and enhancement requests!