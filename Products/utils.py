import stripe
from django.conf import settings
from decimal import Decimal
from django.db.models import Sum
stripe.api_key = settings.STRIPE_SECRET_KEY
from UserProfile.models import Commission
from Products.models import CreatorWithdrawal
def retrieve_connected_account(user):
    if not user.stripe_account_id:
        return None
    return stripe.Account.retrieve(user.stripe_account_id)


def refresh_stripe_account_status(user):
    """
    Returns latest Stripe account object for the connected account.
    """
    try:
        if not user.stripe_account_id:
            return None

        account = stripe.Account.retrieve(user.stripe_account_id)
        return {
            "account": account,
            "charges_enabled": account.get("charges_enabled", False),
            "payouts_enabled": account.get("payouts_enabled", False),
            "details_submitted": account.get("details_submitted", False),
        }
    except Exception as e:
        print(f"Stripe sync error: {e}")
        return None
    
    
    


def get_creator_available_balance(user):
    total_commission = Commission.objects.filter(
        creator=user
    ).aggregate(total=Sum("commission_amount"))["total"] or Decimal("0.00")

    total_withdrawn = CreatorWithdrawal.objects.filter(
        creator=user,
        status__in=["pending", "processing", "completed"]
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

    return total_commission - total_withdrawn



