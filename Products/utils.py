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



def get_connected_account_payout_info(stripe_account_id):
    """
    Returns withdraw method + bank/card display info
    """
    try:
        bank_accounts = stripe.Account.list_external_accounts(
            stripe_account_id,
            object="bank_account",
            limit=10
        )

        if bank_accounts.data:
            bank = bank_accounts.data[0]
            return {
                "withdraw_method": "bank_account",
                "bank_name": bank.get("bank_name"),
                "bank_last4": bank.get("last4"),
            }

        cards = stripe.Account.list_external_accounts(
            stripe_account_id,
            object="card",
            limit=10
        )

        if cards.data:
            card = cards.data[0]
            return {
                "withdraw_method": "debit_card",
                "bank_name": f"{card.get('brand', 'Card')} Card",
                "bank_last4": card.get("last4"),
            }

    except Exception as e:
        print("Payout info detect error:", e)

    return {
        "withdraw_method": "unknown",
        "bank_name": None,
        "bank_last4": None,
    }