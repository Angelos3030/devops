import { useEffect, useState, useCallback } from 'react'
import { supabase } from '../lib/supabase'
import { api, previewUrl } from '../lib/api'

const META = {
  studio: { label: 'Editorial', desc: 'Ζεστό, καλλιτεχνικό, με έμφαση στα έργα.' },
  commerce: { label: 'Conversion', desc: 'Φωτεινό, με κριτικές και δυνατά κουμπιά — φτιαγμένο να πουλάει.' },
  atelier: { label: 'Minimal', desc: 'Καθαρό, premium, με μεγάλες φωτογραφίες.' },
  bold: { label: 'Bold', desc: 'Ζωντανό, με έντονα χρώματα και χαρακτήρα.' },
}
const metaFor = (layout) => META[layout] || { label: layout.charAt(0).toUpperCase() + layout.slice(1), desc: '' }
// Render whatever variants the API returns (N designs), recommended first.
const orderVariants = (variants) =>
  [...variants].sort((a, b) => (b.recommended ? 1 : 0) - (a.recommended ? 1 : 0))

export default function Dashboard({ session }) {
  const email = session.user.email
  const [clients, setClients] = useState(null)
  const [active, setActive] = useState(null)
  const [designs, setDesigns] = useState(null)
  const [busy, setBusy] = useState('')
  const [error, setError] = useState('')

  const loadDesigns = useCallback(async (clientId) => {
    setDesigns(null)
    try {
      setDesigns(await api(`/clients/${clientId}/designs`))
    } catch (e) {
      setError('Δεν φόρτωσαν οι προτάσεις.')
    }
  }, [])

  useEffect(() => {
    ;(async () => {
      try {
        const { clients } = await api(`/clients/lookup?email=${encodeURIComponent(email)}`)
        setClients(clients)
        if (clients.length) {
          setActive(clients[0].id)
          loadDesigns(clients[0].id)
        }
      } catch (e) {
        setError('Δεν μπόρεσα να βρω την επιχείρησή σου.')
        setClients([])
      }
    })()
  }, [email, loadDesigns])

  async function approve(layout) {
    setBusy(layout)
    try {
      await api(`/clients/${active}/select-design`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ layout }),
      })
      await loadDesigns(active)
    } catch (e) {
      setError('Η επιλογή δεν αποθηκεύτηκε.')
    } finally {
      setBusy('')
    }
  }

  const logout = () => supabase.auth.signOut()
  const activeClient = clients?.find((c) => c.id === active)

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand"><span className="brand-mark sm">V</span> Vitrina</div>
        <div className="user">
          <span className="muted">{email}</span>
          <button className="btn-ghost sm" onClick={logout}>Έξοδος</button>
        </div>
      </header>

      <main className="page">
        {clients === null && <div className="loading"><span className="spinner" />Φόρτωση…</div>}

        {clients && clients.length === 0 && (
          <div className="empty">
            <h2>Δεν βρήκαμε επιχείρηση σε αυτό το email.</h2>
            <p className="muted">Αν μόλις έκανες εγγραφή, δοκίμασε ξανά σε λίγο ή επικοινώνησε μαζί μας.</p>
          </div>
        )}

        {activeClient && (
          <>
            <div className="page-head">
              <span className="eyebrow">Ο πίνακάς σου</span>
              <h1>{activeClient.name}</h1>
              <p className="muted">
                {activeClient.business_type} · {activeClient.city}
                {clients.length > 1 && (
                  <select className="switcher" value={active} onChange={(e) => { setActive(e.target.value); loadDesigns(e.target.value) }}>
                    {clients.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
                  </select>
                )}
              </p>
            </div>

            {designs?.deployed_url && (
              <div className="live-banner">
                ✅ Το site σου είναι live: <a href={designs.deployed_url} target="_blank" rel="noreferrer">{designs.deployed_url}</a>
              </div>
            )}

            <section className="designs-head">
              <h2>Διάλεξε το design σου</h2>
              <p className="muted">Ετοιμάσαμε πολλές προτάσεις. Δες τες και πάτα «Επιλογή» σε αυτή που σου αρέσει — αυτή ανεβάζουμε.</p>
            </section>

            {designs === null && <div className="loading"><span className="spinner" />Φόρτωση προτάσεων…</div>}

            {designs && (
              <div className="grid">
                {orderVariants(designs.variants || []).map((v) => {
                  const layout = v.layout
                  const m = metaFor(layout)
                  const chosen = designs.selected === layout
                  return (
                    <article key={layout} className={'card' + (chosen ? ' chosen' : '')}>
                      <div className="shot">
                        {chosen && <span className="badge sel">✓ Επιλεγμένο</span>}
                        {!chosen && v.recommended && <span className="badge rec">Προτεινόμενο</span>}
                        <iframe src={previewUrl(active, layout)} title={m.label} loading="lazy" scrolling="no" />
                      </div>
                      <div className="card-body">
                        <h3>{m.label}</h3>
                        <p className="muted">{m.desc}</p>
                        <div className="card-actions">
                          <a className="btn-ghost" href={previewUrl(active, layout)} target="_blank" rel="noreferrer">Άνοιξέ το ↗</a>
                          <button className="btn-primary" disabled={busy === layout || chosen} onClick={() => approve(layout)}>
                            {chosen ? '✓ Επιλεγμένο' : busy === layout ? 'Αποθήκευση…' : 'Επιλογή'}
                          </button>
                        </div>
                      </div>
                    </article>
                  )
                })}
              </div>
            )}
          </>
        )}

        {error && <div className="err-banner">{error}</div>}
      </main>
    </div>
  )
}
