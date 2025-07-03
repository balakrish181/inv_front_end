from .text_extraction import extract_text_from_pdf
import instructor
from openai import OpenAI
from pydantic import BaseModel, Field
from pydantic_extra_types.phone_numbers import PhoneNumber
from typing import Iterable

from .fields_to_extract import CreditCardStatement
from .client_request import parse_lead_from_message
from .document_store import store_document, get_customer_spending_summary, save_document_pdf
import csv
import sys
import os

def main(input_doc_path):
    """Process a PDF document and extract financial data"""
    # Extract text from PDF
    context_markdown = extract_text_from_pdf(input_doc_path)

    # Parse the extracted text to get structured data
    response = parse_lead_from_message(CreditCardStatement, context_markdown, model_name="openai")

    # Store the document in the database with the PDF
    stored_doc = store_document(input_doc_path, response, pdf_path=input_doc_path)
    print(f"Document stored for customer: {stored_doc.customer_name}")

    # Get spend line items
    spend_line_items = response.model_dump()['spend_line_items']

    # Generate CSV filename based on input file
    base_filename = os.path.basename(input_doc_path)
    filename = f'spend_line_items_{os.path.splitext(base_filename)[0]}.csv'
    
    # Save data to CSV
    with open(filename, mode='w', newline='') as file:
        if spend_line_items:
            writer = csv.DictWriter(file, fieldnames=spend_line_items[0].keys())
            writer.writeheader()
            writer.writerows(spend_line_items)
            print(f"CSV file created: {filename}")
            
            # Get and print spending summary
            summary = get_customer_spending_summary(stored_doc.customer_name)
            print("\nCustomer Spending Summary:")
            print(f"Total Spend: ${summary['total_spend']:.2f}")
            print("\nCategory Breakdown:")
            for category, amount in summary['category_breakdown'].items():
                print(f"{category}: ${amount:.2f}")
            
            return filename, spend_line_items
        else:
            print("No spend_line_items found.")
            return None, []


if __name__ == "__main__":
    input_doc_path = "pdfs/Amex.pdf"
    main(input_doc_path)
    #print(text)
