import { useState, useEffect, useCallback } from 'react';
import { getMerchants, getBalance, getLedger, getPayouts } from '../api/client';
import BalanceCard from './BalanceCard';
import PayoutForm from './PayoutForm';
import PayoutTable from './PayoutTable';
import LedgerTable from './LedgerTable';
import { RefreshCw, ChevronDown, Zap } from 'lucide-react';

export default function Dashboard() {
  const [merchants, setMerchants] = useState([]);
  const [selected, setSelected] = useState(null);
  const [balance, setBalance] = useState(null);
  const [ledger, setLedger] = useState([]);
  const [payouts, setPayouts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);

  useEffect(() => {
    getMerchants().then(r => {
      setMerchants(r.data);
      if (r.data.length) setSelected(r.data[0]);
    });
  }, []);

  const refresh = useCallback(async () => {
    if (!selected) return;
    setLoading(true);
    try {
      const [b, l, p] = await Promise.all([
        getBalance(selected.id),
        getLedger(selected.id),
        getPayouts(selected.id),
      ]);
      setBalance(b.data);
      setLedger(l.data);
      setPayouts(p.data);
      setLastUpdated(new Date());
    } catch(e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [selected]);

  useEffect(() => { refresh(); }, [refresh]);

  // Live updates every 4 seconds
  useEffect(() => {
    const t = setInterval(refresh, 4000);
    return () => clearInterval(t);
  }, [refresh]);

  return (
    <div className="min-h-screen bg-[#0f0f13]">
      {/* Header */}
      <div className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-md sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-gradient-to-br from-violet-500 to-violet-700 rounded-xl flex items-center justify-center shadow-lg shadow-violet-500/20">
              <Zap size={18} className="text-white"/>
            </div>
            <div>
              <span className="text-white font-bold text-lg leading-none">Playto Pay</span>
              <p className="text-slate-500 text-xs mt-0.5">Payout Engine</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {lastUpdated && (
              <span className="text-slate-600 text-xs hidden sm:block">
                Updated {lastUpdated.toLocaleTimeString('en-IN')}
              </span>
            )}
            <div className="relative">
              <select
                value={selected?.id || ''}
                onChange={e => setSelected(merchants.find(m => m.id == e.target.value))}
                className="bg-slate-800 border border-slate-700 rounded-xl pl-4 pr-9 py-2 text-white text-sm appearance-none focus:outline-none focus:border-violet-500 cursor-pointer transition">
                {merchants.map(m => <option key={m.id} value={m.id}>{m.name}</option>)}
              </select>
              <ChevronDown size={13} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none"/>
            </div>
            <button onClick={refresh}
              className="p-2.5 hover:bg-slate-800 rounded-xl transition text-slate-400 hover:text-white border border-transparent hover:border-slate-700">
              <RefreshCw size={15} className={loading ? 'animate-spin' : ''}/>
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-6xl mx-auto px-6 py-8">
        {selected ? (
          <>
            <div className="mb-7">
              <h2 className="text-2xl font-bold text-white">{selected.name}</h2>
              <p className="text-slate-500 text-sm mt-1">{selected.email}</p>
            </div>
            <BalanceCard balance={balance}/>
            <PayoutForm
              merchant={selected}
              bankAccounts={selected.bank_accounts || []}
              onSuccess={refresh}
            />
            <PayoutTable payouts={payouts} loading={loading}/>
            <LedgerTable entries={ledger}/>
          </>
        ) : (
          <div className="flex items-center justify-center h-64">
            <div className="w-8 h-8 border-2 border-violet-500/30 border-t-violet-500 rounded-full animate-spin"/>
          </div>
        )}
      </div>
    </div>
  );
}