"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { ArrowLeft, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Form validation schema - define both input and output types
const transactionSchema = z.object({
  amount: z.number().positive("Amount must be greater than 0").max(1000000, "Amount too large"),
  payee: z
    .string()
    .min(1, "Payee name is required")
    .max(255, "Payee name too long"),
  reference: z
    .string()
    .min(1, "Reference is required")
    .max(100, "Reference too long"),
  timestamp: z.string().min(1, "Timestamp is required"),
  payee_is_new: z.boolean(),
});

type TransactionFormData = z.infer<typeof transactionSchema>;

export default function NewTransactionPage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<TransactionFormData>({
    resolver: zodResolver(transactionSchema),
    defaultValues: {
      payee_is_new: false,
      timestamp: new Date().toISOString().slice(0, 16), // Format for datetime-local
    },
  });

  const onSubmit = async (data: TransactionFormData) => {
    setIsSubmitting(true);
    setError(null);

    try {
      // Convert datetime-local to ISO 8601
      const payload = {
        ...data,
        amount: Number(data.amount),
        timestamp: new Date(data.timestamp).toISOString(),
      };

      const response = await fetch(`${API_BASE}/transactions`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to create transaction");
      }

      const result = await response.json();
      router.push(`/transactions/${result.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setIsSubmitting(false);
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
            <h1 className="text-2xl font-bold">Add New Transaction</h1>
            <p className="text-zinc-500 dark:text-zinc-400 mt-1">
              Submit a transaction for fraud detection analysis
            </p>
          </div>

          {/* Error Alert */}
          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
              <p className="text-sm text-red-800 dark:text-red-200">
                {error}
              </p>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Amount */}
            <div className="space-y-2">
              <label
                htmlFor="amount"
                className="block text-sm font-medium"
              >
                Amount (£)
              </label>
              <input
                id="amount"
                type="number"
                step="0.01"
                {...register("amount", { valueAsNumber: true })}
                className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-700 rounded-lg bg-white dark:bg-zinc-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="1250.00"
              />
              {errors.amount && (
                <p className="text-sm text-red-600 dark:text-red-400">
                  {errors.amount.message}
                </p>
              )}
            </div>

            {/* Payee */}
            <div className="space-y-2">
              <label
                htmlFor="payee"
                className="block text-sm font-medium"
              >
                Payee Name
              </label>
              <input
                id="payee"
                type="text"
                {...register("payee")}
                className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-700 rounded-lg bg-white dark:bg-zinc-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="ABC Holdings Ltd"
              />
              {errors.payee && (
                <p className="text-sm text-red-600 dark:text-red-400">
                  {errors.payee.message}
                </p>
              )}
            </div>

            {/* Reference */}
            <div className="space-y-2">
              <label
                htmlFor="reference"
                className="block text-sm font-medium"
              >
                Reference
              </label>
              <input
                id="reference"
                type="text"
                {...register("reference")}
                className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-700 rounded-lg bg-white dark:bg-zinc-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Invoice 2847"
              />
              {errors.reference && (
                <p className="text-sm text-red-600 dark:text-red-400">
                  {errors.reference.message}
                </p>
              )}
            </div>

            {/* Timestamp */}
            <div className="space-y-2">
              <label
                htmlFor="timestamp"
                className="block text-sm font-medium"
              >
                Transaction Date & Time
              </label>
              <input
                id="timestamp"
                type="datetime-local"
                {...register("timestamp")}
                className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-700 rounded-lg bg-white dark:bg-zinc-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              {errors.timestamp && (
                <p className="text-sm text-red-600 dark:text-red-400">
                  {errors.timestamp.message}
                </p>
              )}
            </div>

            {/* New Payee Checkbox */}
            <div className="flex items-center gap-2">
              <input
                id="payee_is_new"
                type="checkbox"
                {...register("payee_is_new")}
                className="h-4 w-4 rounded border-zinc-300 dark:border-zinc-700 text-blue-600 focus:ring-blue-500"
              />
              <label
                htmlFor="payee_is_new"
                className="text-sm font-medium"
              >
                This is a first-time transfer to this payee
              </label>
            </div>

            {/* Submit Buttons */}
            <div className="flex gap-3 pt-4">
              <Button
                type="submit"
                disabled={isSubmitting}
                className="flex-1"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  "Submit Transaction"
                )}
              </Button>
              <Link href="/" className="flex-1">
                <Button
                  type="button"
                  variant="ghost"
                  className="w-full"
                  disabled={isSubmitting}
                >
                  Cancel
                </Button>
              </Link>
            </div>
          </form>
        </div>
      </Card>

      {/* Help Text */}
      <Card className="bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
        <p className="text-sm text-blue-800 dark:text-blue-200">
          <strong>Tip:</strong> Check &ldquo;first-time transfer&rdquo; if you&apos;ve never sent money to this payee before. This helps our fraud detection system assess risk more accurately.
        </p>
      </Card>
    </div>
  );
}
