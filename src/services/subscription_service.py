import os
import stripe
from datetime import datetime, timedelta
from src.models import ParentProfile, db

# Initialize Stripe with API key
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'sk_test_your_test_key')

class SubscriptionService:
    @staticmethod
    def create_customer(parent_profile, payment_method_id=None):
        """Create a Stripe customer for a parent."""
        try:
            # Create customer in Stripe
            customer_data = {
                'email': parent_profile.user.email,
                'name': f"{parent_profile.first_name or ''} {parent_profile.last_name or ''}".strip(),
                'metadata': {
                    'parent_id': parent_profile.id,
                    'user_id': parent_profile.user_id
                }
            }
            
            # Attach payment method if provided
            if payment_method_id:
                customer_data['payment_method'] = payment_method_id
            
            customer = stripe.Customer.create(**customer_data)
            
            # Update parent profile with Stripe customer ID
            parent_profile.stripe_customer_id = customer.id
            db.session.commit()
            
            return True, customer
        except stripe.error.StripeError as e:
            return False, str(e)
    
    @staticmethod
    def create_subscription(parent_profile, price_id):
        """Create a subscription for a parent."""
        try:
            # Check if parent has a Stripe customer ID
            if not parent_profile.stripe_customer_id:
                return False, "Parent does not have a Stripe customer ID"
            
            # Create subscription
            subscription = stripe.Subscription.create(
                customer=parent_profile.stripe_customer_id,
                items=[
                    {'price': price_id},
                ],
                payment_behavior='default_incomplete',
                expand=['latest_invoice.payment_intent'],
                metadata={
                    'parent_id': parent_profile.id,
                    'user_id': parent_profile.user_id
                }
            )
            
            return True, subscription
        except stripe.error.StripeError as e:
            return False, str(e)
    
    @staticmethod
    def cancel_subscription(parent_profile):
        """Cancel a parent's subscription."""
        try:
            # Find active subscriptions for the customer
            subscriptions = stripe.Subscription.list(
                customer=parent_profile.stripe_customer_id,
                status='active'
            )
            
            if not subscriptions.data:
                return False, "No active subscription found"
            
            # Cancel the subscription
            for subscription in subscriptions.data:
                stripe.Subscription.delete(subscription.id)
            
            # Update parent profile
            parent_profile.subscription_status = 'canceled'
            db.session.commit()
            
            return True, "Subscription canceled successfully"
        except stripe.error.StripeError as e:
            return False, str(e)
    
    @staticmethod
    def update_subscription_status(parent_profile, status, expiry_date=None):
        """Update a parent's subscription status."""
        try:
            # Update parent profile
            parent_profile.subscription_status = status
            
            if expiry_date:
                parent_profile.subscription_expiry = expiry_date
            elif status == 'active':
                # Set default expiry to 1 month from now if not provided
                parent_profile.subscription_expiry = datetime.utcnow() + timedelta(days=30)
            
            db.session.commit()
            
            return True, "Subscription status updated successfully"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def handle_webhook_event(event):
        """Handle Stripe webhook events."""
        try:
            # Handle different event types
            if event['type'] == 'customer.subscription.created':
                subscription = event['data']['object']
                customer_id = subscription['customer']
                
                # Find parent profile by Stripe customer ID
                parent_profile = ParentProfile.query.filter_by(stripe_customer_id=customer_id).first()
                if parent_profile:
                    # Update subscription status
                    status = subscription['status']
                    if status == 'active':
                        expiry_date = datetime.fromtimestamp(subscription['current_period_end'])
                        SubscriptionService.update_subscription_status(parent_profile, 'active', expiry_date)
                    else:
                        SubscriptionService.update_subscription_status(parent_profile, status)
            
            elif event['type'] == 'customer.subscription.updated':
                subscription = event['data']['object']
                customer_id = subscription['customer']
                
                # Find parent profile by Stripe customer ID
                parent_profile = ParentProfile.query.filter_by(stripe_customer_id=customer_id).first()
                if parent_profile:
                    # Update subscription status
                    status = subscription['status']
                    if status == 'active':
                        expiry_date = datetime.fromtimestamp(subscription['current_period_end'])
                        SubscriptionService.update_subscription_status(parent_profile, 'active', expiry_date)
                    else:
                        SubscriptionService.update_subscription_status(parent_profile, status)
            
            elif event['type'] == 'customer.subscription.deleted':
                subscription = event['data']['object']
                customer_id = subscription['customer']
                
                # Find parent profile by Stripe customer ID
                parent_profile = ParentProfile.query.filter_by(stripe_customer_id=customer_id).first()
                if parent_profile:
                    # Update subscription status
                    SubscriptionService.update_subscription_status(parent_profile, 'canceled')
            
            elif event['type'] == 'invoice.payment_succeeded':
                invoice = event['data']['object']
                customer_id = invoice['customer']
                subscription_id = invoice.get('subscription')
                
                if subscription_id:
                    # Find parent profile by Stripe customer ID
                    parent_profile = ParentProfile.query.filter_by(stripe_customer_id=customer_id).first()
                    if parent_profile:
                        # Get subscription details
                        subscription = stripe.Subscription.retrieve(subscription_id)
                        expiry_date = datetime.fromtimestamp(subscription['current_period_end'])
                        
                        # Update subscription status
                        SubscriptionService.update_subscription_status(parent_profile, 'active', expiry_date)
            
            elif event['type'] == 'invoice.payment_failed':
                invoice = event['data']['object']
                customer_id = invoice['customer']
                
                # Find parent profile by Stripe customer ID
                parent_profile = ParentProfile.query.filter_by(stripe_customer_id=customer_id).first()
                if parent_profile:
                    # Update subscription status
                    SubscriptionService.update_subscription_status(parent_profile, 'past_due')
            
            return True, "Webhook event handled successfully"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def get_subscription_plans():
        """Get available subscription plans."""
        try:
            # Get all active products
            products = stripe.Product.list(active=True)
            
            plans = []
            for product in products.data:
                # Get prices for each product
                prices = stripe.Price.list(product=product.id, active=True)
                
                for price in prices.data:
                    plan = {
                        'id': price.id,
                        'product_id': product.id,
                        'name': product.name,
                        'description': product.description,
                        'amount': price.unit_amount / 100,  # Convert from cents to dollars/pounds
                        'currency': price.currency,
                        'interval': price.recurring.interval if price.recurring else None,
                        'interval_count': price.recurring.interval_count if price.recurring else None,
                        'metadata': product.metadata
                    }
                    plans.append(plan)
            
            return True, plans
        except stripe.error.StripeError as e:
            return False, str(e)

