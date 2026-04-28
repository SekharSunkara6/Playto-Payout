import threading
import json
from django.test import TransactionTestCase, RequestFactory
from django.db import close_old_connections
from apps.merchants.models import Merchant, BankAccount
from apps.payouts.models import LedgerEntry, Payout
from apps.payouts.views import PayoutCreateView


class ConcurrencyTest(TransactionTestCase):
    """
    Uses TransactionTestCase (not TestCase) because:
    - TestCase wraps each test in a transaction that never commits
    - select_for_update() requires REAL committed transactions to work
    - TransactionTestCase flushes the DB after each test instead
    """

    def setUp(self):
        self.factory = RequestFactory()
        self.merchant = Merchant.objects.create(
            name='Concurrency Test Merchant',
            email='concurrent@test.com'
        )
        self.bank = BankAccount.objects.create(
            merchant=self.merchant,
            account_number='1234567890',
            ifsc_code='HDFC0001234',
            account_holder_name='Concurrency Test',
            is_primary=True,
        )
        LedgerEntry.objects.create(
            merchant=self.merchant,
            entry_type='CREDIT',
            amount_paise=10000,
            description='Seed credit for concurrency test',
            reference_id='seed-concurrent-001',
        )

    def _make_payout_request(self, idempotency_key, results, index):
        try:
            close_old_connections()
            request = self.factory.post(
                '/api/v1/payouts/',
                data=json.dumps({
                    'merchant_id': self.merchant.id,
                    'amount_paise': 6000,
                    'bank_account_id': self.bank.id,
                }),
                content_type='application/json',
            )
            request.META['HTTP_IDEMPOTENCY_KEY'] = idempotency_key
            view = PayoutCreateView.as_view()
            response = view(request)
            results[index] = response.status_code
        except Exception as e:
            results[index] = 500
            print(f"\n  Thread {index} raised exception: {e}")
        finally:
            close_old_connections()

    def test_concurrent_overdraw_prevented(self):
        """
        Two simultaneous 60 INR requests against 100 INR balance.
        Exactly one must succeed (201). The other must be rejected (400).
        select_for_update() on Merchant row serializes at PostgreSQL level.
        """
        results = [None, None]

        t1 = threading.Thread(
            target=self._make_payout_request,
            args=('concurrent-thread-key-1', results, 0)
        )
        t2 = threading.Thread(
            target=self._make_payout_request,
            args=('concurrent-thread-key-2', results, 1)
        )

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        print(f"\n  Thread results: {results}")

        successes = results.count(201)
        rejections = results.count(400)

        self.assertEqual(successes, 1,
            f"Expected exactly 1 success (201), got {successes}. Results: {results}")
        self.assertEqual(rejections, 1,
            f"Expected exactly 1 rejection (400), got {rejections}. Results: {results}")

        payout_count = Payout.objects.filter(merchant=self.merchant).count()
        self.assertEqual(payout_count, 1,
            f"Expected 1 payout in DB, got {payout_count}")

        from django.db.models import Sum
        credits = LedgerEntry.objects.filter(
            merchant=self.merchant, entry_type='CREDIT'
        ).aggregate(t=Sum('amount_paise'))['t'] or 0
        debits = LedgerEntry.objects.filter(
            merchant=self.merchant, entry_type='DEBIT'
        ).aggregate(t=Sum('amount_paise'))['t'] or 0

        print(f"  Ledger: credits={credits} debits={debits} remaining={credits-debits}")
        self.assertEqual(credits - debits, 4000,
            f"Ledger integrity violated: {credits} - {debits} = {credits-debits}, expected 4000")