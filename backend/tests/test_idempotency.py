from django.test import TestCase, Client
from apps.merchants.models import Merchant, BankAccount
from apps.payouts.models import LedgerEntry, Payout


class IdempotencyTest(TestCase):
    def setUp(self):
        self.merchant = Merchant.objects.create(name='Idem Test', email='idem@t.com')
        self.bank = BankAccount.objects.create(
            merchant=self.merchant, account_number='9876543210',
            ifsc_code='ICIC0001234', account_holder_name='Idem Test'
        )
        LedgerEntry.objects.create(
            merchant=self.merchant, entry_type='CREDIT',
            amount_paise=50000, description='seed'
        )
        self.client = Client()

    def test_same_key_returns_same_response(self):
        """Two requests with identical idempotency key → identical response, one payout created."""
        payload = {
            'merchant_id': self.merchant.id,
            'amount_paise': 5000,
            'bank_account_id': self.bank.id,
        }
        r1 = self.client.post('/api/v1/payouts/', data=payload,
                              content_type='application/json',
                              HTTP_IDEMPOTENCY_KEY='unique-key-123')
        r2 = self.client.post('/api/v1/payouts/', data=payload,
                              content_type='application/json',
                              HTTP_IDEMPOTENCY_KEY='unique-key-123')

        self.assertEqual(r1.status_code, 201)
        self.assertEqual(r2.status_code, 201)
        self.assertEqual(r1.json()['id'], r2.json()['id'])
        # Only ONE payout should exist
        self.assertEqual(Payout.objects.filter(merchant=self.merchant).count(), 1)

    def test_different_keys_create_different_payouts(self):
        """Different keys create separate payouts."""
        payload = {'merchant_id': self.merchant.id, 'amount_paise': 2000,
                   'bank_account_id': self.bank.id}
        r1 = self.client.post('/api/v1/payouts/', data=payload,
                              content_type='application/json', HTTP_IDEMPOTENCY_KEY='key-A')
        r2 = self.client.post('/api/v1/payouts/', data=payload,
                              content_type='application/json', HTTP_IDEMPOTENCY_KEY='key-B')
        self.assertNotEqual(r1.json()['id'], r2.json()['id'])
        self.assertEqual(Payout.objects.filter(merchant=self.merchant).count(), 2)