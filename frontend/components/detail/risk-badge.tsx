"use client";

import { RiskLevel } from "@/lib/types";
import { riskColors, riskEmoji } from "@/lib/utils";

interface RiskBadgeProps {
  level: RiskLevel;
  className?: string;
}

export function RiskBadge({ level, className }: RiskBadgeProps) {
  const colors = riskColors[level];

  return (
    <div className={`inline-flex flex-col items-center justify-center p-6 rounded-2xl ${colors.bg} text-white ${className}`}>
      <span className="text-4xl mb-2">
        {riskEmoji[level]}
      </span>
      <span className="text-2xl font-bold uppercase tracking-wider">
        {level}
      </span>
      <span className="text-sm opacity-80">RISK</span>
    </div>
  );
}
