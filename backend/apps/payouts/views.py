import uuid
from django.db import transaction
from django.db.models import Sum, Q, F, Case, When, BigIntegerField
from django.utils import timezone
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.merchants.models import Merchant, BankAccount
from apps.payouts.models import Payout, LedgerEntry, IdempotencyKey
from apps.payouts.serializers import PayoutSerializer, LedgerEntrySerializer
from apps.payouts.tasks import process_payout


class PayoutCreateView(APIView):

    def post(self, request):
        merchant_id = request.data.get('merchant_id')
        amount_paise = request.data.get('amount_paise')
        bank_account_id = request.data.get('bank_account_id')
        idempotency_key = request.headers.get('Idempotency-Key')

        if not all([merchant_id, amount_paise, bank_account_id, idempotency_key]):
            return Response({'error': 'merchant_id, amount_paise, bank_account_id, Idempotency-Key required'}, status=400)

        try:
            amount_paise = int(amount_paise)
            assert amount_paise > 0
        except (ValueError, AssertionError):
            return Response({'error': 'amount_paise must be a positive integer'}, status=400)

        try:
            merchant = Merchant.objects.get(pk=merchant_id)
            bank_account = BankAccount.objects.get(pk=bank_account_id, merchant=merchant)
        except Merchant.DoesNotExist:
            return Response({'error': 'Merchant not found'}, status=404)
        except BankAccount.DoesNotExist:
            return Response({'error': 'BankAccount not found'}, status=404)

        now = timezone.now()

        # Fast-path idempotency check BEFORE acquiring lock
        existing_key = IdempotencyKey.objects.filter(
            merchant=merchant,
            key=idempotency_key,
            expires_at__gt=now
        ).first()
        if existing_key:
            return Response(existing_key.response_body, status=existing_key.response_status)

        # --- CRITICAL SECTION ---
        # We use a dedicated merchant-level advisory lock via SELECT FOR UPDATE
        # on the Merchant row itself. This is the correct pattern:
        # lock the merchant row → compute balance → create payout atomically.
        # All concurrent requests for the same merchant queue here at DB level.
        try:
            with transaction.atomic():
                # Lock the merchant row — this is the serialization point.
                # Any other transaction trying to lock the same merchant blocks here.
                merchant_locked = Merchant.objects.select_for_update().get(pk=merchant.pk)

                # Compute total credits
                total_credits = LedgerEntry.objects.filter(
                    merchant=merchant_locked, entry_type='CREDIT'
                ).aggregate(t=Sum('amount_paise'))['t'] or 0

                # Compute total debits
                total_debits = LedgerEntry.objects.filter(
                    merchant=merchant_locked, entry_type='DEBIT'
                ).aggregate(t=Sum('amount_paise'))['t'] or 0

                # Funds held by in-flight payouts
                held = Payout.objects.filter(
                    merchant=merchant_locked,
                    status__in=['PENDING', 'PROCESSING']
                ).aggregate(t=Sum('amount_paise'))['t'] or 0

                available = total_credits - total_debits - held

                if available < amount_paise:
                    return Response({
                        'error': 'Insufficient balance',
                        'available_paise': available,
                        'requested_paise': amount_paise,
                    }, status=400)

                # Create payout
                payout = Payout.objects.create(
                    merchant=merchant_locked,
                    bank_account=bank_account,
                    amount_paise=amount_paise,
                    status='PENDING',
                    idempotency_key=idempotency_key,
                )

                # Write debit ledger entry
                LedgerEntry.objects.create(
                    merchant=merchant_locked,
                    entry_type='DEBIT',
                    amount_paise=amount_paise,
                    description=f'Payout initiated #{str(payout.id)[:8]}',
                    reference_id=str(payout.id),
                )

                response_data = PayoutSerializer(payout).data
                response_status_code = 201

                # Save idempotency key atomically with the payout
                IdempotencyKey.objects.get_or_create(
                    merchant=merchant_locked,
                    key=idempotency_key,
                    defaults={
                        'response_body': response_data,
                        'response_status': response_status_code,
                        'expires_at': now + timedelta(hours=24),
                    }
                )

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=500)

        # Dispatch to Celery OUTSIDE transaction so worker can see committed data
        try:
            process_payout.apply_async(args=[str(payout.id)], countdown=2)
        except Exception:
            pass  # Celery unavailable in test environment — payout still created

        return Response(response_data, status=response_status_code)


class PayoutListView(APIView):
    def get(self, request):
        merchant_id = request.query_params.get('merchant_id')
        if not merchant_id:
            return Response({'error': 'merchant_id required'}, status=400)
        payouts = Payout.objects.filter(
            merchant_id=merchant_id
        ).select_related('bank_account').order_by('-created_at')[:50]
        return Response(PayoutSerializer(payouts, many=True).data)


class MerchantBalanceView(APIView):
    def get(self, request, merchant_id):
        try:
            merchant = Merchant.objects.get(pk=merchant_id)
        except Merchant.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)
        return Response({
            'merchant_id': merchant.id,
            'merchant_name': merchant.name,
            'total_balance_paise': merchant.get_balance(),
            'held_balance_paise': merchant.get_held_balance(),
            'available_balance_paise': merchant.get_available_balance(),
        })


class LedgerView(APIView):
    def get(self, request, merchant_id):
        try:
            merchant = Merchant.objects.get(pk=merchant_id)
        except Merchant.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)
        entries = LedgerEntry.objects.filter(
            merchant=merchant
        ).order_by('-created_at')[:100]
        return Response(LedgerEntrySerializer(entries, many=True).data)