import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
import pandas as pd
import json
from main import main as process_pdf

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process the uploaded PDF using the main function
        try:
            # Process the PDF and get CSV filename and spend line items
            csv_filename, spend_line_items = process_pdf(filepath)
            
            if csv_filename:
                # Redirect to dashboard with the CSV filename
                return redirect(url_for('dashboard', filename=csv_filename))
            else:
                return "No spend items found in the uploaded document."
        except Exception as e:
            return f"An error occurred while processing the file: {str(e)}"
    return redirect(request.url)

@app.route('/dashboard/<path:filename>')
def dashboard(filename):
    return render_template('dashboard.html', csv_file=filename)

@app.route('/get_data/<path:filename>')
def get_data(filename):
    try:
        df = pd.read_csv(filename)
        
        # Prepare data for charts
        category_data = df.groupby('category')['amount'].sum().reset_index()
        category_labels = category_data['category'].tolist()
        category_values = category_data['amount'].tolist()
        
        # Time series data (assuming spend_date is in proper format)
        df['spend_date'] = pd.to_datetime(df['spend_date'])
        date_data = df.groupby('spend_date')['amount'].sum().reset_index()
        date_labels = date_data['spend_date'].dt.strftime('%Y-%m-%d').tolist()
        date_values = date_data['amount'].tolist()
        
        # Top merchants data
        merchant_data = df.groupby('spend_description')['amount'].sum().reset_index().sort_values('amount', ascending=False).head(10)
        merchant_labels = merchant_data['spend_description'].tolist()
        merchant_values = merchant_data['amount'].tolist()
        
        # Total amount
        total_spent = df['amount'].sum()
        
        # Format transaction data for the table
        transactions = []
        for _, row in df.iterrows():
            transactions.append({
                'spend_date': row['spend_date'].strftime('%Y-%m-%d'),
                'spend_description': row['spend_description'],
                'amount': float(row['amount']),
                'category': row['category']
            })
        
        return jsonify({
            'category': {
                'labels': category_labels,
                'values': category_values
            },
            'date': {
                'labels': date_labels,
                'values': date_values
            },
            'merchant': {
                'labels': merchant_labels,
                'values': merchant_values
            },
            'total': total_spent,
            'transactions': transactions
        })
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
