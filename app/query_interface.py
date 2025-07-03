from document_store import (
    get_all_customers,
    get_customer_spending_summary,
    get_documents_by_customer,
    save_document_pdf
)
import os
from typing import List, Dict, Optional
from datetime import datetime

def list_all_customers() -> List[str]:
    """Get a list of all customers in the database."""
    return get_all_customers()

def get_spending_summary(customer_name: str) -> Dict:
    """Get spending summary for a specific customer."""
    return get_customer_spending_summary(customer_name)

def retrieve_customer_documents(customer_name: str, output_dir: str = "retrieved_documents") -> List[str]:
    """
    Retrieve all documents for a customer and save them to the specified directory.
    
    Args:
        customer_name (str): Name of the customer
        output_dir (str): Directory to save the documents
        
    Returns:
        List[str]: List of paths to saved documents
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all documents for the customer
    documents = get_documents_by_customer(customer_name)
    saved_paths = []
    
    for doc in documents:
        # Create a timestamped filename to avoid overwrites
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{timestamp}_{doc.filename}"
        output_path = os.path.join(output_dir, output_filename)
        
        # Save the document
        if save_document_pdf(doc.filename, output_path):
            saved_paths.append(output_path)
    
    return saved_paths

def print_spending_summary(customer_name: str):
    """Print a formatted spending summary for a customer."""
    summary = get_spending_summary(customer_name)
    
    print(f"\nSpending Summary for {customer_name}")
    print("=" * 50)
    print(f"Total Spend: ${summary['total_spend']:.2f}")
    print("\nCategory Breakdown:")
    print("-" * 30)
    
    for category, amount in summary['category_breakdown'].items():
        print(f"{category:20} ${amount:10.2f}")

def main():
    """Interactive command-line interface for document queries."""
    while True:
        print("\nDocument Query Interface")
        print("=" * 30)
        print("1. List all customers")
        print("2. Get spending summary for a customer")
        print("3. Retrieve customer documents")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == "1":
            customers = list_all_customers()
            print("\nAvailable Customers:")
            for customer in customers:
                print(f"- {customer}")
                
        elif choice == "2":
            customer_name = input("Enter customer name: ")
            print_spending_summary(customer_name)
            
        elif choice == "3":
            customer_name = input("Enter customer name: ")
            output_dir = input("Enter output directory (default: retrieved_documents): ") or "retrieved_documents"
            
            saved_paths = retrieve_customer_documents(customer_name, output_dir)
            if saved_paths:
                print("\nRetrieved Documents:")
                for path in saved_paths:
                    print(f"- {path}")
            else:
                print("No documents found for this customer.")
                
        elif choice == "4":
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 