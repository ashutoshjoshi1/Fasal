import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

/**
 * Per-request nonce-based Content-Security-Policy.
 *
 * Next.js detects the nonce from the request CSP header and applies it to its own framework
 * scripts; `strict-dynamic` then trusts the chunks those nonce'd scripts load, so no host
 * allowlist is needed for scripts. The CSP is also set on the response for the browser to enforce.
 *
 * FASAL-specific allowances:
 *  - img-src: the backend renders capture PNGs ({API_ORIGIN}); MapLibre paints to blob:/data:.
 *  - connect-src: the API origin (data fetches) + ws: in dev (HMR).
 *  - worker-src blob: — MapLibre GL spawns its workers from blob: URLs.
 *  - style-src 'unsafe-inline' — React inline styles carry the OKLCH design tokens.
 */
const API_ORIGIN = (() => {
  try {
    return new URL(process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000").origin;
  } catch {
    return "";
  }
})();

export function middleware(request: NextRequest) {
  const isDev = process.env.NODE_ENV !== "production";
  const nonce = btoa(String.fromCharCode(...crypto.getRandomValues(new Uint8Array(16))));

  const scriptSrc = ["'self'", `'nonce-${nonce}'`, "'strict-dynamic'", isDev && "'unsafe-eval'"]
    .filter(Boolean)
    .join(" ");
  const connectSrc = ["'self'", API_ORIGIN, isDev && "ws:"].filter(Boolean).join(" ");
  const imgSrc = ["'self'", "blob:", "data:", API_ORIGIN].filter(Boolean).join(" ");

  const csp = [
    `default-src 'self'`,
    `script-src ${scriptSrc}`,
    `style-src 'self' 'unsafe-inline'`,
    `img-src ${imgSrc}`,
    `font-src 'self' data:`,
    `connect-src ${connectSrc}`,
    `worker-src blob:`,
    `object-src 'none'`,
    `base-uri 'self'`,
    `form-action 'self'`,
    `frame-ancestors 'none'`,
    !isDev && `upgrade-insecure-requests`,
  ]
    .filter(Boolean)
    .join("; ");

  const requestHeaders = new Headers(request.headers);
  requestHeaders.set("x-nonce", nonce);
  requestHeaders.set("Content-Security-Policy", csp); // read by Next to nonce its scripts

  const response = NextResponse.next({ request: { headers: requestHeaders } });
  response.headers.set("Content-Security-Policy", csp); // enforced by the browser
  return response;
}

export const config = {
  // Run on pages, not on static assets or image optimizer output.
  matcher: [
    {
      source:
        "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:png|jpg|jpeg|gif|svg|ico|webp|avif|woff2?)$).*)",
    },
  ],
};
