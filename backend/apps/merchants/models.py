from django.db import models
from django.db.models import Sum, Q


class Merchant(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_balance(self):
        """
        CRITICAL: Balance computed at DB level using a single aggregation query.
        Never fetch rows and sum in Python — that breaks under concurrent writes.
        """
        from apps.payouts.models import LedgerEntry
        result = LedgerEntry.objects.filter(merchant=self).aggregate(
            total=Sum(
                models.Case(
                    models.When(entry_type='CREDIT', then='amount_paise'),
                    models.When(entry_type='DEBIT', then=models.F('amount_paise') * -1),
                    output_field=models.BigIntegerField(),
                    default=0,
                )
            )
        )
        return result['total'] or 0

    def get_held_balance(self):
        """Funds locked by pending/processing payouts."""
        from apps.payouts.models import Payout
        result = Payout.objects.filter(
            merchant=self,
            status__in=['PENDING', 'PROCESSING']
        ).aggregate(total=Sum('amount_paise'))
        return result['total'] or 0

    def get_available_balance(self):
        return self.get_balance() - self.get_held_balance()

    def __str__(self):
        return self.name


class BankAccount(models.Model):
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='bank_accounts')
    account_number = models.CharField(max_length=20)
    ifsc_code = models.CharField(max_length=11)
    account_holder_name = models.CharField(max_length=255)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.account_holder_name} — {self.account_number[-4:]}"