import "maplibre-gl/dist/maplibre-gl.css";

import { AppShell } from "@/components/shell/AppShell";

export default function ConsoleLayout({ children }: { children: React.ReactNode }) {
  return <AppShell>{children}</AppShell>;
}
