# ⚡ Playto Payout Engine

Cross-border payout infrastructure for Indian agencies, freelancers, and online businesses.
Built for the **Playto Founding Engineer Challenge 2026**.

---

## 🌐 Live Demo

| Service | URL |
|---------|-----|
| 🎨 Frontend Dashboard | https://playto-payout-weld.vercel.app |
| 🔌 Backend API | https://playto-payout-1yb3.onrender.com |
| 📡 Merchants API | https://playto-payout-1yb3.onrender.com/api/v1/merchants/ |
| 💰 Balance API | https://playto-payout-1yb3.onrender.com/api/v1/merchants/1/balance/ |

---

## 🏗️ Architecture Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────┐
│   React + Vite  │────▶│  Django + DRF    │────▶│  PostgreSQL │
│   Tailwind CSS  │     │  Gunicorn WSGI   │     │  (Neon)     │
│   Vercel CDN    │     │  Render Free     │     └─────────────┘
└─────────────────┘     └──────────────────┘            │
                               │                         │
                        ┌──────▼──────┐         ┌───────▼──────┐
                        │   Celery    │         │    Ledger    │
                        │   Worker   │         │   Entries    │
                        └──────┬──────┘         └─────────────┘
                               │
                        ┌──────▼──────┐
                        │    Redis    │
                        │  (Upstash)  │
                        └─────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| 🎨 Frontend | React 18 + Vite + Tailwind CSS | Merchant dashboard with live updates |
| 🔌 Backend | Django 4.2 + Django REST Framework | REST API with atomic transactions |
| 🗄️ Database | PostgreSQL (Neon) | Row-level locking, BigIntegerField |
| 📬 Queue | Celery 5.3 + Redis (Upstash) | Async payout processing |
| 🔄 Scheduler | Celery Beat | Retry stuck payouts every 30s |
| 🚀 Deployment | Render + Vercel + Neon + Upstash | Full production stack |

---

## 🚀 Local Setup

### 📋 Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL (running locally)
- Redis (running locally)

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/SekharSunkara6/Playto-Payout.git
cd Playto-Payout
```

### 2️⃣ Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3️⃣ Environment Variables

Create `backend/.env`:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=playto
DB_USER=postgres
DB_PASSWORD=your-postgres-password
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
ALLOWED_HOSTS=*
DJANGO_SETTINGS_MODULE=config.settings.development
```

### 4️⃣ Database Setup

```bash
# Run migrations
python manage.py migrate

# Seed test data (3 merchants with credit history)
python seed.py
```

### 5️⃣ Frontend Setup

```bash
cd frontend
npm install
```

Create `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

---

## ▶️ Running Locally

Open **4 terminal windows** simultaneously:

**Terminal 1 — Django Server**
```bash
cd backend
venv\Scripts\activate
python manage.py runserver
```

**Terminal 2 — Celery Worker**
```bash
cd backend
venv\Scripts\activate
celery -A config worker -l info --pool=solo
```

**Terminal 3 — Celery Beat Scheduler**
```bash
cd backend
venv\Scripts\activate
celery -A config beat -l info
```

**Terminal 4 — Frontend**
```bash
cd frontend
npm run dev
```

Open **http://localhost:5173** 🎉

---

## 🧪 Running Tests

```bash
cd backend
python manage.py test tests -v 2
```

### Test Coverage

| Test | Description | Type |
|------|-------------|------|
| `test_concurrent_overdraw_prevented` | Two simultaneous ₹60 requests against ₹100 balance — exactly one succeeds | `TransactionTestCase` |
| `test_same_key_returns_same_response` | Same idempotency key returns identical response, one payout created | `TestCase` |
| `test_different_keys_create_different_payouts` | Different keys create separate payouts | `TestCase` |

Expected output:
```
Ran 3 tests in 11.5s
OK
```

---

## 📡 API Reference

### Base URL
```
https://playto-payout-1yb3.onrender.com/api/v1
```

### Endpoints

#### 🏪 Merchants

```http
GET /merchants/
```
Returns all merchants with bank accounts.

```http
GET /merchants/{id}/balance/
```
Returns total, available and held balance in paise.

```http
GET /merchants/{id}/ledger/
```
Returns full credit/debit ledger history.

#### 💸 Payouts

```http
POST /payouts/
Headers: Idempotency-Key: <uuid>
Body: {
  "merchant_id": 1,
  "amount_paise": 50000,
  "bank_account_id": 1
}
```
Creates a payout request. Returns same response for duplicate keys.

```http
GET /payouts/list/?merchant_id={id}
```
Returns payout history with live status.

### Example Request

```bash
curl -X POST https://playto-payout-1yb3.onrender.com/api/v1/payouts/ \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: unique-uuid-here" \
  -d '{"merchant_id": 1, "amount_paise": 50000, "bank_account_id": 1}'
