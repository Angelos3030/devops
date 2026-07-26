const API_BASE = (process.env.NEXT_PUBLIC_API_BASE || '').replace(/\/$/, '')

// Fetch a client's structured site-data from the FastAPI backend.
// `fresh` bypasses the fetch cache (used by /choose previews right after uploads).
export async function getSiteData(clientId, layout, fresh = false) {
  const q = layout ? `?layout=${encodeURIComponent(layout)}` : ''
  const res = await fetch(`${API_BASE}/clients/${clientId}/site-data${q}`, {
    ...(fresh ? { cache: 'no-store' } : { next: { revalidate: 300 } }), // ISR: fresh every 5 min
  })
  if (!res.ok) throw new Error(`site-data ${res.status}`)
  return res.json()
}
