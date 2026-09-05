"use client";

import { useEffect, useState } from "react";
import { Clock, CheckCircle, XCircle, FileText } from "lucide-react";
import { Card } from "@/components/ui/card";

interface AuditEntry {
  timestamp: string;
  action: string;
  details: string;
}

interface AuditTrailProps {
  transactionId: string;
}

export function AuditTrail({ transactionId }: AuditTrailProps) {
  const [auditLog, setAuditLog] = useState<AuditEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchAuditTrail() {
      try {
        setIsLoading(true);
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const response = await fetch(`${apiUrl}/transactions/${transactionId}/audit`);

        if (!response.ok) {
          throw new Error(`Failed to fetch audit trail: ${response.statusText}`);
        }

        const data = await response.json();
        setAuditLog(data.audit_trail || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load audit trail");
      } finally {
        setIsLoading(false);
      }
    }

    fetchAuditTrail();
  }, [transactionId]);

  if (isLoading) {
    return (
      <Card>
        <h3 className="text-lg font-semibold mb-4">Audit Trail</h3>
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-12 bg-zinc-200 dark:bg-zinc-700 rounded animate-pulse" />
          ))}
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800">
        <p className="text-sm text-red-800 dark:text-red-200">
          <strong>Error:</strong> {error}
        </p>
      </Card>
    );
  }

  const getActionIcon = (action: string) => {
    switch (action.toLowerCase()) {
      case "approved":
        return <CheckCircle className="h-5 w-5 text-green-600 dark:text-green-400" />;
      case "rejected":
        return <XCircle className="h-5 w-5 text-red-600 dark:text-red-400" />;
      case "created":
        return <FileText className="h-5 w-5 text-blue-600 dark:text-blue-400" />;
      default:
        return <Clock className="h-5 w-5 text-zinc-600 dark:text-zinc-400" />;
    }
  };

  const getActionLabel = (action: string) => {
    return action.charAt(0).toUpperCase() + action.slice(1);
  };

  return (
    <Card>
      <h3 className="text-lg font-semibold mb-4">Audit Trail</h3>

      {auditLog.length === 0 ? (
        <p className="text-sm text-zinc-500 dark:text-zinc-400">No audit log entries yet.</p>
      ) : (
        <div className="space-y-4">
          {auditLog.map((entry, index) => (
            <div key={index} className="flex gap-4 pb-4 border-b border-zinc-200 dark:border-zinc-800 last:border-b-0 last:pb-0">
              <div className="flex-shrink-0 pt-1">
                {getActionIcon(entry.action)}
              </div>
              <div className="flex-grow">
                <p className="font-medium text-sm">
                  {getActionLabel(entry.action)}
                </p>
                {entry.details && (
                  <p className="text-sm text-zinc-600 dark:text-zinc-400 mt-1">
                    {entry.details}
                  </p>
                )}
                <p className="text-xs text-zinc-500 dark:text-zinc-500 mt-2">
                  {new Date(entry.timestamp).toLocaleString()}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}