```

### Payout Status Flow

```
PENDING ──▶ PROCESSING ──▶ COMPLETED
                    │
                    └──▶ FAILED (funds returned atomically)
```

---

## 🔐 Key Engineering Decisions

### 💰 Money as Paise — BigIntegerField Only

```python
amount_paise = models.BigIntegerField()  # NEVER FloatField or DecimalField
```

All amounts stored as integers in paise (1 INR = 100 paise).
Eliminates floating point errors entirely in financial calculations.

### 📊 Database-level Balance Calculation

```python
LedgerEntry.objects.filter(merchant=self).aggregate(
    total=Sum(
        Case(
            When(entry_type='CREDIT', then='amount_paise'),
            When(entry_type='DEBIT', then=F('amount_paise') * -1),
            output_field=BigIntegerField(),
        )
    )
)
```

Balance derived from a single DB aggregation — never Python arithmetic
on fetched rows. Prevents stale reads under concurrent load.

### 🔒 SELECT FOR UPDATE — Concurrency Lock

```python
with transaction.atomic():
    merchant_locked = Merchant.objects.select_for_update().get(pk=merchant.pk)
    # balance check + payout creation happens atomically
```

Merchant row locked at PostgreSQL level during payout creation.
Two simultaneous requests against insufficient balance — exactly one
succeeds. Proven by `TransactionTestCase` concurrency test.

### 🔑 Idempotency Keys

```python
IdempotencyKey.objects.get_or_create(
    merchant=merchant,
    key=idempotency_key,
    defaults={'response_body': response_data, 'expires_at': now + timedelta(hours=24)}
)
```

Merchant-scoped UUID keys with 24h TTL. Safe to retry on network failure.
`unique_together` constraint prevents duplicate key creation under race conditions.

### ⚙️ State Machine

```python
VALID_TRANSITIONS = {
    'PENDING':    ['PROCESSING'],
    'PROCESSING': ['COMPLETED', 'FAILED'],
    'COMPLETED':  [],   # Terminal
    'FAILED':     [],   # Terminal
}
```

All transitions go through a single `transition_payout()` function.
Illegal transitions raise `InvalidTransitionError`.
Failed payout refunds are atomic with the state transition.

### 🔄 Retry Logic

- Payouts stuck in PROCESSING for 30+ seconds are retried automatically
- Exponential backoff: 2^attempt seconds
- Max 3 attempts then moves to FAILED and returns funds
- Celery Beat scheduler fires every 30 seconds

---

## 🌱 Seed Data

3 merchants pre-loaded with credit history:

| Merchant | Balance | Credits |
|----------|---------|---------|
| Arjun Sharma Designs | ₹9,000 | Logo design, Social media, Website |
| Priya Tech Solutions | ₹9,000 | Logo design, Social media, Website |
| Rahul Content Studio | ₹9,000 | Logo design, Social media, Website |

---

## 📁 Project Structure

```
playto-payout/
├── 📂 backend/
│   ├── 📂 apps/
│   │   ├── 📂 merchants/          # Merchant model + bank accounts
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   └── urls.py
│   │   └── 📂 payouts/            # Payout engine
│   │       ├── models.py          # Payout, LedgerEntry, IdempotencyKey
│   │       ├── views.py           # PayoutCreateView with locking
│   │       ├── tasks.py           # Celery worker tasks
│   │       ├── state_machine.py   # State transition enforcement
│   │       └── urls.py
│   ├── 📂 config/
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   └── production.py
│   │   ├── celery.py
│   │   └── urls.py
│   ├── 📂 tests/
│   │   ├── test_concurrency.py    # TransactionTestCase
│   │   └── test_idempotency.py    # Idempotency tests
│   ├── seed.py
│   └── requirements.txt
├── 📂 frontend/
│   ├── 📂 src/
│   │   ├── 📂 components/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── BalanceCard.jsx
│   │   │   ├── PayoutForm.jsx
│   │   │   ├── PayoutTable.jsx
│   │   │   ├── LedgerTable.jsx
│   │   │   └── StatusBadge.jsx
│   │   └── 📂 api/
│   │       └── client.js
│   └── package.json
├── 📄 EXPLAINER.md
├── 📄 README.md
├── 📄 docker-compose.yml
└── 📄 render.yaml
```

---

## 🐳 Docker Setup (Optional)

```bash
# Start all services with one command
docker-compose up
```

Services started:
- PostgreSQL on port 5432
- Redis on port 6379
- Django backend on port 8000
- Celery worker
- React frontend on port 5173

---

## 📝 Submission

- 🔗 **GitHub:** https://github.com/SekharSunkara6/Playto-Payout
- 🌐 **Live Demo:** https://playto-payout-weld.vercel.app
- 📧 **Challenge:** Playto Founding Engineer Challenge 2026
