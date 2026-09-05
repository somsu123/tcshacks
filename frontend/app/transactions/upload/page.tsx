"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowLeft, Upload, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

import { loadSampleData } from "@/lib/api";

export default function UploadTransactionsPage() {
  const router = useRouter();
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<{ success: number; missing: number; failed: number } | null>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFile(e.target.files[0]);
    }
  };

  const handleLoadSample = async () => {
    setIsUploading(true);
    setError(null);
    try {
      await loadSampleData();
      router.push("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load sample data");
    } finally {
      setIsUploading(false);
    }
  };

  const handleFile = async (file: File) => {
    // Validate file type
    if (!file.name.endsWith(".csv") && file.type !== "text/csv") {
      setError("Please upload a CSV file");
      return;
    }

    setIsUploading(true);
    setError(null);
    setResults(null);

    try {
      // Parse CSV
      const text = await file.text();
      const lines = text.split("\n").filter((line) => line.trim());

      if (lines.length < 2) {
        throw new Error("CSV file must contain header and at least one row");
      }

      // Parse header
      const header = lines[0].split(",").map((h) => h.trim().toLowerCase());
      const requiredFields = ["amount", "payee", "reference", "timestamp"];
      const missingFields = requiredFields.filter((field) => !header.includes(field));

      if (missingFields.length > 0) {
        throw new Error(
          `CSV missing required columns: ${missingFields.join(", ")}. Required: amount, payee, reference, timestamp`
        );
      }

      // Parse rows
      const transactions = [];
      let missingCount = 0;
      let failedCount = 0;

      for (let i = 1; i < lines.length; i++) {
        const values = lines[i].split(",").map((v) => v.trim());
        const row: Record<string, string> = {};

        header.forEach((field, index) => {
          row[field] = values[index] || "";
        });

        try {
          // Build transaction object
          const transaction = {
            amount: parseFloat(row.amount),
            payee: row.payee,
            reference: row.reference,
            timestamp: new Date(row.timestamp).toISOString(),
            payee_is_new: row.payee_is_new?.toLowerCase() === "true",
          };

          // Validate
          if (!transaction.amount || transaction.amount <= 0 || !transaction.payee || !transaction.reference || !transaction.timestamp || transaction.timestamp === "Invalid Date") {
            missingCount++;
            continue;
          }

          transactions.push(transaction);
        } catch (_rowError) {
          failedCount++;
          console.error(`Row ${i + 1} failed:`, _rowError);
        }
      }

      // Upload transactions
      if (transactions.length === 0 && missingCount === 0 && failedCount === 0) {
        throw new Error("No valid transactions found in CSV");
      }

      let uploadedCount = 0;

      for (const transaction of transactions) {
        try {
          const response = await fetch(`${API_BASE}/transactions`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(transaction),
          });

          if (response.ok) {
            uploadedCount++;
          } else {
            failedCount++;
          }
        } catch {
          failedCount++;
        }
      }

      setResults({
        success: uploadedCount,
        missing: missingCount,
        failed: failedCount,
      });

      // Redirect after success
      if (uploadedCount > 0) {
        setTimeout(() => {
          router.push("/");
        }, 2000);
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : "Failed to process file");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href="/">
          <Button variant="ghost" className="gap-2">
            <ArrowLeft className="h-4 w-4" />
            Back to Dashboard
          </Button>
        </Link>
      </div>

      <Card>
        <div className="space-y-6">
          <div>
            <h1 className="text-2xl font-bold">Import Transactions</h1>
            <p className="text-zinc-500 dark:text-zinc-400 mt-1">
              Upload a CSV file to bulk import transactions
            </p>
          </div>

          {/* File Upload Area */}
          {!results && (
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => {
                const input = document.getElementById('csv-upload') as HTMLInputElement;
                input?.click();
              }}
              className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer ${
                isDragging
                  ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                  : "border-zinc-300 dark:border-zinc-700 hover:border-zinc-400 dark:hover:border-zinc-600"
              }`}
            >
              <div className="flex flex-col items-center gap-3">
                <Upload className="h-8 w-8 text-zinc-400" />
                <div>
                  <p className="font-medium">Drop your CSV file here</p>
                  <p className="text-sm text-zinc-500 dark:text-zinc-400">
                    or click to select
                  </p>
                </div>
              </div>
              <input
                id="csv-upload"
                type="file"
                accept=".csv"
                onChange={handleFileInput}
                disabled={isUploading}
                className="hidden"
              />
            </div>
          )}

          {/* Error Alert */}
          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
              <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
            </div>
          )}

          {/* Results */}
          {results && (
            <div className="bg-zinc-50 dark:bg-zinc-900/50 border border-zinc-200 dark:border-zinc-800 rounded-lg p-6">
              <h3 className="font-semibold text-lg mb-4">
                Import Complete
              </h3>
              <div className="space-y-3">
                <div className="flex items-center gap-2 text-green-700 dark:text-green-400 font-medium">
                  <span>✅</span>
                  <span>Successfully analyzed: {results.success}</span>
                </div>
                {results.missing > 0 && (
                  <div className="flex items-center gap-2 text-amber-600 dark:text-amber-400 font-medium">
                    <span>⚠️</span>
                    <span>Could not evaluate (missing required fields): {results.missing}</span>
                  </div>
                )}
                {results.failed > 0 && (
                  <div className="flex items-center gap-2 text-red-600 dark:text-red-400 font-medium">
                    <span>❌</span>
                    <span>Failed (other errors): {results.failed}</span>
                  </div>
                )}
              </div>
              {results.success > 0 && (
                <p className="text-sm text-zinc-500 mt-4">
                  Redirecting to dashboard...
                </p>
              )}
            </div>
          )}

          {!results && !error && (
            <div className="text-center pt-2 pb-2">
              <span className="text-sm text-zinc-500">Or</span>
            </div>
          )}

          {!results && (
            <Button
              variant="outline"
              disabled={isUploading}
              onClick={handleLoadSample}
              className="w-full"
            >
              {isUploading ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : null}
              Load Sample Dataset Instead
            </Button>
          )}

          {/* CSV Format Help */}
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">
              CSV Format Required
            </h4>
            <p className="text-sm text-blue-800 dark:text-blue-200 mb-3">
              Your CSV must include these columns:
            </p>
            <code className="block bg-white dark:bg-zinc-900 p-3 rounded text-xs text-zinc-900 dark:text-zinc-100 overflow-x-auto">
              amount,payee,reference,timestamp,payee_is_new
            </code>
            <p className="text-xs text-blue-700 dark:text-blue-300 mt-3">
              Example:
              <br />
              2000,ABC Holdings Ltd,Invoice 2847,2026-01-05T15:30:00Z,true
            </p>
          </div>

          {/* Upload Button */}
          <Button
            disabled={isUploading || !!results}
            className="w-full"
            onClick={() => {
              const input = document.getElementById('csv-upload') as HTMLInputElement;
              input?.click();
            }}
          >
            {isUploading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <Upload className="h-4 w-4 mr-2" />
                Select CSV File
              </>
            )}
          </Button>
        </div>
      </Card>
    </div>
  );
}
