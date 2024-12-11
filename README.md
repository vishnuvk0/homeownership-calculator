# homeownership-calculator


## install requirements

pip install -r requirements.txt

## run app

run `python3 home_script_including_moving_out_4.py`


# *how to use*

- this app makes some assumptions right now.

    -assumption 0: you are debating buying ur FIRST home.

    -assumption 1: if you are debating renting vs. buying you are going to LIVE in this home for at least 2 years before potentially renting it out (if you wanted to )

    - assumption 2: if you were to continue renting, the down payment amount would be invested in another asset class (businesses/stocks) that you can adjust the annual growth rate

    - assumption 3: if you plan to rent out your home for some reason after leaving it (moving to new city, etc), you will rent somewhere else.

*read this before you start the app.*

the app asks for the following (you can enter 0 for any of these if n/a):

### *home purchase*

- `home price` (e.g. 900000)
- `Buyer closing costs percentage` (e.g. 0.04 for 4%): 
- `down payment percentage` (e.g. 0.20 for 20%)
- `mortgage interest rate` (e.g. 0.06 for 6%)
    - does not account for refinancing yet
- `mortgage term` in years (e.g. 30): 
- `annual property` tax rate (e.g. 0.011 for 1.1%): 
- `Annual maintenance` cost (e.g. 5000): 
- `Annual insurance cost` (e.g. 3500): 
- `Monthly HOA` fee (e.g. 300): 


- `Selling closing costs percentage` (e.g. 0.06 for 6%): 

### *the alternative: renting*
- `Current monthly rent` (e.g. 2400): 
    -   what you pay for rent
- `Annual rent growth rate` (e.g. 0.04 for 4%):
    -   how much you think rent will go up over time? enter 0 if you are rent controlled?
- `Savings/Investment annual growth rate` (e.g. 0.16 for 16%):
    -   project the growth rate of what you WOULD get investing the the following: 
        -  a) `{monthly home ownership payment}` `-` `{current rent}`
            - basically what you would have put towards mortgage that is more than rent you're investing it.
        -  b) `down payment` 
    into another asset class such as another a brokerage/money market/etc account. default is set to `16%` but that should be changed.
- `Home appreciation annual growth rate` (e.g. 0.08 for 8%): 
    - hard to predict, somewhere between 4-10% makes sense.
- `Tax rate` (e.g. 0.30 for 30%): 
    - average rate you pay for state/local/federal taxes. 
    - used to calculate your mortgage interest deduction
- `Property tax deduction cap` (e.g. 10000): 
    - what you can deduct from your taxes for property taxes
- `Number of months you plan to live in the home` (e.g. 36): 
    - use months. 1 year = 12 months, 2 years =24 months, etc.
    - if you think you're going to buy the house rent it out, live in a new city, come back in 5 years, and live in the house for the next 5 or whatever, calculate the number of months that you actually think you might live in it for. doesn't matter when it happens
- `Number of months you plan to rent out the home` (e.g. 36): 
    -how many months will this house be rented?
    -this is how long you expect to rent out your home before selling.
- `Monthly rent you will pay elsewhere after moving out` (e.g. 2500):
    - essentially what you would pay for rent in the market.
- `Monthly rent you expect to collect from the home` (e.g. 3500)
    -this is how much you could get per month for your home