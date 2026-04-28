import uuid
from django.db import models
from django.utils import timezone


class LedgerEntry(models.Model):
    ENTRY_TYPES = [('CREDIT', 'Credit'), ('DEBIT', 'Debit')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    merchant = models.ForeignKey('merchants.Merchant', on_delete=models.PROTECT, related_name='ledger_entries')
    entry_type = models.CharField(max_length=6, choices=ENTRY_TYPES)
    amount_paise = models.BigIntegerField()           # NEVER FloatField
    description = models.CharField(max_length=500)
    reference_id = models.CharField(max_length=255, blank=True)  # payout ID or payment ID
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['merchant', 'created_at'])]

    def __str__(self):
        return f"{self.entry_type} ₹{self.amount_paise/100:.2f} for {self.merchant}"


class IdempotencyKey(models.Model):
    merchant = models.ForeignKey('merchants.Merchant', on_delete=models.CASCADE)
    key = models.CharField(max_length=255)
    response_body = models.JSONField()
    response_status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        unique_together = ('merchant', 'key')   # Key scoped per merchant
        indexes = [models.Index(fields=['merchant', 'key'])]


class Payout(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    # Valid state transitions — enforced in state_machine.py
    VALID_TRANSITIONS = {
        'PENDING': ['PROCESSING'],
        'PROCESSING': ['COMPLETED', 'FAILED'],
        'COMPLETED': [],       # Terminal
        'FAILED': [],          # Terminal
    }

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    merchant = models.ForeignKey('merchants.Merchant', on_delete=models.PROTECT, related_name='payouts')
    bank_account = models.ForeignKey('merchants.BankAccount', on_delete=models.PROTECT)
    amount_paise = models.BigIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    attempt_count = models.IntegerField(default=0)
    idempotency_key = models.CharField(max_length=255, blank=True)
    failure_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processing_started_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['merchant', 'status']),
            models.Index(fields=['status', 'processing_started_at']),
        ]