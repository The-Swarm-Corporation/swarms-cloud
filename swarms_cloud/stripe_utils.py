import logging

import stripe
from pydantic import BaseModel
import os


class StripeInterface(BaseModel):
    customer_id: str
    amount: float
    description: str


def bill_customer(customer_id: str, amount: float, description: str):
    stripe.api_key = os.getenv("STRIPE_API_KEY")

    try:
        stripe.Charge.create(
            customer=customer_id,
            amount=amount,  # in cents
            currency="usd",
            description=description,
        )
        logging.info("Payment successful")
    except stripe.error.StripeError as e:
        logging.error(f"Payment failed: {str(e)}")


# Usage:
# bill_customer("429232323", 1000, "1,000 tokens")
