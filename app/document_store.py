from sqlalchemy import create_engine, Column, String, DateTime, JSON, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date
import os
import json
from fields_to_extract import CreditCardStatement
from pymongo import MongoClient
from bson import ObjectId, Binary
from decimal import Decimal
import base64

# MongoDB connection string - you'll need to set this in your environment
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')

# Create MongoDB client and get database
client = MongoClient(MONGODB_URI)
db = client['document_classifier']  # Explicitly specify the database name
documents_collection = db.documents

class Document:
    def __init__(self, filename, customer_name, customer_address, payment_info, spend_line_items, pdf_content=None):
        self.filename = filename
        self.customer_name = customer_name
        self.customer_address = customer_address
        self.payment_info = payment_info
        self.spend_line_items = spend_line_items
        self.pdf_content = pdf_content
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    @classmethod
    def from_mongo(cls, data):
        """Create a Document instance from MongoDB data"""
        # Create a copy of the data to avoid modifying the original
        doc_data = data.copy()
        
        # Remove MongoDB's _id field and timestamp fields
        doc_data.pop('_id', None)
        doc_data.pop('created_at', None)
        doc_data.pop('updated_at', None)
        
        # Create new instance
        doc = cls(**doc_data)
        
        # Set timestamp fields if they exist in the original data
        if 'created_at' in data:
            doc.created_at = data['created_at']
        if 'updated_at' in data:
            doc.updated_at = data['updated_at']
            
        return doc

    def to_dict(self):
        # Convert the document to a dictionary, handling Decimal and date values
        doc_dict = {
            'filename': self.filename,
            'customer_name': self.customer_name,
            'customer_address': self.customer_address,
            'payment_info': self._convert_payment_info(self.payment_info),
            'spend_line_items': self._convert_spend_items(self.spend_line_items),
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        
        # Add PDF content if it exists
        if self.pdf_content:
            doc_dict['pdf_content'] = Binary(self.pdf_content)
            
        return doc_dict

    def _convert_payment_info(self, payment_info):
        """Convert payment info Decimal and date values to MongoDB-compatible formats"""
        return {
            'new_balance': str(payment_info['new_balance']),
            'minimum_payment': str(payment_info['minimum_payment']),
            'due_date': datetime.combine(payment_info['due_date'], datetime.min.time())
        }

    def _convert_spend_items(self, spend_items):
        """Convert spend items Decimal and date values to MongoDB-compatible formats"""
        converted_items = []
        for item in spend_items:
            converted_item = {
                'spend_date': datetime.combine(item['spend_date'], datetime.min.time()),
                'spend_description': item['spend_description'],
                'amount': str(item['amount']),
                'category': item['category']
            }
            converted_items.append(converted_item)
        return converted_items

def store_document(filename: str, statement_data: CreditCardStatement, pdf_path: str = None):
    """Store a processed credit card statement in the database."""
    try:
        # Convert Pydantic model to dict
        data = statement_data.model_dump()
        
        # Read PDF content if path is provided
        pdf_content = None
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as f:
                pdf_content = f.read()
        
        # Create document record
        doc = Document(
            filename=filename,
            customer_name=data['customer_name'],
            customer_address=data['customer_address'],
            payment_info=data['payment_info'],
            spend_line_items=data['spend_line_items'],
            pdf_content=pdf_content
        )
        
        # Insert into MongoDB
        result = documents_collection.insert_one(doc.to_dict())
        return doc
    except Exception as e:
        raise

def get_documents_by_customer(customer_name: str):
    """Retrieve all documents for a specific customer."""
    try:
        cursor = documents_collection.find({'customer_name': customer_name})
        return [Document.from_mongo(doc) for doc in cursor]
    except Exception as e:
        raise

def get_all_customers():
    """Retrieve list of all unique customers."""
    try:
        customers = documents_collection.distinct('customer_name')
        return list(customers)
    except Exception as e:
        raise

def get_customer_spending_summary(customer_name: str):
    """Get a summary of spending for a specific customer."""
    try:
        documents = documents_collection.find({'customer_name': customer_name})
        total_spend = 0
        category_spend = {}
        
        for doc in documents:
            for item in doc['spend_line_items']:
                amount = float(item['amount'])  # Convert string back to float
                category = item['category']
                total_spend += amount
                category_spend[category] = category_spend.get(category, 0) + amount
        
        return {
            'customer_name': customer_name,
            'total_spend': total_spend,
            'category_breakdown': category_spend
        }
    except Exception as e:
        raise

def get_document_pdf(filename: str):
    """Retrieve the PDF content for a specific document."""
    try:
        doc = documents_collection.find_one({'filename': filename})
        if doc and 'pdf_content' in doc:
            return doc['pdf_content']
        return None
    except Exception as e:
        raise

def save_document_pdf(filename: str, output_path: str):
    """Retrieve and save a document's PDF to a file."""
    try:
        pdf_content = get_document_pdf(filename)
        if pdf_content:
            with open(output_path, 'wb') as f:
                f.write(pdf_content)
            return True
        return False
    except Exception as e:
        raise 