from flask import Flask, render_template, request, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
import requests
import json
import csv
import io
import os
from datetime import datetime
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///crypto_dashboard.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize database
db = SQLAlchemy(app)

# Database Models
class DownloadRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    download_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    filename = db.Column(db.String(255), nullable=False)
    download_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    file_size = db.Column(db.Integer, nullable=True)
    crypto_count = db.Column(db.Integer, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'download_id': self.download_id,
            'filename': self.filename,
            'download_time': self.download_time.strftime('%Y-%m-%d %H:%M:%S UTC'),
            'file_size': self.file_size,
            'crypto_count': self.crypto_count
        }

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
        
        # Generate filename
        filename = f"crypto_prices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Store download record in database
        try:
            download_record = DownloadRecord(
                filename=filename,
                file_size=len(csv_content.encode('utf-8')),
                crypto_count=len(crypto_data)
            )
            db.session.add(download_record)
            db.session.commit()
        except Exception as db_error:
            # Log the error but don't fail the download
            print(f"Database error: {db_error}")
        
        response = Response(
            csv_content,
            mimetype='text/csv; charset=utf-8',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Type': 'text/csv; charset=utf-8',
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            }
        )
        
        return response
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download-history')
def download_history():
    """API endpoint to get download history"""
    try:
        records = DownloadRecord.query.order_by(DownloadRecord.download_time.desc()).limit(50).all()
        return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/history')
def history():
    """Page to view download history"""
    return render_template('history.html')

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

# Initialize database tables
with app.app_context():
    db.create_all()

if __name__=='__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
