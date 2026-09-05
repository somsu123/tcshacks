"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Shield } from "lucide-react";
import { useTransaction } from "@/hooks/use-transaction";
import { formatAmount, formatFullTimestamp } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { DetailSkeleton } from "@/components/ui/skeleton";
import { RiskBadge } from "@/components/detail/risk-badge";
import { ConfidenceMeter } from "@/components/detail/confidence-meter";
import { FactorCard, NoFactors } from "@/components/detail/factor-card";
import { ActionButtons } from "@/components/detail/action-buttons";
import { AuditTrail } from "@/components/detail/audit-trail";


export default function TransactionDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const { transaction, isLoading, isError } = useTransaction(id);

  if (isLoading) {
    return <DetailSkeleton />;
  }

  if (isError || !transaction) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-semibold mb-2">Transaction Not Found</h2>
        <p className="text-zinc-500 dark:text-zinc-400 mb-4">
          The transaction you&apos;re looking for doesn&apos;t exist.
        </p>
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
      {/* Back Button */}
      <Link href="/">
        <Button variant="ghost" className="gap-2">
          <ArrowLeft className="h-4 w-4" />
          Back to Dashboard
        </Button>
      </Link>

      {/* Transaction Header */}
      <Card>
        <div className="space-y-4">
          <div className="flex justify-between items-start">
            <h1 className="text-2xl font-bold">{transaction.payee}</h1>
            <Link href={`/accounts/${transaction.account_id}/timeline`}>
              <Button variant="outline" size="sm" className="gap-2">
                View Account Timeline →
              </Button>
            </Link>
          </div>
          <div className="flex flex-wrap items-center gap-4 text-zinc-500 dark:text-zinc-400">
            <span className="text-xl font-semibold text-[var(--foreground)] tabular-nums">
              {formatAmount(transaction.amount)}
            </span>
            <span>•</span>
            <span>{formatFullTimestamp(transaction.timestamp)}</span>
            <span>•</span>
            <span>{transaction.reference}</span>
            <span>•</span>
            <span>Acc: {transaction.account_id}</span>
            {transaction.location_country && (
              <>
                <span>•</span>
                <span>🌍 {transaction.location_country}</span>
              </>
            )}
          </div>
        </div>
      </Card>

      {/* Risk Assessment */}
      <div className="grid md:grid-cols-2 gap-6">
        <RiskBadge level={transaction.risk_level} className="h-full" />
        <ConfidenceMeter
          confidence={transaction.confidence}
          level={transaction.risk_level}
        />
      </div>

      {/* Risk Factors */}
      <section>
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Shield className="h-5 w-5 text-zinc-500" />
          Why This Was Flagged
        </h2>
        <div className="space-y-3">
          {transaction.risk_factors.length > 0 ? (
            transaction.risk_factors.map((factor, index) => (
              <FactorCard key={index} factor={factor} />
            ))
          ) : (
            <NoFactors />
          )}
        </div>
      </section>

      {/* Recommended Action */}
      <section>
        <h2 className="text-lg font-semibold mb-4">Recommended Action</h2>
        <div className="p-4 rounded-xl border-2 border-accent/20 bg-accent/5">
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-accent/10 flex items-center justify-center">
              <Shield className="h-4 w-4 text-accent" />
            </div>
            <p className="text-lg">{transaction.recommended_action}</p>
          </div>
        </div>
      </section>

      {/* Action Buttons */}
      <section>
        <h2 className="text-lg font-semibold mb-4">Take Action</h2>
        <ActionButtons transactionId={transaction.id} riskLevel={transaction.risk_level} status={transaction.status} />
      </section>

      {/* Audit Trail */}
      <section>
        <AuditTrail transactionId={transaction.id} />
      </section>    </div>
  );
}