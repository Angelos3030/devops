'use client'
import { useEffect, useState } from 'react'
import { TEMPLATE_META } from '../../../lib/templates'
import s from './choose.module.css'

const API = (process.env.NEXT_PUBLIC_API_BASE || '').replace(/\/$/, '')
const DEMO_CARPENTER = ['canvas', 'runway', 'grid', 'forge', 'dispatch']

// Legacy static layouts (fallback όταν το backend δεν στέλνει smart-matched templates)
const LABELS = {
  studio: 'Editorial', commerce: 'Conversion', atelier: 'Minimal', bold: 'Bold',
  trust: 'Classic', noir: 'Noir', fresh: 'Fresh', warmth: 'Warm', coast: 'Coast',
}
const labelOf = (k) => TEMPLATE_META[k]?.label || LABELS[k] || k
const descOf = (k) => TEMPLATE_META[k]?.desc || ''

export default function Choose({ params }) {
  const client = params.client
  const isDemo = client === 'demo-carpenter'
  const [variants, setVariants] = useState(() => isDemo
    ? DEMO_CARPENTER.map((layout, i) => ({ layout, recommended: i === 0 }))
    : null)
  const [selected, setSelected] = useState(isDemo ? DEMO_CARPENTER[0] : null)
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState('')
  const [ver, setVer] = useState(0)          // cache-bust των previews μετά από upload
  const [nPhotos, setNPhotos] = useState(0)  // πόσες φωτο ανέβηκαν εδώ
  const [hasLogo, setHasLogo] = useState(false)
  const [uploading, setUploading] = useState('')

  useEffect(() => {
    if (isDemo) return
    let tries = 0
    const load = async () => {
      try {
        const r = await fetch(`${API}/clients/${client}/designs`)
        const d = await r.json()
        // Smart-match: το backend προτείνει premium templates για το επάγγελμά του.
        if (d.templates?.length) {
          const list = d.templates.map((layout, i) => ({ layout, recommended: i === 0 }))
          setVariants(list)
          setSelected(d.selected && d.templates.includes(d.selected) ? d.selected : list[0].layout)
          return
        }
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
  }, [client, isDemo])

  const siteHref = (layout) => isDemo
    ? `/preview/${layout}?biz=carpenter`
    : `/site/${client}?layout=${layout}${ver ? `&v=${ver}` : ''}`

  // Upload φωτο/logo ΜΕΤΑ το wow (τα previews ανανεώνονται με τις δικές του).
  async function uploadFiles(files, assetType) {
    if (!files?.length) return
    setUploading(assetType); setErr('')
    let ok = 0
    for (const file of Array.from(files).slice(0, 8)) {
      try {
        const fd = new FormData()
        fd.append('file', file)
        fd.append('asset_type', assetType)
        fd.append('rights_ok', 'true')
        const r = await fetch(`${API}/clients/${client}/upload`, { method: 'POST', body: fd })
        if (r.ok) ok++
      } catch (e) {}
    }
    setUploading('')
    if (ok) {
      if (assetType === 'logo') setHasLogo(true)
      else setNPhotos((n) => n + ok)
      setVer(Date.now()) // ξαναφόρτωσε τα previews με τις νέες φωτο
    } else {
      setErr('Το ανέβασμα δεν πέτυχε. Δοκίμασε ξανά (JPG/PNG έως 10MB).')
    }
  }

  async function checkout() {
    if (isDemo) return
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
              <iframe src={siteHref(v.layout)} title={v.layout} loading="lazy" scrolling="no" />
            </div>
            <div className={s.label}>
              {labelOf(v.layout)}
              {descOf(v.layout) && <span className={s.labelDesc}>{descOf(v.layout)}</span>}
            </div>
          </button>
        ))}
      </div>

      {nPhotos === 0 && (
        <p className={s.note}>Οι φωτογραφίες στα σχέδια είναι <strong>δείγμα</strong> — αντικαθίστανται αυτόματα με τις δικές σου.</p>
      )}

      <section className={s.own}>
        <h2>Κάνε το 100% δικό σου <span>(προαιρετικό — μπορείς και αργότερα)</span></h2>
        <div className={s.ownGrid}>
          <label className={s.drop}>
            <input type="file" accept="image/jpeg,image/png,image/webp" multiple hidden
              onChange={(e) => uploadFiles(e.target.files, 'photo')} />
            <span className={s.dropIcon}>📸</span>
            <strong>{nPhotos ? `${nPhotos} φωτογραφίες ανέβηκαν ✓` : 'Ανέβασε φωτο από τη δουλειά σου'}</strong>
            <span className={s.dropHint}>{uploading === 'photo' ? 'Ανεβαίνουν…' : 'Από το κινητό σου, έως 8 (JPG/PNG)'}</span>
          </label>
          <label className={s.drop}>
            <input type="file" accept="image/jpeg,image/png,image/webp,image/svg+xml" hidden
              onChange={(e) => uploadFiles(e.target.files, 'logo')} />
            <span className={s.dropIcon}>🏷️</span>
            <strong>{hasLogo ? 'Το λογότυπο ανέβηκε ✓' : 'Έχεις λογότυπο; Ανέβασέ το'}</strong>
            <span className={s.dropHint}>{uploading === 'logo' ? 'Ανεβαίνει…' : 'Αλλιώς φτιάχνουμε κομψό με το όνομά σου'}</span>
          </label>
        </div>
      </section>

      <div className={s.bar}>
        <a className={s.preview} href={siteHref(selected)} target="_blank" rel="noreferrer">Άνοιξε σε πλήρη οθόνη ↗</a>
        <button className={s.cta} onClick={checkout} disabled={busy || isDemo}>
          {isDemo ? 'Demo επιλογής πελάτη' : busy ? 'Σε πάμε στην πληρωμή…' : 'Συνέχεια — €14.99/μήνα · 1ος μήνας δωρεάν'}
        </button>
      </div>
      {err && <p className={s.errline}>{err}</p>}
    </div>
  )
}
