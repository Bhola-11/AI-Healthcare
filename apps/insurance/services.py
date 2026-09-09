from decimal import Decimal
from django.utils import timezone
from .models import InsuranceClaim

class ClaimAdjudicationService:
    @staticmethod
    def adjudicate_claim(claim, approved_rate_percent=80.0):
        # Calculate covered amount vs patient co-pay
        rate = Decimal(str(approved_rate_percent)) / Decimal("100.0")
        approved = round(claim.claimed_amount * rate, 2)
        copay = claim.policy.copay_amount
        
        claim.approved_amount = approved
        claim.copay_collected = copay
        claim.status = InsuranceClaim.ClaimStatus.APPROVED
        claim.adjudicated_at = timezone.now()
        claim.adjudication_notes = f"Adjudicated at standard contractual allowance of {approved_rate_percent}%."
        claim.save()
        return claim
