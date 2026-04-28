import { ArrowDownLeft, ArrowUpRight } from 'lucide-react';

export default function LedgerTable({ entries }) {
  return (
    <div className="bg-slate-900/60 border border-slate-700/50 rounded-2xl p-6">
      <h3 className="text-lg font-semibold text-white mb-5">Ledger Entries</h3>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-slate-500 text-xs uppercase tracking-wide border-b border-slate-800">
              <th className="text-left pb-3 pr-4 font-medium">Type</th>
              <th className="text-left pb-3 pr-4 font-medium">Amount</th>
              <th className="text-left pb-3 pr-4 font-medium">Description</th>
              <th className="text-left pb-3 font-medium">Date</th>
            </tr>
          </thead>
          <tbody>
            {entries.map(e => (
              <tr key={e.id} className="border-b border-slate-800/60 hover:bg-slate-800/30 transition">
                <td className="py-3.5 pr-4">
                  {e.entry_type === 'CREDIT'
                    ? <span className="flex items-center gap-1.5 text-emerald-400 font-medium"><ArrowDownLeft size={13}/>Credit</span>
                    : <span className="flex items-center gap-1.5 text-red-400 font-medium"><ArrowUpRight size={13}/>Debit</span>}
                </td>
                <td className={`py-3.5 pr-4 font-semibold ${e.entry_type === 'CREDIT' ? 'text-emerald-400' : 'text-red-400'}`}>
                  {e.entry_type === 'CREDIT' ? '+' : '-'}₹{(e.amount_paise/100).toLocaleString('en-IN', {minimumFractionDigits:2})}
                </td>
                <td className="py-3.5 pr-4 text-slate-300">{e.description}</td>
                <td className="py-3.5 text-slate-500 text-xs">{new Date(e.created_at).toLocaleString('en-IN')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}