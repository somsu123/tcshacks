import { type ClassValue, clsx } from "clsx";

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

export function formatAmount(amount: number): string {
  return `£${amount.toLocaleString("en-GB", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

export function formatTimestamp(timestamp: string): string {
  const date = new Date(timestamp);
  return date.toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function formatFullTimestamp(timestamp: string): string {
  const date = new Date(timestamp);
  return date.toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export interface ParsedRiskFactor {
  number: string;
  title: string;
  description: string;
  icon: string;
}

export function parseRiskFactor(factor: string): ParsedRiskFactor {
  // Format: "1. New Payee - First-ever transfer to this payee..."
  const match = factor.match(/^(\d+)\.\s*([^-]+)\s*-\s*(.+)$/);
  if (!match) {
    return { number: "1", title: factor, description: "", icon: "⚠️" };
  }

  const [, number, title, description] = match;

  // Map titles to icons
  const iconMap: Record<string, string> = {
    "new payee": "👤",
    "unusual timing": "🕐",
    "amount spike": "📈",
    "suspicious reference": "⚠️",
    "geo velocity": "🌍",
    "velocity": "⚡",
    "impossible travel": "✈️",
  };

  const icon = iconMap[title.toLowerCase().trim()] || "⚠️";

  return {
    number,
    title: title.trim(),
    description: description.trim(),
    icon,
  };
}

export const riskColors = {
  high: {
    bg: "bg-red-500",
    bgLight: "bg-red-500/10",
    text: "text-red-500",
    border: "border-red-500",
  },
  medium: {
    bg: "bg-amber-500",
    bgLight: "bg-amber-500/10",
    text: "text-amber-500",
    border: "border-amber-500",
  },
  low: {
    bg: "bg-emerald-500",
    bgLight: "bg-emerald-500/10",
    text: "text-emerald-500",
    border: "border-emerald-500",
  },
} as const;

export const riskEmoji = {
  high: "🔴",
  medium: "🟡",
  low: "🟢",
} as const;
