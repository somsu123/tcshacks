"use client";

import Link from "next/link";
import { Shield, Settings } from "lucide-react";
import { ThemeToggle } from "../ui/theme-toggle";

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-[var(--background)]/80 backdrop-blur-lg">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <Link href="/" className="flex items-center gap-2">
          <Shield className="h-8 w-8 text-accent" />
          <div>
            <h1 className="text-xl font-bold tracking-tight">FraudShield AI</h1>
            <p className="text-xs text-zinc-500 dark:text-zinc-400 hidden sm:block">
              Explainable Fraud Detection for SMBs
            </p>
          </div>
        </Link>
        <div className="flex items-center gap-2">
          <Link href="/settings" title="Settings">
            <button className="p-2 hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded-lg transition-colors">
              <Settings className="h-5 w-5" />
            </button>
          </Link>
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
