import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.merchants.models import Merchant, BankAccount
from apps.payouts.models import LedgerEntry

Merchant.objects.all().delete()

merchants_data = [
    {'name': 'Arjun Sharma Designs', 'email': 'arjun@designs.in'},
    {'name': 'Priya Tech Solutions', 'email': 'priya@techsol.in'},
    {'name': 'Rahul Content Studio', 'email': 'rahul@contentstudio.in'},
]

for i, m in enumerate(merchants_data):
    merchant = Merchant.objects.create(**m)
    BankAccount.objects.create(
        merchant=merchant,
        account_number=f'50100{i+1}234567890',
        ifsc_code='HDFC0001234',
        account_holder_name=m['name'],
        is_primary=True,
    )
    # Seed credits (simulated incoming payments)
    for amount, desc in [
        (500000, 'Client payment - Logo design project'),
        (150000, 'Client payment - Social media package'),
        (250000, 'Client payment - Website redesign'),
    ]:
        LedgerEntry.objects.create(
            merchant=merchant,
            entry_type='CREDIT',
            amount_paise=amount,
            description=desc,
            reference_id=f'pay_{i}_{amount}',
        )
    print(f"Seeded: {merchant.name}")

print("Done! Run: python manage.py runserver")