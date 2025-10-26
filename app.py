from flask import Flask, render_template, request, jsonify
import requests
import json

app = Flask(__name__)

@app.route('/')
def run():
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/crypto-prices')
def get_crypto_prices():
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
        
        return jsonify(formatted_data)
        
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to fetch crypto data: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

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
    app.run(debug=True)
