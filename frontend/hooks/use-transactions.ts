"use client";

import useSWR from "swr";
import { fetcher } from "@/lib/api";
import { PaginatedResponse, Transaction } from "@/lib/types";

export function useTransactions() {
  const { data, error, isLoading, mutate } = useSWR<PaginatedResponse>(
    "/transactions?page=1&page_size=100",
    fetcher,
    {
      refreshInterval: 30000, // Refresh every 30 seconds
      revalidateOnFocus: true,
    }
  );

  // Sort transactions by risk level (high first)
  const sortedTransactions = [...(data?.items ?? [])].sort((a, b) => {
    const riskOrder = { high: 0, medium: 1, low: 2 };
    return riskOrder[a.risk_level] - riskOrder[b.risk_level];
  });

  // Calculate stats
  const stats = {
    total: data?.total ?? 0,
    high: data?.items?.filter((t) => t.risk_level === "high").length ?? 0,
    medium: data?.items?.filter((t) => t.risk_level === "medium").length ?? 0,
    low: data?.items?.filter((t) => t.risk_level === "low").length ?? 0,
  };

  return {
    transactions: sortedTransactions,
    stats,
    isLoading,
    isError: !!error,
    error,
    mutate,
  };
}
