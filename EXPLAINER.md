# EXPLAINER.md — Playto Payout Engine

## 1. The Ledger

**Balance calculation query:**

```python
LedgerEntry.objects.filter(merchant=self).aggregate(
    total=Sum(
        Case(
            When(entry_type='CREDIT', then='amount_paise'),
            When(entry_type='DEBIT', then=F('amount_paise') * -1),
            output_field=BigIntegerField(),
            default=0,
        )
    )
)
```

Credits and debits are modeled as separate immutable rows rather than
a single mutable balance column. This means:

- Balance is always derivable from the ledger — no possibility of the
  balance column drifting from a bug
- Every transaction has a reason and reference ID — full audit trail built-in
- The aggregation runs in one SQL query, never fetching rows into Python memory
- Concurrent writes cannot corrupt a balance column because there is no
  balance column to corrupt

## 2. The Lock

```python
with transaction.atomic():
    # Lock the merchant row — this is the serialization point.
    # Any other transaction trying to lock the same merchant blocks here
    # at the PostgreSQL level until this transaction commits or rolls back.
    merchant_locked = Merchant.objects.select_for_update().get(pk=merchant.pk)

    total_credits = LedgerEntry.objects.filter(
        merchant=merchant_locked, entry_type='CREDIT'
    ).aggregate(t=Sum('amount_paise'))['t'] or 0

    total_debits = LedgerEntry.objects.filter(
        merchant=merchant_locked, entry_type='DEBIT'
    ).aggregate(t=Sum('amount_paise'))['t'] or 0

    held = Payout.objects.filter(
        merchant=merchant_locked, status__in=['PENDING', 'PROCESSING']
    ).aggregate(t=Sum('amount_paise'))['t'] or 0

    available = total_credits - total_debits - held

    if available < amount_paise:
        return Response({'error': 'Insufficient balance'}, status=400)

    Payout.objects.create(...)
    LedgerEntry.objects.create(entry_type='DEBIT', ...)
```

`select_for_update()` maps to PostgreSQL's `SELECT ... FOR UPDATE`.
This acquires a row-level exclusive lock on the Merchant row.
Any concurrent transaction attempting the same lock blocks at the
database level — not Python level — until the first commits or rolls back.

This is the only correct solution. Python-level locks (threading.Lock)
would not work across multiple gunicorn workers or Celery processes.
The balance check and payout creation happen atomically while holding
the lock — this eliminates the TOCTOU (time-of-check-time-of-use)
race condition entirely.

## 3. The Idempotency

Idempotency keys are stored in the `IdempotencyKey` table with a
`unique_together` constraint on `(merchant, key)` and a 24-hour TTL.

**Flow:**
1. Before acquiring any locks, check if `IdempotencyKey` exists for
   `(merchant, key)` with `expires_at > now`
2. If found → return stored `response_body` and `response_status` immediately
3. If not found → proceed with payout creation, then write key + full
   response body atomically inside the transaction

**Race condition during in-flight first request:**
If two identical requests arrive simultaneously before either has written
the idempotency key, both miss the pre-check. The `unique_together`
constraint means only one `get_or_create` will succeed — the other gets
back the existing row. Additionally, `select_for_update` on the Merchant
row means only one will actually create a payout. The second will fail
the balance check (since the first payout reduces available balance)
and return a 400.

Keys are scoped per merchant — the same UUID used by two different
merchants creates two separate valid keys.

## 4. The State Machine

Illegal transitions are blocked in `state_machine.py`:

```python
VALID_TRANSITIONS = {
    'PENDING':    ['PROCESSING'],
    'PROCESSING': ['COMPLETED', 'FAILED'],
    'COMPLETED':  [],   # Terminal — nothing allowed
    'FAILED':     [],   # Terminal — nothing allowed
}

def transition_payout(payout, new_status):
    allowed = Payout.VALID_TRANSITIONS.get(payout.status, [])
    if new_status not in allowed:
        raise InvalidTransitionError(
            f"Transition {payout.status} → {new_status} is illegal."
        )
    # Re-fetch with row lock inside transaction
    with transaction.atomic():
        locked = Payout.objects.select_for_update().get(pk=payout.pk)
        # Double-check after acquiring lock
        allowed = Payout.VALID_TRANSITIONS.get(locked.status, [])
        if new_status not in allowed:
            raise InvalidTransitionError(...)
        locked.status = new_status
        locked.save()
        # FAILED → atomically refund funds to ledger
        if new_status == 'FAILED':
            LedgerEntry.objects.create(
                merchant=locked.merchant,
                entry_type='CREDIT',
                amount_paise=locked.amount_paise,
                description=f'Refund for failed payout {locked.id}',
            )
```

`COMPLETED → PENDING` would require `'PENDING'` to be in
`VALID_TRANSITIONS['COMPLETED']` which is `[]` — so it raises
`InvalidTransitionError`. Every status change in the entire codebase
goes through this single function. There are no direct
`payout.status = 'X'` assignments anywhere else.

Failed payout fund return is atomic with the state transition — both
happen inside the same `transaction.atomic()` block. Either both
commit or neither does.

## 5. The AI Audit

**What AI gave me (wrong):**

```python
# AI-generated balance check — WRONG
merchant = Merchant.objects.get(pk=merchant_id)
balance = merchant.get_balance()  # fetches rows and sums in Python
if balance >= amount_paise:
    Payout.objects.create(...)
    LedgerEntry.objects.create(...)
```

**Why it's wrong:**
This is a classic TOCTOU (time-of-check-time-of-use) race condition.
Between reading the balance and creating the payout, another concurrent
request can also read the same balance. Both see sufficient funds. Both
create payouts. The account is overdrawn.

The AI also initially generated the balance check using Python-level
aggregation outside any transaction, which means the read is not
protected by any lock.

**What I replaced it with:**

```python
with transaction.atomic():
    merchant_locked = Merchant.objects.select_for_update().get(pk=merchant.pk)
    # compute balance INSIDE the lock at DB level
    total_credits = LedgerEntry.objects.filter(
        merchant=merchant_locked, entry_type='CREDIT'
    ).aggregate(t=Sum('amount_paise'))['t'] or 0
    # ... then create payout while still holding the lock
```

The key insight: `select_for_update()` on the Merchant row means
PostgreSQL will not allow any other transaction to read or modify that
row until we commit. The balance check and payout creation are now
a single atomic operation. The concurrency test confirms this:
two simultaneous ₹60 requests against ₹100 balance — exactly one
succeeds, one gets 400, ledger integrity maintained.

## Deployment Note

The live deployment runs on Render free tier which does not support
background workers without payment. Payouts remain in PENDING state
on the live demo at https://playto-payout-weld.vercel.app

The full payout lifecycle (PENDING → PROCESSING → COMPLETED/FAILED)
works correctly in local development with Celery worker running.
To test locally: run `celery -A config worker -l info --pool=solo`
from the backend directory.