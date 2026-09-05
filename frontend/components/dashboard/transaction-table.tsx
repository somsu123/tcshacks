"use client";

import { Transaction } from "@/lib/types";
import { TransactionRow } from "./transaction-row";
import { TableSkeleton } from "../ui/skeleton";
import { AlertCircle } from "lucide-react";

interface TransactionTableProps {
  transactions: Transaction[];
  isLoading: boolean;
  isError: boolean;
  totalCount?: number;
  onLoadSample?: () => void;
}

export function TransactionTable({
  transactions,
  isLoading,
  isError,
  totalCount = 0,
  onLoadSample,
}: TransactionTableProps) {
  if (isLoading) {
    return (
      <div className="rounded-xl border bg-[var(--card)] p-4">
        <TableSkeleton rows={8} />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="rounded-xl border bg-[var(--card)] p-8 text-center">
        <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <h3 className="text-lg font-semibold mb-2">Connection Error</h3>
        <p className="text-zinc-500 dark:text-zinc-400 mb-4">
          Cannot connect to FraudShield API. Is the backend running?
        </p>
        <code className="block bg-zinc-100 dark:bg-zinc-800 rounded-lg p-3 text-sm">
          uvicorn app.main:app --port 8000
        </code>
      </div>
    );
  }

  if (transactions.length === 0 && !isLoading && !isError) {
    // Distinguish between "no data at all" and "no matches for filter"
    return (
      <div className="rounded-xl border bg-[var(--card)] p-8 text-center space-y-4">
        <div className="text-4xl">📊</div>
        <h3 className="text-lg font-semibold">No transactions found</h3>
        <p className="text-zinc-500 dark:text-zinc-400">
          {totalCount === 0
            ? "Get started by loading the sample dataset or uploading your own transactions."
            : "No anomalies detected — all transactions appear normal for the current filters."}
        </p>
        {totalCount === 0 && onLoadSample && (
          <button
            onClick={onLoadSample}
            className="px-4 py-2 bg-[var(--accent)] text-white rounded-lg hover:opacity-90 transition-opacity"
          >
            Load Sample Dataset
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {/* Header */}
      <div className="hidden md:flex items-center gap-4 px-4 text-sm font-medium text-zinc-500 dark:text-zinc-400">
        <div className="w-6">Risk</div>
        <div className="w-28">Amount</div>
        <div className="flex-1">Payee</div>
        <div className="w-32">Time</div>
        <div className="w-20">Score</div>
        <div className="w-5"></div>
      </div>

      {/* Rows */}
      <div className="space-y-2">
        {transactions.map((transaction, index) => (
          <TransactionRow
            key={transaction.id}
            transaction={transaction}
            index={index}
          />
        ))}
      </div>
    </div>
  );
}
