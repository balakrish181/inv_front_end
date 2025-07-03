
from pydantic import BaseModel, Field, condecimal, constr
from typing import List
from datetime import date
import decimal



# Address Model
class CustomerAddress(BaseModel):
    full_address: constr(min_length=5, strip_whitespace=True) = Field(
        description="The complete mailing address of the customer"
    )
    city: constr(strip_whitespace=True, min_length=2) = Field(
        description="City from the customer's address"
    )
    zip: str = Field(description="ZIP code from the customer's address")



class PaymentInfo(BaseModel):
    new_balance: condecimal(gt=0, decimal_places=2) = Field(
        description="The full amount due for the current statement"
    )
    minimum_payment: condecimal(ge=0, decimal_places=2) = Field(
        description="The minimum payment due"
    )
    due_date: date = Field(
        description="The due date for the payment (YYYY-MM-DD)"
    )


class SpendItem(BaseModel):
    spend_date: date = Field(
        description="Transaction date in yyyy-mm-dd format"
    )
    spend_description: constr(min_length=2, strip_whitespace=True) = Field(
        description="Merchant or description of the transaction"
    )
    amount: condecimal(gt=0, decimal_places=2) = Field(
        description="Transaction amount, formatted with 2 decimal places"
    )
    category: constr(strip_whitespace=True, min_length=2) = Field(
        description="Category of the transaction like grocery, dining, travel, etc... If you can't find a category, use 'Other'"
    )


class CreditCardStatement(BaseModel):
    customer_name: constr(strip_whitespace=True, min_length=3) = Field(
        description="Name of the customer, formatted with each word capitalized"
    )
    customer_address: CustomerAddress = Field(
        description="Address associated with the customer"
    )
    payment_info: PaymentInfo = Field(
        description="Summary of the payment information for this statement"
    )
    spend_line_items: List[SpendItem] = Field(
        description="Purchases made using the credit card! Make sure to extract all the Purchases in the document"
    )



if __name__ == "__main__":

    print(CreditCardStatement.model_json_schema())