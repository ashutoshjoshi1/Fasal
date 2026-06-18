import { cn } from "@/lib/cn";

export function Skeleton({ className }: { className?: string }) {
  return <div className={cn("animate-pulse rounded-md bg-surface-sunken", className)} />;
}

export function Loading({ label = "Loading…" }: { label?: string }) {
  return (
    <div className="flex items-center gap-2 p-4 text-sm text-text-muted">
      <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-border border-t-brand" />
      {label}
    </div>
  );
}

export function EmptyState({ title, hint }: { title: string; hint?: string }) {
  return (
    <div className="grid place-items-center rounded-card border border-dashed border-border p-8 text-center">
      <p className="font-medium text-text-primary">{title}</p>
      {hint && <p className="mt-1 text-sm text-text-muted">{hint}</p>}
    </div>
  );
}

export function ErrorState({ message }: { message?: string }) {
  return (
    <div
      className="rounded-card border p-4 text-sm"
      style={{
        borderColor: "color-mix(in oklch, var(--danger) 40%, transparent)",
        background: "color-mix(in oklch, var(--danger) 8%, transparent)",
        color: "var(--text-secondary)",
      }}
      role="alert"
    >
      <strong className="text-text-primary">Couldn&rsquo;t load data.</strong>{" "}
      {message ?? "Is the backend running on :8000? (uvicorn fasal.api.app:app --reload)"}
    </div>
  );
}
