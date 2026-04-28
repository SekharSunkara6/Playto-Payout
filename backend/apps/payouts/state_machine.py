from django.db import transaction
from django.utils import timezone
from apps.payouts.models import Payout, LedgerEntry


class InvalidTransitionError(Exception):
    pass


def transition_payout(payout: Payout, new_status: str, failure_reason: str = '') -> Payout:
    """
    THE ONLY place where payout status changes happen.
    Enforces legal transitions. Atomic with ledger writes.
    """
    allowed = Payout.VALID_TRANSITIONS.get(payout.status, [])
    if new_status not in allowed:
        raise InvalidTransitionError(
            f"Transition {payout.status} → {new_status} is illegal."
        )

    with transaction.atomic():
        # Re-fetch with row lock inside transaction
        locked_payout = Payout.objects.select_for_update().get(pk=payout.pk)

        # Double-check after acquiring lock (state may have changed)
        allowed = Payout.VALID_TRANSITIONS.get(locked_payout.status, [])
        if new_status not in allowed:
            raise InvalidTransitionError(
                f"Transition {locked_payout.status} → {new_status} is illegal (post-lock check)."
            )

        locked_payout.status = new_status
        if new_status == 'PROCESSING':
            locked_payout.processing_started_at = timezone.now()
        if new_status in ('COMPLETED', 'FAILED'):
            locked_payout.failure_reason = failure_reason

        locked_payout.save(update_fields=['status', 'processing_started_at',
                                          'failure_reason', 'updated_at'])

        # On FAILED: atomically return funds to ledger
        if new_status == 'FAILED':
            LedgerEntry.objects.create(
                merchant=locked_payout.merchant,
                entry_type='CREDIT',
                amount_paise=locked_payout.amount_paise,
                description=f'Refund for failed payout {locked_payout.id}',
                reference_id=str(locked_payout.id),
            )

    return locked_payout