"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { ArrowLeft, Download, Loader2, CheckCircle, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { fetchRiskThresholds, saveRiskThresholds } from "@/lib/api";

export default function SettingsPage() {
  const [emailAlerts, setEmailAlerts] = useState(true);
  const [smsAlerts, setSmsAlerts] = useState(false);
  const [sensitivity, setSensitivity] = useState(65);
  const [highRiskThreshold, setHighRiskThreshold] = useState(0.65);
  const [mediumRiskThreshold, setMediumRiskThreshold] = useState(0.35);
  
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [toast, setToast] = useState<{ type: "success" | "error"; message: string } | null>(null);

  useEffect(() => {
    async function loadSettings() {
      try {
        const data = await fetchRiskThresholds();
        setHighRiskThreshold(data.high);
        setMediumRiskThreshold(data.medium);
      } catch (err) {
        console.error("Failed to load thresholds:", err);
      } finally {
        setIsLoading(false);
      }
    }
    loadSettings();
  }, []);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await saveRiskThresholds({
        high: highRiskThreshold,
        medium: mediumRiskThreshold,
      });
      setToast({ type: "success", message: "Settings saved successfully" });
      setTimeout(() => setToast(null), 3000);
    } catch (err) {
      setToast({ type: "error", message: "Failed to save settings" });
      setTimeout(() => setToast(null), 3000);
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto p-6 flex justify-center items-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-zinc-400" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 relative">
      {/* Toast Notification */}
      {toast && (
        <div
          className={`fixed top-4 right-4 z-50 px-4 py-3 rounded-lg shadow-lg flex items-center gap-3 animate-in slide-in-from-top ${
            toast.type === "success"
              ? "bg-green-100 dark:bg-green-900/20 text-green-800 dark:text-green-200 border border-green-200 dark:border-green-800"
              : "bg-red-100 dark:bg-red-900/20 text-red-800 dark:text-red-200 border border-red-200 dark:border-red-800"
          }`}
        >
          {toast.type === "success" ? (
            <CheckCircle className="h-5 w-5" />
          ) : (
            <AlertTriangle className="h-5 w-5" />
          )}
          <span className="font-medium">{toast.message}</span>
        </div>
      )}

      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href="/">
          <Button variant="ghost" className="gap-2">
            <ArrowLeft className="h-4 w-4" />
            Back to Dashboard
          </Button>
        </Link>
      </div>

      <h1 className="text-3xl font-bold">Settings</h1>

      {/* Alert Preferences */}
      <Card>
        <div className="space-y-6">
          <h2 className="text-xl font-semibold">Alert Preferences</h2>

          {/* Email Alerts */}
          <div className="flex items-center justify-between p-4 border border-zinc-200 dark:border-zinc-800 rounded-lg">
            <div>
              <h3 className="font-medium">Email Alerts</h3>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">
                Get notifications for high-risk transactions
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={emailAlerts}
                onChange={(e) => setEmailAlerts(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-zinc-300 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-zinc-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all dark:peer-checked:bg-blue-600 peer-checked:bg-blue-600"></div>
            </label>
          </div>

          {/* SMS Alerts */}
          <div className="flex items-center justify-between p-4 border border-zinc-200 dark:border-zinc-800 rounded-lg">
            <div>
              <h3 className="font-medium">SMS Alerts</h3>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">
                Get text messages for critical alerts
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={smsAlerts}
                onChange={(e) => setSmsAlerts(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-zinc-300 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-zinc-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all dark:peer-checked:bg-blue-600 peer-checked:bg-blue-600"></div>
            </label>
          </div>
        </div>
      </Card>

      {/* Detection Sensitivity */}
      <Card>
        <div className="space-y-6">
          <div>
            <h2 className="text-xl font-semibold">Detection Sensitivity</h2>
            <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-2">
              Adjust how aggressive the fraud detection should be
            </p>
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium">Overall Sensitivity</label>
              <span className="text-sm font-bold text-blue-600 dark:text-blue-400">
                {sensitivity}%
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={sensitivity}
              onChange={(e) => setSensitivity(Number(e.target.value))}
              className="w-full h-2 bg-zinc-300 rounded-lg appearance-none cursor-pointer dark:bg-zinc-700"
            />
            <div className="flex justify-between text-xs text-zinc-500 dark:text-zinc-400">
              <span>Low (Fewer alerts)</span>
              <span>High (More alerts)</span>
            </div>
          </div>
        </div>
      </Card>

      {/* Risk Thresholds */}
      <Card>
        <div className="space-y-6">
          <h2 className="text-xl font-semibold">Risk Thresholds</h2>

          <div className="space-y-4">
            {/* High Risk */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium text-red-700 dark:text-red-300">
                  High Risk Threshold
                </label>
                <span className="text-sm font-bold text-red-600 dark:text-red-400">
                  {highRiskThreshold.toFixed(2)}
                </span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={highRiskThreshold}
                onChange={(e) => setHighRiskThreshold(Number(e.target.value))}
                className="w-full h-2 bg-red-300 rounded-lg appearance-none cursor-pointer dark:bg-red-700"
              />
              <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">
                Transactions with score ≥ {highRiskThreshold.toFixed(2)} are HIGH risk
              </p>
            </div>

            {/* Medium Risk */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium text-amber-700 dark:text-amber-300">
                  Medium Risk Threshold
                </label>
                <span className="text-sm font-bold text-amber-600 dark:text-amber-400">
                  {mediumRiskThreshold.toFixed(2)}
                </span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={mediumRiskThreshold}
                onChange={(e) => setMediumRiskThreshold(Number(e.target.value))}
                className="w-full h-2 bg-amber-300 rounded-lg appearance-none cursor-pointer dark:bg-amber-700"
              />
              <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">
                Transactions between {mediumRiskThreshold.toFixed(2)} and {highRiskThreshold.toFixed(2)} are MEDIUM risk
              </p>
            </div>
          </div>
        </div>
      </Card>

      {/* Data & Privacy */}
      <Card>
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Data & Privacy</h2>

          <button className="w-full px-4 py-3 text-left border border-zinc-300 dark:border-zinc-700 rounded-lg hover:bg-zinc-50 dark:hover:bg-zinc-900 transition-colors flex items-center justify-between">
            <div>
              <p className="font-medium">Export Audit Log</p>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">
                Download all your transaction actions and decisions
              </p>
            </div>
            <Download className="h-4 w-4 text-zinc-400" />
          </button>

          <button className="w-full px-4 py-3 text-left border border-zinc-300 dark:border-zinc-700 rounded-lg hover:bg-zinc-50 dark:hover:bg-zinc-900 transition-colors flex items-center justify-between">
            <div>
              <p className="font-medium">Export All Data</p>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">
                Download all transactions in CSV format
              </p>
            </div>
            <Download className="h-4 w-4 text-zinc-400" />
          </button>
        </div>
      </Card>

      {/* Save Button */}
      <div className="flex gap-3">
        <Button 
          className="flex-1 sm:flex-auto" 
          onClick={handleSave} 
          disabled={isSaving}
        >
          {isSaving ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Saving...
            </>
          ) : (
            "Save Settings"
          )}
        </Button>
        <Link href="/">
          <Button variant="ghost" className="flex-1 sm:flex-auto">
            Cancel
          </Button>
        </Link>
      </div>

      {/* Info Box */}
      <Card className="bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
        <p className="text-sm text-blue-800 dark:text-blue-200">
          <strong>Note:</strong> Settings are currently in demo mode. Persistent settings configuration coming in Phase 2.
        </p>
      </Card>
    </div>
  );
}
