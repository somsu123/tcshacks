"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Clock, MapPin, Building, CreditCard } from "lucide-react";
import { fetchAccountTimeline } from "@/lib/api";
import { Transaction } from "@/lib/types";
import { formatAmount, formatFullTimestamp } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { RiskBadge } from "@/components/detail/risk-badge";
import { DetailSkeleton } from "@/components/ui/skeleton";

export default function AccountTimelinePage() {
  const params = useParams();
  const accountId = params.account_id as string;
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isError, setIsError] = useState(false);

  useEffect(() => {
    async function loadTimeline() {
      try {
        const data = await fetchAccountTimeline(accountId, 1, 50);
        setTransactions(data.items || []);
      } catch (err) {
        setIsError(true);
      } finally {
        setIsLoading(false);
      }
    }
    loadTimeline();
  }, [accountId]);

  if (isLoading) {
    return <DetailSkeleton />;
  }

  if (isError) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-semibold mb-2">Failed to load timeline</h2>
        <Link href="/">
          <Button>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Dashboard
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      <Link href="/">
        <Button variant="ghost" className="gap-2">
          <ArrowLeft className="h-4 w-4" />
          Back to Dashboard
        </Button>
      </Link>

      <Card>
        <div className="space-y-2">
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Building className="h-6 w-6 text-zinc-400" />
            Account Timeline
          </h1>
          <p className="text-zinc-500 dark:text-zinc-400 font-mono">
            {accountId}
          </p>
        </div>
      </Card>

      <div className="relative border-l-2 border-zinc-200 dark:border-zinc-800 ml-4 pl-8 space-y-8 py-4">
        {transactions.map((tx) => (
          <div key={tx.id} className="relative">
            <div className="absolute -left-[41px] top-1 h-6 w-6 rounded-full bg-white dark:bg-zinc-950 border-2 border-zinc-300 dark:border-zinc-700 flex items-center justify-center">
              <div className="h-2 w-2 rounded-full bg-zinc-400 dark:bg-zinc-500" />
            </div>
            
            <Card className="hover:border-blue-500/50 transition-colors">
              <Link href={`/transactions/${tx.id}`} className="block p-1">
                <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                  <div className="space-y-1">
                    <h3 className="font-semibold text-lg flex items-center gap-2">
                      {tx.payee}
                    </h3>
                    <div className="flex items-center gap-4 text-sm text-zinc-500 dark:text-zinc-400">
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {formatFullTimestamp(tx.timestamp)}
                      </span>
                      {tx.location_country && (
                        <span className="flex items-center gap-1">
                          <MapPin className="h-3 w-3" />
                          {tx.location_country}
                        </span>
                      )}
                      <span className="flex items-center gap-1">
                        <CreditCard className="h-3 w-3" />
                        {tx.reference}
                      </span>
                    </div>
                  </div>
                  
                  <div className="flex flex-col items-end gap-2">
                    <span className="text-lg font-bold tabular-nums">
                      {formatAmount(tx.amount)}
                    </span>
                    <div className="flex items-center gap-2">
                      <span className="text-xs px-2 py-1 bg-zinc-100 dark:bg-zinc-800 rounded-md font-medium uppercase tracking-wide text-zinc-600 dark:text-zinc-300">
                        {tx.status}
                      </span>
                      <RiskBadge level={tx.risk_level} />
                    </div>
                  </div>
                </div>
              </Link>
            </Card>
          </div>
        ))}

        {transactions.length === 0 && (
          <p className="text-zinc-500">No transactions found for this account.</p>
        )}
      </div>
    </div>
  );
}
