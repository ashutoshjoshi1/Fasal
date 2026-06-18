"use client";

import { type ReactNode, useState } from "react";

import { cn } from "@/lib/cn";

export interface Column<T> {
  key: string;
  header: string;
  render: (row: T) => ReactNode;
  sortValue?: (row: T) => number | string;
  align?: "left" | "right";
}

export function DataTable<T>({
  columns,
  rows,
  onRowClick,
  getRowId,
}: {
  columns: Column<T>[];
  rows: T[];
  onRowClick?: (row: T) => void;
  getRowId?: (row: T) => string;
}) {
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [dir, setDir] = useState<1 | -1>(-1);

  const sorted = [...rows];
  const col = columns.find((c) => c.key === sortKey);
  if (col?.sortValue) {
    sorted.sort((a, b) => {
      const va = col.sortValue!(a);
      const vb = col.sortValue!(b);
      return (va < vb ? -1 : va > vb ? 1 : 0) * dir;
    });
  }

  const toggle = (key: string) => {
    if (sortKey === key) setDir((d) => (d === 1 ? -1 : 1));
    else {
      setSortKey(key);
      setDir(-1);
    }
  };

  return (
    <div className="overflow-x-auto rounded-card border border-border bg-surface-1">
      <table className="w-full border-collapse text-sm">
        <thead>
          <tr className="border-b border-border bg-surface-2 text-left">
            {columns.map((c) => (
              <th
                key={c.key}
                className={cn(
                  "px-3 py-2 text-xs font-medium uppercase tracking-wide text-text-muted",
                  c.align === "right" && "text-right",
                )}
              >
                {c.sortValue ? (
                  <button className="inline-flex items-center gap-1 hover:text-text-primary" onClick={() => toggle(c.key)}>
                    {c.header}
                    {sortKey === c.key && <span aria-hidden>{dir === 1 ? "↑" : "↓"}</span>}
                  </button>
                ) : (
                  c.header
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sorted.map((row, i) => (
            <tr
              key={getRowId ? getRowId(row) : i}
              className={cn("border-b border-border last:border-0", onRowClick && "cursor-pointer hover:bg-surface-2")}
              onClick={() => onRowClick?.(row)}
            >
              {columns.map((c) => (
                <td key={c.key} className={cn("px-3 py-2.5 align-middle", c.align === "right" && "text-right tnum")}>
                  {c.render(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
