# FASAL Console (web)

Next.js (App Router) + TypeScript + Tailwind v4 frontend for FASAL — the operator console for
pesticide-residue **risk screening** (screening, not certification). Built from
[`../design.md`](../design.md) and wired to the FastAPI backend.

## Quickstart

```bash
# 1) backend (from repo root)
pip install -e ".[api]"
uvicorn fasal.api.app:app --reload          # http://localhost:8000

# 2) frontend
cd web
cp .env.local.example .env.local            # NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
pnpm install
pnpm dev                                     # http://localhost:3000
```

## Stack
- **Next.js 15 / React 19**, App Router, TypeScript
- **Tailwind v4** (CSS-first `@theme`) with **OKLCH** design tokens (light / dark / field-high-contrast)
- **IBM Plex Sans/Mono** via `next/font`
- **TanStack Query** for server state
- **MapLibre GL** for the geospatial risk map

## Structure
```
web/
├── app/            # routes (console shell + views) + globals.css (tokens)
├── components/     # ui primitives + FASAL components + map + charts
├── lib/            # api client, types, theme/format helpers
└── public/
```

## Trust-first UX (non-negotiable)
Every risk output shows **class + calibrated score + confidence (incl. OOD) + reason codes + a
safety-first action**, with a persistent "Screening — not a lab result" disclaimer and a
"Request lab confirmation" path. Risk is encoded by **lightness order + icon + label** (+ hatch on
high) so it is colorblind-safe — never hue alone.
