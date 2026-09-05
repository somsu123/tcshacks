"use client";

import Link from "next/link";
import { ChevronRight } from "lucide-react";
import { Transaction } from "@/lib/types";
import { formatAmount, formatTimestamp, riskColors } from "@/lib/utils";
import { RiskDot } from "../ui/badge";

interface TransactionRowProps {
  transaction: Transaction;
  index: number;
}

export function TransactionRow({ transaction }: TransactionRowProps) {
  const colors = riskColors[transaction.risk_level];

  return (
    <Link href={`/transactions/${transaction.id}`}>
      <div className="group flex items-center gap-4 p-4 rounded-lg border bg-[var(--card)] cursor-pointer hover:-translate-y-0.5 hover:shadow-lg transition-all duration-200">
          {/* Risk indicator */}
          <div className="flex-shrink-0">
            <RiskDot level={transaction.risk_level} />
          </div>

          {/* Amount */}
          <div className="w-28 flex-shrink-0">
            <span className="font-semibold tabular-nums">
              {formatAmount(transaction.amount)}
            </span>
          </div>

          {/* Payee */}
          <div className="flex-1 min-w-0">
            <p className="font-medium truncate">{transaction.payee}</p>
            <p className="text-sm text-zinc-500 dark:text-zinc-400 truncate">
              {transaction.reference}
            </p>
          </div>

          {/* Timestamp */}
          <div className="hidden sm:block w-32 text-sm text-zinc-500 dark:text-zinc-400">
            {formatTimestamp(transaction.timestamp)}
          </div>

          {/* Risk score as confidence */}
          <div className="hidden md:flex items-center gap-2 w-20">
            <div className="flex-1 h-1.5 bg-zinc-200 dark:bg-zinc-700 rounded-full overflow-hidden">
              <div
                className={`h-full ${colors.bg} transition-all duration-500`}
                style={{ width: `${transaction.risk_score * 100}%` }}
              />
            </div>
            <span className="text-xs text-zinc-500 tabular-nums">
              {Math.round(transaction.risk_score * 100)}%
            </span>
          </div>

          {/* Chevron */}
          <ChevronRight className="h-5 w-5 text-zinc-400 group-hover:text-zinc-600 dark:group-hover:text-zinc-300 transition-colors" />
        </div>
    </Link>
  );
}
