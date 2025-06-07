import os
import stripe
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from src.models import ParentProfile, User, UserRole, db
from src.services.subscription_service import SubscriptionService

subscription_bp = Blueprint('subscription', __name__)

# Initialize Stripe with API key
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'sk_test_your_test_key')

@subscription_bp.route('/plans', methods=['GET'])
def get_subscription_plans():
    """Get available subscription plans."""
    success, result = SubscriptionService.get_subscription_plans()
    
    if not success:
        return jsonify({"error": result}), 500
    
    return jsonify(result)

@subscription_bp.route('/checkout-session', methods=['POST'])
@jwt_required()
def create_checkout_session():
    """Create a Stripe Checkout session for subscription."""
    # Check if user is a parent
    user_id = get_jwt_identity()
    user_role = get_jwt().get('role')
    
    if user_role != UserRole.PARENT.value:
        return jsonify({"error": "Only parents can subscribe"}), 403
    
    # Get parent profile
    parent_profile = ParentProfile.query.filter_by(user_id=user_id).first()
    if not parent_profile:
        return jsonify({"error": "Parent profile not found"}), 404
    
    data = request.json
    
    # Check required fields
    if 'price_id' not in data:
        return jsonify({"error": "Missing required field: price_id"}), 400
    
    try:
        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            customer_email=parent_profile.user.email,
            payment_method_types=['card'],
            line_items=[
                {
                    'price': data['price_id'],
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=data.get('success_url', request.host_url + 'subscription/success'),
            cancel_url=data.get('cancel_url', request.host_url + 'subscription/cancel'),
            metadata={
                'parent_id': parent_profile.id,
                'user_id': parent_profile.user_id
            }
        )
        
        return jsonify({"checkout_url": checkout_session.url})
    except stripe.error.StripeError as e:
        return jsonify({"error": str(e)}), 500

@subscription_bp.route('/create-customer', methods=['POST'])
@jwt_required()
def create_customer():
    """Create a Stripe customer for a parent."""
    # Check if user is a parent
    user_id = get_jwt_identity()
    user_role = get_jwt().get('role')
    
    if user_role != UserRole.PARENT.value:
        return jsonify({"error": "Only parents can create customers"}), 403
    
    # Get parent profile
    parent_profile = ParentProfile.query.filter_by(user_id=user_id).first()
    if not parent_profile:
        return jsonify({"error": "Parent profile not found"}), 404
    
    data = request.json
    
    # Create customer
    success, result = SubscriptionService.create_customer(
        parent_profile,
        payment_method_id=data.get('payment_method_id')
    )
    
    if not success:
        return jsonify({"error": result}), 500
    
    return jsonify({
        "customer_id": result.id,
        "email": result.email,
        "name": result.name
    })

@subscription_bp.route('/create-subscription', methods=['POST'])
@jwt_required()
def create_subscription():
    """Create a subscription for a parent."""
    # Check if user is a parent
    user_id = get_jwt_identity()
    user_role = get_jwt().get('role')
    
    if user_role != UserRole.PARENT.value:
        return jsonify({"error": "Only parents can create subscriptions"}), 403
    
    # Get parent profile
    parent_profile = ParentProfile.query.filter_by(user_id=user_id).first()
    if not parent_profile:
        return jsonify({"error": "Parent profile not found"}), 404
    
    data = request.json
    
    # Check required fields
    if 'price_id' not in data:
        return jsonify({"error": "Missing required field: price_id"}), 400
    
    # Create subscription
    success, result = SubscriptionService.create_subscription(
        parent_profile,
        data['price_id']
    )
    
    if not success:
        return jsonify({"error": result}), 500
    
    return jsonify({
        "subscription_id": result.id,
        "status": result.status,
        "current_period_end": result.current_period_end,
        "client_secret": result.latest_invoice.payment_intent.client_secret if result.latest_invoice and result.latest_invoice.payment_intent else None
    })

@subscription_bp.route('/cancel-subscription', methods=['POST'])
@jwt_required()
def cancel_subscription():
    """Cancel a parent's subscription."""
    # Check if user is a parent
    user_id = get_jwt_identity()
    user_role = get_jwt().get('role')
    
    if user_role != UserRole.PARENT.value:
        return jsonify({"error": "Only parents can cancel subscriptions"}), 403
    
    # Get parent profile
    parent_profile = ParentProfile.query.filter_by(user_id=user_id).first()
    if not parent_profile:
        return jsonify({"error": "Parent profile not found"}), 404
    
    # Cancel subscription
    success, result = SubscriptionService.cancel_subscription(parent_profile)
    
    if not success:
        return jsonify({"error": result}), 500
    
    return jsonify({"message": result})

@subscription_bp.route('/status', methods=['GET'])
@jwt_required()
def get_subscription_status():
    """Get a parent's subscription status."""
    # Check if user is a parent
    user_id = get_jwt_identity()
    user_role = get_jwt().get('role')
    
    if user_role != UserRole.PARENT.value:
        return jsonify({"error": "Only parents can view subscription status"}), 403
    
    # Get parent profile
    parent_profile = ParentProfile.query.filter_by(user_id=user_id).first()
    if not parent_profile:
        return jsonify({"error": "Parent profile not found"}), 404
    
    # Get subscription status
    return jsonify({
        "status": parent_profile.subscription_status,
        "expiry": parent_profile.subscription_expiry.isoformat() if parent_profile.subscription_expiry else None,
        "customer_id": parent_profile.stripe_customer_id
    })

@subscription_bp.route('/webhook', methods=['POST'])
def webhook():
    """Handle Stripe webhook events."""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        # Verify webhook signature
        webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET', 'whsec_your_webhook_secret')
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        # Invalid payload
        return jsonify({"error": "Invalid payload"}), 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return jsonify({"error": "Invalid signature"}), 400
    
    # Handle the event
    success, result = SubscriptionService.handle_webhook_event(event)
    
    if not success:
        current_app.logger.error(f"Error handling webhook: {result}")
        return jsonify({"error": result}), 500
    
    return jsonify({"received": True})

