import axios from 'axios';

const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
});

export const getMerchants = () => API.get('/merchants/');
export const getBalance = (id) => API.get(`/merchants/${id}/balance/`);
export const getLedger = (id) => API.get(`/merchants/${id}/ledger/`);
export const getPayouts = (id) => API.get(`/payouts/list/?merchant_id=${id}`);
export const createPayout = (data, idempotencyKey) =>
  API.post('/payouts/', data, { headers: { 'Idempotency-Key': idempotencyKey } });