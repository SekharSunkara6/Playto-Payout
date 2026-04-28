const colors = {
  PENDING:    'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
  PROCESSING: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
  COMPLETED:  'bg-green-500/20 text-green-300 border-green-500/30',
  FAILED:     'bg-red-500/20 text-red-300 border-red-500/30',
};
export default function StatusBadge({ status }) {
  return (
    <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border ${colors[status] || 'bg-gray-500/20 text-gray-300'}`}>
      {status}
    </span>
  );
}