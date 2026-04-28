import random
import time
import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta

from apps.payouts.models import Payout
from apps.payouts.state_machine import transition_payout, InvalidTransitionError

logger = logging.getLogger(__name__)

PROCESSING_TIMEOUT_SECONDS = 30
MAX_ATTEMPTS = 3


@shared_task(bind=True, max_retries=3)
def process_payout(self, payout_id: str):
    try:
        payout = Payout.objects.get(pk=payout_id)
    except Payout.DoesNotExist:
        logger.error(f"Payout {payout_id} not found")
        return

    if payout.status not in ('PENDING', 'PROCESSING'):
        logger.info(f"Payout {payout_id} already in terminal state {payout.status}")
        return

    if payout.attempt_count >= MAX_ATTEMPTS:
        transition_payout(payout, 'FAILED', failure_reason='Max retry attempts exceeded')
        return

    # Move to PROCESSING
    try:
        payout = transition_payout(payout, 'PROCESSING')
        payout.attempt_count += 1
        payout.save(update_fields=['attempt_count'])
    except InvalidTransitionError as e:
        logger.warning(str(e))
        return

    # Simulate bank settlement: 70% success, 20% fail, 10% hang
    outcome = random.choices(
        ['success', 'fail', 'hang'],
        weights=[70, 20, 10],
        k=1
    )[0]

    if outcome == 'success':
        transition_payout(payout, 'COMPLETED')
        logger.info(f"Payout {payout_id} completed successfully")

    elif outcome == 'fail':
        transition_payout(payout, 'FAILED', failure_reason='Bank rejected the transfer')
        logger.info(f"Payout {payout_id} failed — funds returned")

    else:  # hang — will be picked up by retry_stuck_payouts
        logger.info(f"Payout {payout_id} hanging in PROCESSING")


@shared_task
def retry_stuck_payouts():
    """
    Runs every 30 seconds. Finds payouts stuck in PROCESSING
    and retries or fails them with exponential backoff.
    """
    cutoff = timezone.now() - timedelta(seconds=PROCESSING_TIMEOUT_SECONDS)
    stuck = Payout.objects.filter(
        status='PROCESSING',
        processing_started_at__lt=cutoff
    )

    for payout in stuck:
        logger.info(f"Found stuck payout {payout.id}, attempt {payout.attempt_count}")
        if payout.attempt_count >= MAX_ATTEMPTS:
            transition_payout(payout, 'FAILED', failure_reason='Timed out after max retries')
        else:
            # Reset to PENDING so process_payout can re-run it
            # Use exponential backoff: 2^attempt seconds
            backoff = 2 ** payout.attempt_count
            payout.status = 'PENDING'
            payout.processing_started_at = None
            payout.save(update_fields=['status', 'processing_started_at', 'updated_at'])
            process_payout.apply_async(args=[str(payout.id)], countdown=backoff)