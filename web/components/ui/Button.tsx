"use client";

import type { ButtonHTMLAttributes } from "react";

import { cn } from "@/lib/cn";

type Variant = "primary" | "secondary" | "ghost" | "danger";

const VARIANT: Record<Variant, string> = {
  primary: "bg-brand text-text-on-brand hover:bg-brand-strong border-transparent",
  secondary: "bg-surface-1 text-text-primary border-border-strong hover:bg-surface-2",
  ghost: "bg-transparent text-text-secondary border-transparent hover:bg-surface-2",
  danger: "bg-risk-high text-white border-transparent hover:opacity-90",
};

export function Button({
  variant = "secondary",
  className,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant }) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-input border px-3 py-1.5 text-sm font-medium",
        "transition-colors duration-150 disabled:cursor-not-allowed disabled:opacity-50",
        VARIANT[variant],
        className,
      )}
      {...props}
    />
  );
}
