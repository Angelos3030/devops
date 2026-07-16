'use client'
import { useEffect, useState } from 'react'
import s from './choose.module.css'

const API = (process.env.NEXT_PUBLIC_API_BASE || '').replace(/\/$/, '')

const LABELS = {
  studio: 'Editorial', commerce: 'Conversion', atelier: 'Minimal', bold: 'Bold',
  trust: 'Classic', noir: 'Noir', fresh: 'Fresh', warmth: 'Warm', coast: 'Coast',
}

export default function Choose({ params }) {
  const client = params.client
  const [variants, setVariants] = useState(null)
  const [selected, setSelected] = useState(null)
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState('')

  useEffect(() => {
    let tries = 0
    const load = async () => {
      try {
        const r = await fetch(`${API}/clients/${client}/designs`)
        const d = await r.json()
        if (d.variants?.length) {
          const rec = d.variants.find((v) => v.recommended)?.layout
          setVariants([...d.variants].sort((a, b) => (b.recommended ? 1 : 0) - (a.recommended ? 1 : 0)))
          setSelected(d.selected || rec || d.variants[0].layout)
          return
        }
      } catch (e) {}
      if (tries++ < 8) setTimeout(load, 2500) // designs generate in background
      else setErr('Τα σχέδιά σου ετοιμάζονται ακόμα. Ανανέωσε σε λίγο.')
    }
    load()
  }, [client])

  async function checkout() {
    setBusy(true); setErr('')
    try {
      await fetch(`${API}/clients/${client}/select-design`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ layout: selected }),
      })
      const r = await fetch(`${API}/create-checkout`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ client_id: client, plan: 'site' }),
      })
      const d = await r.json()
      if (d.checkout_url) window.location.href = d.checkout_url
      else throw new Error(d.detail || 'checkout')
    } catch (e) {
      setErr('Κάτι πήγε στραβά με την πληρωμή. Δοκίμασε ξανά ή γράψε μας στο hello@getvitrina.gr')
      setBusy(false)
    }
  }

  if (err && !variants) return <div className={s.center}>{err}</div>
  if (!variants) return <div className={s.center}><span className={s.spin} />Ετοιμάζουμε τα σχέδιά σου…</div>

  return (
    <div className={s.page}>
      <header className={s.head}>
        <span className={s.eyebrow}>Σχεδόν έτοιμο</span>
        <h1>Διάλεξε το design σου</h1>
        <p>Ετοίμασα {variants.length} σχέδια για την επιχείρησή σου. Πάτα σε αυτό που σου αρέσει.</p>
      </header>

      <div className={s.grid}>
        {variants.map((v) => (
          <button key={v.layout} className={`${s.card} ${selected === v.layout ? s.on : ''}`} onClick={() => setSelected(v.layout)}>
            <div className={s.shot}>
              {v.recommended && <span className={s.rec}>Προτεινόμενο</span>}
              {selected === v.layout && <span className={s.tick}>✓</span>}
              <iframe src={`/site/${client}?layout=${v.layout}`} title={v.layout} loading="lazy" scrolling="no" />
            </div>
            <div className={s.label}>{LABELS[v.layout] || v.layout}</div>
          </button>
        ))}
      </div>

      <div className={s.bar}>
        <a className={s.preview} href={`/site/${client}?layout=${selected}`} target="_blank" rel="noreferrer">Άνοιξε σε πλήρη οθόνη ↗</a>
        <button className={s.cta} onClick={checkout} disabled={busy}>
          {busy ? 'Σε πάμε στην πληρωμή…' : 'Συνέχεια — €14.99/μήνα · 1ος μήνας δωρεάν'}
        </button>
      </div>
      {err && <p className={s.errline}>{err}</p>}
    </div>
  )
}
