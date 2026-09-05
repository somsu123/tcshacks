"use client";

import Link from "next/link";
import { Plus } from "lucide-react";
import { useState } from "react";
import { useTransactions } from "@/hooks/use-transactions";
import { StatsRow } from "@/components/dashboard/stats-row";
import { DashboardFilters } from "@/components/dashboard/filters";
import { TransactionTable } from "@/components/dashboard/transaction-table";
import { StatsSkeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { RiskLevel } from "@/lib/types";
import { formatAmount } from "@/lib/utils";
import { loadSampleData } from "@/lib/api";

export default function DashboardPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [riskLevel, setRiskLevel] = useState<RiskLevel | "all">("all");
  const [statusFilter, setStatusFilter] = useState<string | "all">("all");
  const [isSampleLoading, setIsSampleLoading] = useState(false);

  const { transactions: allTransactions, isLoading, isError, mutate } = useTransactions();

  const handleLoadSample = async () => {
    setIsSampleLoading(true);
    try {
      await loadSampleData();
      await mutate();
    } catch (error) {
      console.error("Failed to load sample data:", error);
    } finally {
      setIsSampleLoading(false);
    }
  };

  // Client-side filtering
  const transactions = allTransactions.filter((t) => {
    const matchesSearch = 
      t.payee.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.reference.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesRisk = riskLevel === "all" || t.risk_level === riskLevel;
    const matchesStatus = statusFilter === "all" || t.status === statusFilter;
    return matchesSearch && matchesRisk && matchesStatus;
  });

  // Calculate stats from filtered transactions
  const stats = {
    total: transactions.length,
    high: transactions.filter((t) => t.risk_level === "high").length,
    medium: transactions.filter((t) => t.risk_level === "medium").length,
    low: transactions.filter((t) => t.risk_level === "low").length,
    atRisk: transactions
      .filter((t) => t.risk_level === "high")
      .reduce((sum, t) => sum + t.amount, 0),
  };

  // Calculate fraud rate
  const fraudRate =
    stats.total > 0 ? Math.round((stats.high / stats.total) * 100) : 0;

  return (
    <div className="space-y-8">
      {/* Filters */}
      <DashboardFilters
        searchQuery={searchQuery}
        riskLevel={riskLevel}
        statusFilter={statusFilter}
        onSearchChange={setSearchQuery}
        onRiskLevelChange={setRiskLevel}
        onStatusChange={setStatusFilter}
      />

      {/* Financial Summary */}
      {!isLoading && (
        <Card>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            {/* Amount at Risk */}
            <div className="space-y-2">
              <p className="text-sm font-medium text-zinc-600 dark:text-zinc-400">
                Amount at Risk
              </p>
              <p className="text-2xl font-bold text-red-600 dark:text-red-400">
                {formatAmount(stats.atRisk)}
              </p>
              <p className="text-xs text-zinc-500 dark:text-zinc-500">
                High-risk transactions
              </p>
            </div>

            {/* Fraud Rate */}
            <div className="space-y-2">
              <p className="text-sm font-medium text-zinc-600 dark:text-zinc-400">
                Fraud Rate
              </p>
              <p className="text-2xl font-bold text-amber-600 dark:text-amber-400">
                {fraudRate}%
              </p>
              <p className="text-xs text-zinc-500 dark:text-zinc-500">
                {stats.high} of {stats.total} transactions
              </p>
            </div>

            {/* Transaction Count */}
            <div className="space-y-2">
              <p className="text-sm font-medium text-zinc-600 dark:text-zinc-400">
                Total Transactions
              </p>
              <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                {stats.total}
              </p>
              <p className="text-xs text-zinc-500 dark:text-zinc-500">
                in current view
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* Stats Row */}
      {isLoading ? (
        <StatsSkeleton />
      ) : (
        <StatsRow
          total={stats.total}
          high={stats.high}
          medium={stats.medium}
          low={stats.low}
        />
      )}

      {/* Transaction Table */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Transactions</h2>
          <div className="flex gap-2">
            <Link href="/transactions/upload">
              <Button variant="ghost" className="gap-2">
                <Plus className="h-4 w-4" />
                Import CSV
              </Button>
            </Link>
            <Link href="/transactions/new">
              <Button className="gap-2">
                <Plus className="h-4 w-4" />
                Add Transaction
              </Button>
            </Link>
          </div>
        </div>
        <TransactionTable
          transactions={transactions}
          isLoading={isLoading || isSampleLoading}
          isError={isError}
          totalCount={allTransactions.length}
          onLoadSample={handleLoadSample}
        />
      </section>
    </div>
  );
}
