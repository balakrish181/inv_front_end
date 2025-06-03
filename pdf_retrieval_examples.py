from document_store import get_document_pdf, save_document_pdf, get_documents_by_customer
import os

def retrieve_and_save_pdf(customer_name, output_dir="retrieved_pdfs"):
    """
    Retrieve and save all PDFs for a specific customer
    
    Args:
        customer_name (str): Name of the customer
        output_dir (str): Directory to save the PDFs
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all documents for the customer
    documents = get_documents_by_customer(customer_name)
    
    print(f"Found {len(documents)} documents for customer: {customer_name}")
    
    # Retrieve and save each PDF
    for doc in documents:
        # Get the PDF content
        pdf_content = get_document_pdf(doc.filename)
        
        if pdf_content:
            # Create output filename
            output_path = os.path.join(output_dir, doc.filename)
            
            # Save the PDF
            save_document_pdf(doc.filename, output_path)
            print(f"Saved PDF to: {output_path}")
        else:
            print(f"No PDF found for document: {doc.filename}")

def main():
    # Example usage
    customer_name = "John Doe"  # Replace with actual customer name
    retrieve_and_save_pdf(customer_name)

if __name__ == "__main__":
    main() 