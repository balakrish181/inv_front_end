from document_store import (
    get_documents_by_customer,
    get_all_customers,
    get_customer_spending_summary,
    documents_collection
)
from datetime import datetime
import json

def print_json(data):
    """Helper function to print data in a readable JSON format"""
    print(json.dumps(data, indent=2, default=str))

def example_queries():
    # 1. Get all customers
    print("\n1. All Customers:")
    customers = get_all_customers()
    print_json(customers)

    # 2. Get documents for a specific customer
    print("\n2. Documents for a specific customer:")
    customer_name = "Joseph Paulson"  # Replace with actual customer name
    customer_docs = get_documents_by_customer(customer_name)
    for doc in customer_docs:
        print(f"\nDocument: {doc.filename}")
        print(f"Customer: {doc.customer_name}")
        print(f"Address: {doc.customer_address}")

    # 3. Get spending summary for a customer
    print("\n3. Customer Spending Summary:")
    summary = get_customer_spending_summary(customer_name)
    print_json(summary)

    # 4. Advanced MongoDB queries
    print("\n4. Advanced Queries:")

    # Find documents with high spending (e.g., total spend > $1000)
    high_spending_docs = documents_collection.find({
        "spend_line_items": {
            "$elemMatch": {
                "amount": {"$gt": "1000.00"}
            }
        }
    })
    print("\nDocuments with transactions over $1000:")
    for doc in high_spending_docs:
        print(f"Customer: {doc['customer_name']}")
        print(f"File: {doc['filename']}")

    # Find documents by date range
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 12, 31)
    date_range_docs = documents_collection.find({
        "created_at": {
            "$gte": start_date,
            "$lte": end_date
        }
    })
    print("\nDocuments from 2023:")
    for doc in date_range_docs:
        print(f"Customer: {doc['customer_name']}")
        print(f"Created: {doc['created_at']}")

    # Find documents by category
    category = "Dining"
    category_docs = documents_collection.find({
        "spend_line_items": {
            "$elemMatch": {
                "category": category
            }
        }
    })
    print(f"\nDocuments with {category} transactions:")
    for doc in category_docs:
        print(f"Customer: {doc['customer_name']}")
        print(f"File: {doc['filename']}")

    # Aggregate spending by category across all customers
    pipeline = [
        {"$unwind": "$spend_line_items"},
        {"$group": {
            "_id": "$spend_line_items.category",
            "total_spend": {"$sum": {"$toDouble": "$spend_line_items.amount"}},
            "count": {"$sum": 1}
        }},
        {"$sort": {"total_spend": -1}}
    ]
    category_totals = documents_collection.aggregate(pipeline)
    print("\nTotal spending by category across all customers:")
    for result in category_totals:
        print(f"Category: {result['_id']}")
        print(f"Total Spend: ${result['total_spend']:.2f}")
        print(f"Number of transactions: {result['count']}")

if __name__ == "__main__":
    example_queries() 