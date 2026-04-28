import { useState, useEffect } from 'react';
import { Send, AlertCircle, CheckCircle2 } from 'lucide-react';
import { createPayout } from '../api/client';

function uuid() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = Math.random() * 16 | 0;
    return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
  });
}

export default function PayoutForm({ merchant, bankAccounts, onSuccess }) {
  const [amount, setAmount] = useState('');
  const [bankId, setBankId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Reset everything when merchant changes
  useEffect(() => {
    setAmount('');
    setError('');
    setSuccess('');
    // Set bank to this merchant's first bank account
    if (bankAccounts && bankAccounts.length > 0) {
      setBankId(bankAccounts[0].id);
    } else {
      setBankId('');
    }
  }, [merchant.id, bankAccounts]);

  const handleSubmit = async () => {
    setError('');
    setSuccess('');

    if (!bankId) {
      setError('No bank account found for this merchant');
      return;
    }

    const paise = Math.round(parseFloat(amount) * 100);
    if (!amount || isNaN(paise) || paise <= 0) {
      setError('Enter a valid amount in rupees');
      return;
    }

    setLoading(true);
    try {
      const resp = await createPayout(
        {
          merchant_id: merchant.id,
          amount_paise: paise,
          bank_account_id: bankId,
        },
        uuid()
      );
      setSuccess(`Payout of ₹${amount} initiated! ID: ${resp.data.id.slice(0, 8)}…`);
      setAmount('');
      setTimeout(onSuccess, 1500);
    } catch (e) {
      setError(e.response?.data?.error || 'Request failed. Check your balance.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-900/60 border border-slate-700/50 rounded-2xl p-6 mb-6">
      <h3 className="text-lg font-semibold text-white mb-5 flex items-center gap-2">
        <Send size={18} className="text-violet-400" /> Request Payout
      </h3>
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <span className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 font-semibold text-sm">₹</span>
          <input
            type="number"
            value={amount}
            onChange={e => setAmount(e.target.value)}
            placeholder="0.00"
            min="0"
            step="0.01"
            onKeyDown={e => e.key === 'Enter' && handleSubmit()}
            className="w-full bg-slate-800 border border-slate-600 rounded-xl pl-8 pr-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500/30 transition text-sm"
          />
        </div>
        <select
          value={bankId}
          onChange={e => setBankId(e.target.value)}
          className="bg-slate-800 border border-slate-600 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-violet-500 transition text-sm min-w-[180px]">
          {bankAccounts.map(b => (
            <option key={b.id} value={b.id}>
              ···{b.account_number.slice(-4)} | {b.ifsc_code}
            </option>
          ))}
        </select>
        <button
          onClick={handleSubmit}
          disabled={loading}
          className="bg-violet-600 hover:bg-violet-500 active:bg-violet-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold px-6 py-3 rounded-xl transition-all flex items-center gap-2 whitespace-nowrap text-sm">
          {loading
            ? <><span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /><span>Sending…</span></>
            : <><Send size={15} /><span>Send Payout</span></>}
        </button>
      </div>
      {error && (
        <p className="mt-3 text-red-400 text-sm flex items-center gap-2">
          <AlertCircle size={14} />{error}
        </p>
      )}
      {success && (
        <p className="mt-3 text-emerald-400 text-sm flex items-center gap-2">
          <CheckCircle2 size={14} />{success}
        </p>
      )}
    </div>
  );
}