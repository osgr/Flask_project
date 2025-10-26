from flask import Flask, render_template, request, jsonify, Response
import requests
import json
import csv
import io
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def run():
    return render_template('home.html')

@app.route('/test')
def test():
    return "Flask app is working! Dashboard should be at /dashboard"

@app.route('/routes')
def list_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append(f"{rule.rule} -> {rule.endpoint}")
    return "<br>".join(routes)

@app.route('/dashboard')
def dashboard():
    try:
        return render_template('dashboard.html')
    except Exception as e:
        return f"Error loading dashboard: {str(e)}", 500

@app.route('/dashboard-simple')
def dashboard_simple():
    return """
    <html>
    <head><title>Simple Dashboard Test</title></head>
    <body>
        <h1>Crypto Dashboard Test</h1>
        <p>If you can see this, the routing is working!</p>
        <a href="/">Go to Calculator</a><br>
        <a href="/dashboard">Go to Full Dashboard</a><br>
        <a href="/test">Test Route</a>
    </body>
    </html>
    """

def get_crypto_data():
    """Helper function to fetch crypto data from API"""
    try:
        # Using CoinGecko API to get top 10 cryptocurrencies
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': 10,
            'page': 1,
            'sparkline': False
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        crypto_data = response.json()
        
        # Format the data for our dashboard
        formatted_data = []
        for coin in crypto_data:
            formatted_data.append({
                'id': coin['id'],
                'name': coin['name'],
                'symbol': coin['symbol'].upper(),
                'current_price': coin['current_price'],
                'market_cap': coin['market_cap'],
                'market_cap_rank': coin['market_cap_rank'],
                'price_change_percentage_24h': coin['price_change_percentage_24h'],
                'image': coin['image']
            })
        
        return formatted_data
        
    except requests.exceptions.RequestException as e:
        raise Exception(f'Failed to fetch crypto data: {str(e)}')
    except Exception as e:
        raise Exception(f'An error occurred: {str(e)}')

@app.route('/api/crypto-prices')
def get_crypto_prices():
    try:
        formatted_data = get_crypto_data()
        return jsonify(formatted_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download-csv')
def download_csv():
    try:
        crypto_data = get_crypto_data()
        
        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Rank', 'Name', 'Symbol', 'Current Price (USD)', 
            'Market Cap (USD)', '24h Change (%)', 'Download Time'
        ])
        
        # Write data rows
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for coin in crypto_data:
            writer.writerow([
                coin['market_cap_rank'],
                coin['name'],
                coin['symbol'],
                f"${coin['current_price']:,.6f}" if coin['current_price'] < 1 else f"${coin['current_price']:,.2f}",
                f"${coin['market_cap']:,.0f}",
                f"{coin['price_change_percentage_24h']:.2f}%" if coin['price_change_percentage_24h'] else 'N/A',
                current_time
            ])
        
        # Create response
        output.seek(0)
        response = Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename=crypto_prices_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            }
        )
        
        return response
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/submit', methods=['POST'])
def marks():
    Physics=int(request.form['Physics'])
    Maths= int(request.form['Maths'])
    Chemistry = int(request.form['Chemistry'])
    Hindi = int(request.form['Hindi'])
    English = int(request.form['English'])
    result = Physics + Maths + Chemistry + Hindi + English
    Percentage = result/5
    return render_template('home.html',Percentage=Percentage)

if __name__=='__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
