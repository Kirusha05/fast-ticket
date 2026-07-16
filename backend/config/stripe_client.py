import stripe
from config.config import config

stripe_client = stripe.StripeClient(config.STRIPE.SECRET_KEY)