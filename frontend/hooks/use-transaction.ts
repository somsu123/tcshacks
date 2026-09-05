"use client";

import useSWR from "swr";
import { fetcher } from "@/lib/api";
import { TransactionDetail } from "@/lib/types";

export function useTransaction(id: string) {
  const { data, error, isLoading } = useSWR<TransactionDetail>(
    id ? `/transactions/${id}` : null,
    fetcher
  );

  return {
    transaction: data,
    isLoading,
    isError: !!error,
    error,
  };
}
