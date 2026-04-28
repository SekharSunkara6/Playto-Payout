import StatusBadge from './StatusBadge';
import { ArrowDownRight, RefreshCw } from 'lucide-react';

export default function PayoutTable({ payouts, loading }) {
  return (
    <div className="bg-slate-900/60 border border-slate-700/50 rounded-2xl p-6 mb-6">
      <div className="flex items-center justify-between mb-5">
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          <ArrowDownRight size={18} className="text-emerald-400"/> Payout History
        </h3>
        {loading && <RefreshCw size={14} className="text-slate-500 animate-spin"/>}
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-slate-500 text-xs uppercase tracking-wide border-b border-slate-800">
              <th className="text-left pb-3 pr-4 font-medium">ID</th>
              <th className="text-left pb-3 pr-4 font-medium">Amount</th>
              <th className="text-left pb-3 pr-4 font-medium">Status</th>
              <th className="text-left pb-3 pr-4 font-medium">Bank</th>
              <th className="text-left pb-3 pr-4 font-medium">Attempts</th>
              <th className="text-left pb-3 font-medium">Date</th>
            </tr>
          </thead>
          <tbody>
            {payouts.length === 0 && (
              <tr><td colSpan={6} className="py-10 text-center text-slate-500 text-sm">No payouts yet — request one above</td></tr>
            )}
            {payouts.map(p => (
              <tr key={p.id} className="border-b border-slate-800/60 hover:bg-slate-800/30 transition group">
                <td className="py-3.5 pr-4 font-mono text-xs text-slate-400 group-hover:text-slate-300">{p.id.slice(0,8)}…</td>
                <td className="py-3.5 pr-4 text-white font-semibold">
                  ₹{(p.amount_paise/100).toLocaleString('en-IN', {minimumFractionDigits:2})}
                </td>
                <td className="py-3.5 pr-4"><StatusBadge status={p.status}/></td>
                <td className="py-3.5 pr-4 text-slate-400 font-mono text-xs">···{p.bank_account_last4}</td>
                <td className="py-3.5 pr-4 text-slate-400 text-center">{p.attempt_count}</td>
                <td className="py-3.5 text-slate-500 text-xs">{new Date(p.created_at).toLocaleString('en-IN')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}