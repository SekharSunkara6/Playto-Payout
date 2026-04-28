import { Wallet, Lock, TrendingUp } from 'lucide-react';

function fmt(paise) {
  return '₹' + (paise / 100).toLocaleString('en-IN', { minimumFractionDigits: 2 });
}

export default function BalanceCard({ balance }) {
  if (!balance) return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
      {[1,2,3].map(i => <div key={i} className="bg-slate-900/60 border border-slate-700/50 rounded-2xl p-6 animate-pulse h-32"/>)}
    </div>
  );
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
      <div className="bg-gradient-to-br from-violet-600/20 to-violet-900/10 border border-violet-500/20 rounded-2xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-violet-500/20 rounded-xl"><TrendingUp size={20} className="text-violet-400"/></div>
          <span className="text-sm text-slate-400 font-medium">Total Balance</span>
        </div>
        <p className="text-3xl font-bold text-white">{fmt(balance.total_balance_paise)}</p>
        <p className="text-xs text-slate-500 mt-1">All credits minus debits</p>
      </div>
      <div className="bg-gradient-to-br from-emerald-600/20 to-emerald-900/10 border border-emerald-500/20 rounded-2xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-emerald-500/20 rounded-xl"><Wallet size={20} className="text-emerald-400"/></div>
          <span className="text-sm text-slate-400 font-medium">Available</span>
        </div>
        <p className="text-3xl font-bold text-emerald-400">{fmt(balance.available_balance_paise)}</p>
        <p className="text-xs text-slate-500 mt-1">Ready to withdraw</p>
      </div>
      <div className="bg-gradient-to-br from-amber-600/20 to-amber-900/10 border border-amber-500/20 rounded-2xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-amber-500/20 rounded-xl"><Lock size={20} className="text-amber-400"/></div>
          <span className="text-sm text-slate-400 font-medium">Held</span>
        </div>
        <p className="text-3xl font-bold text-amber-400">{fmt(balance.held_balance_paise)}</p>
        <p className="text-xs text-slate-500 mt-1">Pending / processing</p>
      </div>
    </div>
  );
}