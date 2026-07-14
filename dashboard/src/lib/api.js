export const API_BASE = (import.meta.env.VITE_API_BASE || '').replace(/\/$/, '')
// The Next.js multi-tenant sites app (renders React templates from live client data).
export const SITES_BASE = (import.meta.env.VITE_SITES_BASE || 'http://localhost:3000').replace(/\/$/, '')

export async function api(path, opts) {
  const res = await fetch(API_BASE + path, opts)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

// Preview a client's site as a real React template (not the old static HTML).
export const previewUrl = (clientId, layout) =>
  `${SITES_BASE}/site/${clientId}?layout=${layout}`
