from flask import Flask, request, jsonify
from simulation import simulate_scenario
import json

app = Flask(__name__)

@app.route('/api/simulate', methods=['POST'])
def simulate():
    try:
        data = request.get_json()
        
        # Ensure all required fields are present
        required_fields = [
            'home_price', 'down_payment_pct', 'mortgage_rate_annual', 
            'mortgage_term_years', 'property_tax_rate_annual', 'maintenance_annual',
            'insurance_annual', 'hoa_monthly', 'closing_costs_buy_pct',
            'closing_costs_sell_pct', 'rent_current', 'rent_growth_annual',
            'alt_invest_growth_annual', 'monthly_invest_growth_annual',
            'home_appreciation_annual', 'tax_rate', 'property_tax_deduction_cap',
            'months_live_in', 'months_rent_out', 'rent_while_out',
            'rent_collected_home'
        ]
        
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Run simulation with provided parameters
        result = simulate_scenario(
            home_price=float(data['home_price']),
            down_payment_pct=float(data['down_payment_pct']),
            mortgage_rate_annual=float(data['mortgage_rate_annual']),
            mortgage_term_years=int(data['mortgage_term_years']),
            property_tax_rate_annual=float(data['property_tax_rate_annual']),
            maintenance_annual=float(data['maintenance_annual']),
            insurance_annual=float(data['insurance_annual']),
            hoa_monthly=float(data['hoa_monthly']),
            closing_costs_buy_pct=float(data['closing_costs_buy_pct']),
            closing_costs_sell_pct=float(data['closing_costs_sell_pct']),
            rent_current=float(data['rent_current']),
            rent_growth_annual=float(data['rent_growth_annual']),
            alt_invest_growth_annual=float(data['alt_invest_growth_annual']),
            monthly_invest_growth_annual=float(data['monthly_invest_growth_annual']),
            home_appreciation_annual=float(data['home_appreciation_annual']),
            tax_rate=float(data['tax_rate']),
            property_tax_deduction_cap=float(data['property_tax_deduction_cap']),
            months_live_in=int(data['months_live_in']),
            months_rent_out=int(data['months_rent_out']),
            rent_while_out=float(data['rent_while_out']),
            rent_collected_home=float(data['rent_collected_home'])
        )
        
        return jsonify(result)
    except ValueError as e:
        return jsonify({'error': f'Invalid numeric value: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/')
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    # Run on all interfaces, port 8080
    app.run(host='0.0.0.0', port=8080, debug=True)