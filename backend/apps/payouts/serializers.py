from rest_framework import serializers
from .models import Payout, LedgerEntry


class PayoutSerializer(serializers.ModelSerializer):
    amount_inr = serializers.SerializerMethodField()
    bank_account_last4 = serializers.SerializerMethodField()

    class Meta:
        model = Payout
        fields = ['id', 'merchant', 'amount_paise', 'amount_inr', 'status',
                  'bank_account_last4', 'attempt_count', 'failure_reason',
                  'created_at', 'updated_at']

    def get_amount_inr(self, obj):
        return obj.amount_paise / 100

    def get_bank_account_last4(self, obj):
        return obj.bank_account.account_number[-4:]


class LedgerEntrySerializer(serializers.ModelSerializer):
    amount_inr = serializers.SerializerMethodField()

    class Meta:
        model = LedgerEntry
        fields = ['id', 'entry_type', 'amount_paise', 'amount_inr',
                  'description', 'reference_id', 'created_at']

    def get_amount_inr(self, obj):
        return obj.amount_paise / 100