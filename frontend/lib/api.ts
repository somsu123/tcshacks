import { PaginatedResponse, TransactionDetail } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function getTransactions(
  page = 1,
  pageSize = 100
): Promise<PaginatedResponse> {
  const res = await fetch(
    `${API_BASE}/transactions?page=${page}&page_size=${pageSize}`,
    {
      cache: "no-store",
    }
  );

  if (!res.ok) {
    throw new Error("Failed to fetch transactions");
  }

  return res.json();
}

export async function getTransaction(id: string): Promise<TransactionDetail> {
  const res = await fetch(`${API_BASE}/transactions/${id}`, {
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error("Failed to fetch transaction");
  }

  return res.json();
}

// Fetcher for SWR
export const fetcher = async (url: string) => {
  const res = await fetch(`${API_BASE}${url}`);
  if (!res.ok) throw new Error("Failed to fetch");
  return res.json();
};

export async function holdTransaction(id: string) {
  const res = await fetch(`${API_BASE}/transactions/${id}/hold`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to hold transaction');
  return res.json();
}

export async function fetchAccountTimeline(accountId: string, page = 1, pageSize = 50) {
  const res = await fetch(`${API_BASE}/accounts/${accountId}/transactions?page=${page}&page_size=${pageSize}`);
  if (!res.ok) throw new Error('Failed to fetch account timeline');
  return res.json();
}

export async function fetchRiskThresholds() {
  const res = await fetch(`${API_BASE}/config/risk-thresholds`);
  if (!res.ok) throw new Error('Failed to fetch risk thresholds');
  return res.json();
}

export async function saveRiskThresholds(thresholds: { high: number; medium: number }) {
  const res = await fetch(`${API_BASE}/config/risk-thresholds`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(thresholds),
  });
  if (!res.ok) throw new Error('Failed to save risk thresholds');
  return res.json();
}

export async function loadSampleData() {
  const res = await fetch(`${API_BASE}/transactions/load-sample`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to load sample data');
  return res.json();
}
