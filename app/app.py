import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
import pandas as pd
import json
from .main import main as process_pdf

app = Flask(__name__)

UPLOAD_FOLDER = 'data/uploads'
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
        # Print debug info
        print(f"Loading CSV: {filename}")
        
        # Ensure file exists
        if not os.path.exists(filename):
            print(f"File does not exist: {filename}")
            return jsonify({'error': f'File not found: {filename}'})
            
        # Read CSV file
        df = pd.read_csv(filename)
        print(f"CSV loaded successfully. Columns: {df.columns.tolist()}")
        print(f"Data types: {df.dtypes}")
        print(f"First few rows: \n{df.head()}")
        
        # Check if required columns exist
        required_columns = ['spend_date', 'spend_description', 'amount', 'category']
        for col in required_columns:
            if col not in df.columns:
                print(f"Missing column: {col}")
                return jsonify({'error': f'Missing column: {col}. Required columns: {required_columns}'})
        
        # Prepare data for charts
        # Handle category data
        try:
            category_data = df.groupby('category')['amount'].sum().reset_index()
            category_labels = category_data['category'].tolist()
            category_values = category_data['amount'].tolist()
            print(f"Categories found: {category_labels}")
        except Exception as e:
            print(f"Error in category processing: {str(e)}")
            category_labels = ['Other']
            category_values = [df['amount'].sum() if 'amount' in df else 0]
        
        # Handle date data with error checking
        try:
            # Convert to datetime safely
            df['spend_date'] = pd.to_datetime(df['spend_date'], errors='coerce')
            
            # Drop any rows with invalid dates
            df = df.dropna(subset=['spend_date'])
            
            # Group by date
            if not df.empty:
                date_data = df.groupby('spend_date')['amount'].sum().reset_index()
                date_labels = date_data['spend_date'].dt.strftime('%Y-%m-%d').tolist()
                date_values = date_data['amount'].tolist()
            else:
                date_labels = []
                date_values = []
            print(f"Dates found: {date_labels}")
        except Exception as e:
            print(f"Error in date processing: {str(e)}")
            date_labels = []
            date_values = []
        
        # Handle merchant data
        try:
            merchant_data = df.groupby('spend_description')['amount'].sum().reset_index().sort_values('amount', ascending=False).head(10)
            merchant_labels = merchant_data['spend_description'].tolist()
            merchant_values = merchant_data['amount'].tolist()
            print(f"Top merchants found: {merchant_labels[:3]}")
        except Exception as e:
            print(f"Error in merchant processing: {str(e)}")
            merchant_labels = ['No data']
            merchant_values = [0]
        
        # Calculate total amount
        try:
            total_spent = df['amount'].sum()
            print(f"Total spent: {total_spent}")
        except Exception as e:
            print(f"Error calculating total: {str(e)}")
            total_spent = 0
        
        # Format transaction data for the table
        transactions = []
        try:
            for _, row in df.iterrows():
                if pd.notna(row.get('spend_date')):
                    date_str = row['spend_date'].strftime('%Y-%m-%d')
                else:
                    date_str = 'Unknown Date'
                    
                transactions.append({
                    'spend_date': date_str,
                    'spend_description': row['spend_description'],
                    'amount': float(row['amount']),
                    'category': row['category']
                })
        except Exception as e:
            print(f"Error formatting transactions: {str(e)}")
        
        # Return the prepared data
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
        print(f"Global error in get_data: {str(e)}")
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
