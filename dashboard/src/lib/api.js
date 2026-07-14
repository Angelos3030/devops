export const API_BASE = (import.meta.env.VITE_API_BASE || '').replace(/\/$/, '')

export async function api(path, opts) {
  const res = await fetch(API_BASE + path, opts)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

// Direct URL for iframes / new-tab previews (not fetched)
export const previewUrl = (clientId, layout) =>
  `${API_BASE}/clients/${clientId}/preview/${layout}`
