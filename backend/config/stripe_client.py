import stripe
from config import config

stripe_client = stripe.StripeClient(config.STRIPE.SECRET_KEY)