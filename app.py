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
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

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
        
        # Create response with proper encoding for production
        output.seek(0)
        csv_content = output.getvalue()
        
        response = Response(
            csv_content,
            mimetype='text/csv; charset=utf-8',
            headers={
                'Content-Disposition': f'attachment; filename="crypto_prices_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"',
                'Content-Type': 'text/csv; charset=utf-8',
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
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
    return render_template('index.html',Percentage=Percentage)

if __name__=='__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
