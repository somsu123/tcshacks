"use client";

import { cn, riskColors, riskEmoji } from "@/lib/utils";
import { RiskLevel } from "@/lib/types";

interface BadgeProps {
  level: RiskLevel;
  size?: "sm" | "md" | "lg";
  showEmoji?: boolean;
  className?: string;
}

export function Badge({
  level,
  size = "md",
  showEmoji = true,
  className,
}: BadgeProps) {
  const colors = riskColors[level];

  const sizeClasses = {
    sm: "px-2 py-0.5 text-xs",
    md: "px-2.5 py-1 text-sm",
    lg: "px-4 py-2 text-base",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 font-medium rounded-full",
        colors.bgLight,
        colors.text,
        sizeClasses[size],
        className
      )}
    >
      {showEmoji && <span>{riskEmoji[level]}</span>}
      <span className="capitalize">{level}</span>
    </span>
  );
}

export function RiskDot({ level }: { level: RiskLevel }) {
  return (
    <span className="text-lg" aria-label={`${level} risk`}>
      {riskEmoji[level]}
    </span>
  );
}
