"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { ScreeningDisclaimer } from "@/components/ui/ScreeningDisclaimer";
import { cn } from "@/lib/cn";
import { useFields } from "@/lib/queries";
import { fmtCoord } from "@/lib/risk";

import { useTheme, type Theme } from "@/app/providers";
import { SelectedFieldProvider, useSelectedField } from "./field-context";

type IconProps = { className?: string };
const stroke = { fill: "none", stroke: "currentColor", strokeWidth: 1.6, strokeLinecap: "round" as const, strokeLinejoin: "round" as const };

const MapIcon = (p: IconProps) => (
  <svg viewBox="0 0 24 24" width="18" height="18" {...stroke} {...p}>
    <path d="M9 4 3 6v14l6-2 6 2 6-2V4l-6 2-6-2Z" /><path d="M9 4v14M15 6v14" />
  </svg>
);
const FlightIcon = (p: IconProps) => (
  <svg viewBox="0 0 24 24" width="18" height="18" {...stroke} {...p}>
    <circle cx="12" cy="12" r="3" /><path d="M12 2v4M12 18v4M2 12h4M18 12h4" />
  </svg>
);
const BatchIcon = (p: IconProps) => (
  <svg viewBox="0 0 24 24" width="18" height="18" {...stroke} {...p}>
    <path d="M3 7l9-4 9 4-9 4-9-4Z" /><path d="M3 7v10l9 4 9-4V7M12 11v10" />
  </svg>
);
const UploadIcon = (p: IconProps) => (
  <svg viewBox="0 0 24 24" width="18" height="18" {...stroke} {...p}>
    <path d="M12 16V4M7 9l5-5 5 5" /><path d="M4 20h16" />
  </svg>
);
const ChartIcon = (p: IconProps) => (
  <svg viewBox="0 0 24 24" width="18" height="18" {...stroke} {...p}>
    <path d="M4 20V4M4 20h16" /><path d="M8 16l4-5 3 3 4-6" />
  </svg>
);
const GridIcon = (p: IconProps) => (
  <svg viewBox="0 0 24 24" width="18" height="18" {...stroke} {...p}>
    <rect x="4" y="4" width="6" height="6" rx="1" /><rect x="14" y="4" width="6" height="6" rx="1" />
    <rect x="4" y="14" width="6" height="6" rx="1" /><rect x="14" y="14" width="6" height="6" rx="1" />
  </svg>
);
const ImageIcon = (p: IconProps) => (
  <svg viewBox="0 0 24 24" width="18" height="18" {...stroke} {...p}>
    <rect x="3" y="5" width="18" height="14" rx="2" /><path d="M3 16l5-5 4 4 3-3 6 6" /><circle cx="8.5" cy="9.5" r="1.2" />
  </svg>
);

const NAV = [
  { href: "/", label: "Field map", Icon: MapIcon },
  { href: "/flights", label: "Flights", Icon: FlightIcon },
  { href: "/batches", label: "Batch & lab", Icon: BatchIcon },
  { href: "/upload", label: "Upload", Icon: UploadIcon },
  { href: "/regional", label: "Regional", Icon: ChartIcon },
  { href: "/dataset", label: "Dataset", Icon: ImageIcon },
  { href: "/components", label: "Components", Icon: GridIcon },
];

const THEMES: Theme[] = ["light", "dark", "field"];

function FieldSelector() {
  const { data: fields } = useFields();
  const { fieldId, setFieldId } = useSelectedField();
  const selected = fields?.find((f) => f.id === fieldId) ?? fields?.[0];
  return (
    <div className="flex items-center gap-3">
      <select
        aria-label="Selected field"
        value={selected?.id ?? ""}
        onChange={(e) => setFieldId(e.target.value)}
        className="rounded-input border border-border-strong bg-surface-1 px-3 py-1.5 text-sm font-medium text-text-primary"
      >
        {(fields ?? []).map((f) => (
          <option key={f.id} value={f.id}>
            {f.crop} · {f.name}
          </option>
        ))}
        {!fields?.length && <option>Loading fields…</option>}
      </select>
      {selected && (
        <span className="hidden font-mono text-xs text-text-muted md:inline">
          {fmtCoord(selected.location.lat, selected.location.lon)}
        </span>
      )}
    </div>
  );
}

function ThemeControl() {
  const { theme, setTheme } = useTheme();
  return (
    <div className="flex items-center rounded-full border border-border bg-surface-2 p-0.5">
      {THEMES.map((t) => (
        <button
          key={t}
          onClick={() => setTheme(t)}
          className={cn(
            "rounded-full px-2.5 py-1 text-xs font-medium capitalize transition-colors",
            theme === t ? "bg-surface-1 text-text-primary shadow-[var(--shadow-soft)]" : "text-text-muted hover:text-text-secondary",
          )}
        >
          {t}
        </button>
      ))}
    </div>
  );
}

function Shell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  return (
    <div className="flex h-dvh overflow-hidden bg-surface-app">
      {/* left rail */}
      <nav aria-label="Main navigation" className="flex w-[200px] shrink-0 flex-col border-r border-border bg-surface-1">
        <div className="flex items-center gap-2 px-4 py-4">
          <span className="grid h-7 w-7 place-items-center rounded-md bg-brand font-mono text-sm font-semibold text-text-on-brand">F</span>
          <span className="text-sm font-semibold tracking-tight text-text-primary">FASAL</span>
        </div>
        <ul className="flex flex-col gap-0.5 px-2">
          {NAV.map(({ href, label, Icon }) => {
            const active = href === "/" ? pathname === "/" : pathname.startsWith(href);
            return (
              <li key={href}>
                <Link
                  href={href}
                  className={cn(
                    "flex items-center gap-2.5 rounded-input px-3 py-2 text-sm font-medium transition-colors",
                    active ? "bg-brand-tint text-brand-strong" : "text-text-secondary hover:bg-surface-2",
                  )}
                >
                  <Icon /> {label}
                </Link>
              </li>
            );
          })}
        </ul>
        <div className="mt-auto p-3 text-xs text-text-muted">
          <p>Risk screening only.</p>
          <p>Labs remain the reference truth.</p>
        </div>
      </nav>

      {/* header + content */}
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center gap-4 border-b border-border bg-surface-1 px-5 py-3">
          <FieldSelector />
          <div className="ml-auto flex items-center gap-3">
            <ScreeningDisclaimer />
            <ThemeControl />
          </div>
        </header>
        <main className="min-h-0 flex-1 overflow-auto">{children}</main>
      </div>
    </div>
  );
}

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <SelectedFieldProvider>
      <Shell>{children}</Shell>
    </SelectedFieldProvider>
  );
}
