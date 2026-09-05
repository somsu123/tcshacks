"use client";

import { cn } from "@/lib/utils";
import { ButtonHTMLAttributes, forwardRef } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "outline" | "ghost" | "danger" | "success" | "warning";
  size?: "sm" | "md" | "lg";
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", size = "md", children, ...props }, ref) => {
    const baseStyles =
      "inline-flex items-center justify-center font-medium rounded-lg transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50";

    const variants = {
      default:
        "bg-accent text-white hover:bg-accent/90 focus-visible:ring-accent",
      outline:
        "border border-[var(--border)] bg-transparent hover:bg-[var(--card)] focus-visible:ring-accent",
      ghost:
        "bg-transparent hover:bg-[var(--card)] focus-visible:ring-accent",
      danger:
        "bg-red-500 text-white hover:bg-red-600 focus-visible:ring-red-500",
      success:
        "bg-emerald-500 text-white hover:bg-emerald-600 focus-visible:ring-emerald-500",
      warning:
        "bg-amber-500 text-white hover:bg-amber-600 focus-visible:ring-amber-500",
    };

    const sizes = {
      sm: "h-8 px-3 text-sm",
      md: "h-10 px-4 text-sm",
      lg: "h-12 px-6 text-base",
    };

    return (
      <button
        ref={ref}
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        {...props}
      >
        {children}
      </button>
    );
  }
);

Button.displayName = "Button";
