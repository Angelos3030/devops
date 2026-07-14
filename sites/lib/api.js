const API_BASE = (process.env.NEXT_PUBLIC_API_BASE || '').replace(/\/$/, '')

// Fetch a client's structured site-data from the FastAPI backend.
export async function getSiteData(clientId, layout) {
  const q = layout ? `?layout=${encodeURIComponent(layout)}` : ''
  const res = await fetch(`${API_BASE}/clients/${clientId}/site-data${q}`, {
    next: { revalidate: 300 }, // ISR: fresh every 5 min
  })
  if (!res.ok) throw new Error(`site-data ${res.status}`)
  return res.json()
}
