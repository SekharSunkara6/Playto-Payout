from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.utils import timezone


def api_home(request):
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Playto Pay — Payout Engine</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: #0a0a0f;
    color: #e2e8f0;
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    min-height: 100vh;
  }

  /* NAV */
  nav {
    border-bottom: 1px solid #1e1e2e;
    background: rgba(15,15,25,0.9);
    backdrop-filter: blur(12px);
    padding: 0 40px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 64px;
    position: sticky;
    top: 0;
    z-index: 100;
  }
  .nav-brand { display: flex; align-items: center; gap: 10px; }
  .nav-icon {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, #7c3aed, #4f46e5);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
    box-shadow: 0 4px 16px rgba(124,58,237,0.4);
  }
  .nav-title { font-size: 16px; font-weight: 700; color: #fff; }
  .nav-subtitle { font-size: 11px; color: #475569; margin-top: 1px; }
  .nav-links { display: flex; gap: 8px; }
  .nav-btn {
    padding: 7px 16px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 500;
    text-decoration: none;
    transition: all 0.2s;
    cursor: pointer;
    border: none;
  }
  .nav-btn-ghost { background: transparent; color: #64748b; border: 1px solid transparent; }
  .nav-btn-ghost:hover { background: #1a1a2e; color: #a78bfa; border-color: #2d2d44; }
  .nav-btn-primary {
    background: linear-gradient(135deg, #7c3aed, #4f46e5);
    color: white;
    box-shadow: 0 2px 12px rgba(124,58,237,0.3);
  }
  .nav-btn-primary:hover { opacity: 0.85; transform: translateY(-1px); }

  /* HERO */
  .hero {
    padding: 80px 40px 60px;
    max-width: 900px;
    margin: 0 auto;
    text-align: center;
  }
  .hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(124,58,237,0.12);
    border: 1px solid rgba(124,58,237,0.3);
    border-radius: 100px;
    padding: 6px 14px;
    font-size: 12px;
    color: #a78bfa;
    margin-bottom: 28px;
    font-weight: 500;
  }
  .status-dot {
    width: 7px; height: 7px;
    background: #22c55e;
    border-radius: 50%;
    box-shadow: 0 0 8px #22c55e;
    animation: blink 2s infinite;
  }
  @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }
  .hero h1 {
    font-size: 52px;
    font-weight: 800;
    line-height: 1.1;
    margin-bottom: 20px;
    letter-spacing: -1px;
  }
  .hero h1 span {
    background: linear-gradient(135deg, #a78bfa, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .hero p {
    font-size: 18px;
    color: #64748b;
    max-width: 580px;
    margin: 0 auto 36px;
    line-height: 1.7;
  }
  .hero-buttons { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; }
  .btn-hero {
    padding: 13px 28px;
    border-radius: 12px;
    font-size: 15px;
    font-weight: 600;
    text-decoration: none;
    transition: all 0.2s;
    display: inline-flex;
    align-items: center;
    gap: 8px;
  }
  .btn-hero-primary {
    background: linear-gradient(135deg, #7c3aed, #4f46e5);
    color: white;
    box-shadow: 0 4px 20px rgba(124,58,237,0.4);
  }
  .btn-hero-primary:hover { transform: translateY(-2px); box-shadow: 0 8px 30px rgba(124,58,237,0.5); }
  .btn-hero-outline {
    background: transparent;
    color: #94a3b8;
    border: 1px solid #1e1e2e;
  }
  .btn-hero-outline:hover { border-color: #7c3aed; color: #a78bfa; background: rgba(124,58,237,0.05); }

  /* MAIN */
  .main { max-width: 900px; margin: 0 auto; padding: 0 40px 80px; }

  /* STATS */
  .stats {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 40px;
  }
  .stat-card {
    background: #111118;
    border: 1px solid #1e1e2e;
    border-radius: 16px;
    padding: 20px;
    transition: border-color 0.2s;
  }
  .stat-card:hover { border-color: #7c3aed44; }
  .stat-icon { font-size: 24px; margin-bottom: 12px; }
  .stat-label { font-size: 11px; color: #475569; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }
  .stat-value { font-size: 15px; font-weight: 700; color: #fff; }
  .stat-value.green { color: #4ade80; }
  .stat-value.violet { color: #a78bfa; }
  .stat-value.blue { color: #60a5fa; }

  /* SECTION */
  .section { margin-bottom: 36px; }
  .section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 16px;
  }
  .section-icon {
    width: 32px; height: 32px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 15px;
  }
  .section-title { font-size: 14px; font-weight: 600; color: #fff; }
  .section-subtitle { font-size: 12px; color: #475569; margin-top: 1px; }

  /* ENDPOINTS */
  .endpoints-card {
    background: #111118;
    border: 1px solid #1e1e2e;
    border-radius: 16px;
    overflow: hidden;
  }
  .endpoint {
    display: flex;
    align-items: center;
    padding: 14px 20px;
    border-bottom: 1px solid #1a1a28;
    gap: 14px;
    transition: background 0.15s;
    cursor: default;
  }
  .endpoint:last-child { border-bottom: none; }
  .endpoint:hover { background: #16161f; }
  .method {
    font-size: 11px;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 6px;
    min-width: 46px;
    text-align: center;
    letter-spacing: 0.3px;
  }
  .get { background: rgba(14,116,144,0.2); color: #22d3ee; border: 1px solid rgba(14,116,144,0.3); }
  .post { background: rgba(20,83,45,0.2); color: #4ade80; border: 1px solid rgba(20,83,45,0.3); }
  .ep-path {
    font-family: 'Courier New', monospace;
    font-size: 13px;
    color: #a78bfa;
    flex: 1;
  }
  .ep-desc { font-size: 12px; color: #475569; }
  .ep-badge {
    font-size: 10px;
    padding: 2px 8px;
    border-radius: 100px;
    font-weight: 600;
  }
  .badge-lock { background: rgba(245,158,11,0.15); color: #fbbf24; border: 1px solid rgba(245,158,11,0.2); }

  /* TECH STACK */
  .tech-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
  }
  .tech-card {
    background: #111118;
    border: 1px solid #1e1e2e;
    border-radius: 14px;
    padding: 18px;
    transition: all 0.2s;
  }
  .tech-card:hover { border-color: #2d2d44; transform: translateY(-2px); }
  .tech-name { font-size: 14px; font-weight: 600; color: #fff; margin-bottom: 4px; display: flex; align-items: center; gap: 8px; }
  .tech-desc { font-size: 12px; color: #475569; line-height: 1.5; }
  .tech-dot { width: 8px; height: 8px; border-radius: 50%; }
  .dot-green { background: #22c55e; box-shadow: 0 0 6px #22c55e; }
  .dot-blue { background: #60a5fa; box-shadow: 0 0 6px #60a5fa; }
  .dot-violet { background: #a78bfa; box-shadow: 0 0 6px #a78bfa; }
  .dot-orange { background: #fb923c; box-shadow: 0 0 6px #fb923c; }
  .dot-red { background: #f87171; box-shadow: 0 0 6px #f87171; }
  .dot-cyan { background: #22d3ee; box-shadow: 0 0 6px #22d3ee; }

  /* GUARANTEES */
  .guarantees {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }
  .guarantee-card {
    background: #111118;
    border: 1px solid #1e1e2e;
    border-radius: 14px;
    padding: 20px;
  }
  .guarantee-title { font-size: 13px; font-weight: 600; color: #fff; margin-bottom: 8px; display: flex; align-items: center; gap: 8px; }
  .guarantee-desc { font-size: 12px; color: #475569; line-height: 1.6; }
  code {
    background: #1a1a2e;
    border: 1px solid #2d2d44;
    border-radius: 4px;
    padding: 1px 6px;
    font-size: 11px;
    color: #a78bfa;
    font-family: 'Courier New', monospace;
  }

  /* FOOTER */
  footer {
    border-top: 1px solid #1e1e2e;
    padding: 24px 40px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    max-width: 900px;
    margin: 0 auto;
  }
  .footer-left { font-size: 12px; color: #334155; }
  .footer-right { display: flex; gap: 16px; }
  .footer-link { font-size: 12px; color: #475569; text-decoration: none; }
  .footer-link:hover { color: #a78bfa; }

  @media (max-width: 640px) {
    .stats { grid-template-columns: 1fr 1fr; }
    .tech-grid { grid-template-columns: 1fr 1fr; }
    .guarantees { grid-template-columns: 1fr; }
    .hero h1 { font-size: 32px; }
    nav { padding: 0 20px; }
    .main { padding: 0 20px 60px; }
    .hero { padding: 48px 20px 40px; }
  }
</style>
</head>
<body>

<nav>
  <div class="nav-brand">
    <div class="nav-icon">⚡</div>
    <div>
      <div class="nav-title">Playto Pay</div>
      <div class="nav-subtitle">Payout Engine API</div>
    </div>
  </div>
  <div class="nav-links">
    <a href="/api/v1/merchants/" class="nav-btn nav-btn-ghost">📡 API</a>
    <a href="/admin/" class="nav-btn nav-btn-ghost">⚙️ Admin</a>
    <a href="http://localhost:5173" class="nav-btn nav-btn-primary">🚀 Dashboard</a>
  </div>
</nav>

<div class="hero">
  <div class="hero-badge">
    <span class="status-dot"></span>
    All systems operational
  </div>
  <h1>Cross-border <span>Payout Engine</span><br>for Indian Merchants</h1>
  <p>Production-grade payment infrastructure. Handles concurrency, idempotency, and ledger integrity so merchants can withdraw international earnings to Indian bank accounts.</p>
  <div class="hero-buttons">
    <a href="http://localhost:5173" class="btn-hero btn-hero-primary">🚀 Open Merchant Dashboard</a>
    <a href="/api/v1/merchants/" class="btn-hero btn-hero-outline">📡 Explore API</a>
  </div>
</div>

<div class="main">

  <!-- STATS -->
  <div class="stats">
    <div class="stat-card">
      <div class="stat-icon">💰</div>
      <div class="stat-label">Money Precision</div>
      <div class="stat-value green">Paise · BigInt</div>
    </div>
    <div class="stat-card">
      <div class="stat-icon">🔒</div>
      <div class="stat-label">Concurrency Guard</div>
      <div class="stat-value violet">SELECT FOR UPDATE</div>
    </div>
    <div class="stat-card">
      <div class="stat-icon">🔑</div>
      <div class="stat-label">Idempotency TTL</div>
      <div class="stat-value blue">24 Hours</div>
    </div>
    <div class="stat-card">
      <div class="stat-icon">⚙️</div>
      <div class="stat-label">Background Jobs</div>
      <div class="stat-value green">Celery + Beat</div>
    </div>
  </div>

  <!-- ENDPOINTS -->
  <div class="section">
    <div class="section-header">
      <div class="section-icon" style="background:rgba(124,58,237,0.15)">📡</div>
      <div>
        <div class="section-title">API Endpoints</div>
        <div class="section-subtitle">Base URL: /api/v1/</div>
      </div>
    </div>
    <div class="endpoints-card">
      <div class="endpoint">
        <span class="method get">GET</span>
        <span class="ep-path">/api/v1/merchants/</span>
        <span class="ep-desc">List all merchants with bank accounts</span>
      </div>
      <div class="endpoint">
        <span class="method get">GET</span>
        <span class="ep-path">/api/v1/merchants/{id}/balance/</span>
        <span class="ep-desc">Total, available and held balance</span>
      </div>
      <div class="endpoint">
        <span class="method get">GET</span>
        <span class="ep-path">/api/v1/merchants/{id}/ledger/</span>
        <span class="ep-desc">Full credit/debit ledger history</span>
      </div>
      <div class="endpoint">
        <span class="method post">POST</span>
        <span class="ep-path">/api/v1/payouts/</span>
        <span class="ep-desc">Create payout request</span>
        <span class="ep-badge badge-lock">🔑 Idempotency-Key</span>
      </div>
      <div class="endpoint">
        <span class="method get">GET</span>
        <span class="ep-path">/api/v1/payouts/list/?merchant_id={id}</span>
        <span class="ep-desc">Payout history with live status</span>
      </div>
    </div>
  </div>

  <!-- GUARANTEES -->
  <div class="section">
    <div class="section-header">
      <div class="section-icon" style="background:rgba(34,197,94,0.15)">🛡️</div>
      <div>
        <div class="section-title">Engineering Guarantees</div>
        <div class="section-subtitle">What makes this production-grade</div>
      </div>
    </div>
    <div class="guarantees">
      <div class="guarantee-card">
        <div class="guarantee-title">💰 Ledger Integrity</div>
        <div class="guarantee-desc">All amounts stored as <code>BigIntegerField</code> in paise. Balance derived from DB-level aggregation — never Python arithmetic on fetched rows. Credits minus debits always equals displayed balance.</div>
      </div>
      <div class="guarantee-card">
        <div class="guarantee-title">🔒 Concurrency Safe</div>
        <div class="guarantee-desc"><code>SELECT FOR UPDATE</code> on Merchant row serializes concurrent requests at PostgreSQL level. Two simultaneous ₹60 requests against ₹100 balance — exactly one succeeds. Proven by test suite.</div>
      </div>
      <div class="guarantee-card">
        <div class="guarantee-title">🔑 Idempotent API</div>
        <div class="guarantee-desc">Merchant-scoped <code>Idempotency-Key</code> header with 24h TTL. Second call with same key returns identical response. No duplicate payout created. Safe to retry on network failure.</div>
      </div>
      <div class="guarantee-card">
        <div class="guarantee-title">⚙️ State Machine</div>
        <div class="guarantee-desc">Legal: <code>PENDING→PROCESSING→COMPLETED/FAILED</code>. Illegal transitions (e.g. <code>COMPLETED→PENDING</code>) raise <code>InvalidTransitionError</code>. Failed payout refunds funds atomically.</div>
      </div>
    </div>
  </div>

  <!-- TECH STACK -->
  <div class="section">
    <div class="section-header">
      <div class="section-icon" style="background:rgba(96,165,250,0.15)">🛠️</div>
      <div>
        <div class="section-title">Tech Stack</div>
        <div class="section-subtitle">Every component running in production mode</div>
      </div>
    </div>
    <div class="tech-grid">
      <div class="tech-card">
        <div class="tech-name"><span class="tech-dot dot-green"></span>Django 4.2 + DRF</div>
        <div class="tech-desc">REST API with atomic transactions and row-level locking via PostgreSQL</div>
      </div>
      <div class="tech-card">
        <div class="tech-name"><span class="tech-dot dot-blue"></span>PostgreSQL</div>
        <div class="tech-desc">SELECT FOR UPDATE prevents concurrent overdraw. BigIntegerField for paise precision</div>
      </div>
      <div class="tech-card">
        <div class="tech-name"><span class="tech-dot dot-orange"></span>Celery + Redis</div>
        <div class="tech-desc">Async payout processing with exponential backoff retry and beat scheduler</div>
      </div>
      <div class="tech-card">
        <div class="tech-name"><span class="tech-dot dot-violet"></span>React + Vite</div>
        <div class="tech-desc">Merchant dashboard with live status polling every 4 seconds</div>
      </div>
      <div class="tech-card">
        <div class="tech-name"><span class="tech-dot dot-cyan"></span>Tailwind CSS</div>
        <div class="tech-desc">Dark-mode UI with real-time balance cards and payout history table</div>
      </div>
      <div class="tech-card">
        <div class="tech-name"><span class="tech-dot dot-red"></span>Docker Compose</div>
        <div class="tech-desc">One-command setup: db + redis + backend + celery + frontend</div>
      </div>
    </div>
  </div>

</div>

<footer>
  <div class="footer-left">Built for Playto Founding Engineer Challenge 2026 · Cross-border payout infrastructure</div>
  <div class="footer-right">
    <a href="/admin/" class="footer-link">Admin Panel</a>
    <a href="/api/v1/merchants/" class="footer-link">Merchants API</a>
    <a href="http://localhost:5173" class="footer-link">Dashboard</a>
  </div>
</footer>

</body>
</html>
"""
    return HttpResponse(html)


urlpatterns = [
    path('', api_home),
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.merchants.urls')),
    path('api/v1/', include('apps.payouts.urls')),
]