"use client";

import { Search } from "lucide-react";
import { Card } from "@/components/ui/card";
import { RiskLevel } from "@/lib/types";

interface DashboardFiltersProps {
  onSearchChange: (query: string) => void;
  onRiskLevelChange: (level: RiskLevel | "all") => void;
  onStatusChange?: (status: string | "all") => void;
  searchQuery: string;
  riskLevel: RiskLevel | "all";
  statusFilter?: string | "all";
}

export function DashboardFilters({
  onSearchChange,
  onRiskLevelChange,
  onStatusChange,
  searchQuery,
  riskLevel,
  statusFilter = "all",
}: DashboardFiltersProps) {
  const riskLevels: Array<{ value: RiskLevel | "all"; label: string; color: string }> = [
    { value: "all", label: "All Risks", color: "bg-zinc-100 dark:bg-zinc-800" },
    { value: "high", label: "High Risk", color: "bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-200" },
    { value: "medium", label: "Medium Risk", color: "bg-amber-100 dark:bg-amber-900/20 text-amber-700 dark:text-amber-200" },
    { value: "low", label: "Low Risk", color: "bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-200" },
  ];

  const statuses: Array<{ value: string; label: string; color: string }> = [
    { value: "all", label: "All Statuses", color: "bg-zinc-100 dark:bg-zinc-800" },
    { value: "pending", label: "Pending", color: "bg-zinc-100 dark:bg-zinc-800" },
    { value: "approved", label: "Approved", color: "bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-200" },
    { value: "rejected", label: "Rejected", color: "bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-200" },
    { value: "hold", label: "Held", color: "bg-amber-100 dark:bg-amber-900/20 text-amber-700 dark:text-amber-200" },
  ];

  return (
    <Card>
      <div className="space-y-4">
        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-zinc-400" />
          <input
            type="text"
            placeholder="Search by payee or reference..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-zinc-300 dark:border-zinc-700 rounded-lg bg-white dark:bg-zinc-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="flex flex-col gap-3">
          {/* Risk Level Filter Chips */}
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-sm font-medium text-zinc-500 mr-2 w-16">Risk:</span>
            {riskLevels.map((level) => (
              <button
                key={level.value}
                onClick={() => onRiskLevelChange(level.value)}
                className={`px-3 py-1 rounded-full text-sm font-medium transition-all ${
                  riskLevel === level.value
                    ? level.color + " ring-2 ring-offset-2 dark:ring-offset-zinc-950"
                    : "bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 hover:bg-zinc-200 dark:hover:bg-zinc-700"
                }`}
              >
                {level.label}
              </button>
            ))}
          </div>

          {/* Status Filter Chips */}
          {onStatusChange && (
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-sm font-medium text-zinc-500 mr-2 w-16">Status:</span>
              {statuses.map((s) => (
                <button
                  key={s.value}
                  onClick={() => onStatusChange(s.value)}
                  className={`px-3 py-1 rounded-full text-sm font-medium transition-all ${
                    statusFilter === s.value
                      ? s.color + " ring-2 ring-offset-2 dark:ring-offset-zinc-950"
                      : "bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 hover:bg-zinc-200 dark:hover:bg-zinc-700"
                  }`}
                >
                  {s.label}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </Card>
  );
}
