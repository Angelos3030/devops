'use client'

import { useMemo, useRef, useState } from 'react'
import { checkServiceArea, createBookingAction, inventoryAvailability } from './providers'
import { priceLabel } from './contracts'
import s from './CapabilityWidgets.module.css'

export function ServiceAreaChecker({ config, services }) {
  const [postcode, setPostcode] = useState('')
  const [service, setService] = useState(services[0]?.id || '')
  const [preferredDate, setPreferredDate] = useState('')
  const [result, setResult] = useState(null)
  return <section className={s.qualifier} aria-labelledby="area-title">
    <div><span className={s.kicker}>Άμεσος έλεγχος</span><h2 id="area-title">Μπορούμε να έρθουμε σε εσένα;</h2><p>Ένας γρήγορος έλεγχος, χωρίς εγγραφή.</p></div>
    <form onSubmit={(e) => { e.preventDefault(); setResult(checkServiceArea(config, { postcode, service, preferredDate })) }}>
      <label>Τ.Κ.<input inputMode="numeric" value={postcode} onChange={(e) => setPostcode(e.target.value)} placeholder="π.χ. 153 44" required /></label>
      <label>Υπηρεσία<select value={service} onChange={(e) => setService(e.target.value)}>{services.map((x) => <option key={x.id} value={x.id}>{x.name}</option>)}</select></label>
      <label>Προτιμώμενη ημέρα<input type="date" value={preferredDate} onChange={(e) => setPreferredDate(e.target.value)} /></label>
      <button type="submit">Έλεγχος διαθεσιμότητας</button>
    </form>
    {result && <div className={s.result} data-status={result.status} role="status"><strong>{result.message}</strong><span>{result.nextAvailable || result.detail}</span></div>}
  </section>
}

export function PriceBoard({ services, booking }) {
  const categories = ['Όλα', ...new Set(services.map((x) => x.category))]
  const [active, setActive] = useState('Όλα')
  const visible = active === 'Όλα' ? services : services.filter((x) => x.category === active)
  return <section className={s.board} aria-labelledby="prices-title"><header><span className={s.kicker}>Καθαρή τιμολόγηση</span><h2 id="prices-title">Υπηρεσίες, χρόνος, κόστος.</h2></header>
    <div className={s.filters} aria-label="Κατηγορίες">{categories.map((x) => <button key={x} aria-pressed={active === x} onClick={() => setActive(x)}>{x}</button>)}</div>
    <div className={s.rows}>{visible.map((x) => { const action = createBookingAction(booking, x); return <article key={x.id}><div><small>{x.category}</small><h3>{x.name}</h3><p>{x.shortDescription}</p></div><span>{x.duration || 'Κατόπιν συνεννόησης'}</span><strong>{priceLabel(x)}</strong><button disabled={action.kind === 'disabled'}>{action.label}</button></article> })}</div>
  </section>
}

export function TreatmentCatalog({ services, booking }) {
  const [selected, setSelected] = useState(services[0] || null)
  if (!selected) return null
  const action = createBookingAction(booking, selected)
  return <section className={s.catalog} aria-labelledby="treatments-title"><div className={s.catalogNav}><span className={s.kicker}>Κατάλογος</span><h2 id="treatments-title">Βρες τη σωστή υπηρεσία.</h2>{services.map((x) => <button key={x.id} aria-pressed={selected.id === x.id} onClick={() => setSelected(x)}><span>{x.name}</span><b>{priceLabel(x)}</b></button>)}</div><article className={s.detail}><small>{selected.category}</small><h3>{selected.name}</h3><p>{selected.longDescription}</p><dl><div><dt>Διάρκεια</dt><dd>{selected.duration || 'Κατόπιν συνεννόησης'}</dd></div><div><dt>Τιμή</dt><dd>{priceLabel(selected)}</dd></div><div><dt>Διαθεσιμότητα</dt><dd>{selected.availabilityStatus}</dd></div></dl><button disabled={action.kind === 'disabled'}>{action.label}</button></article></section>
}

export function ServiceCarousel({ services }) {
  const [index, setIndex] = useState(0); const item = services[index] || services[0]
  const touchStart = useRef(null)
  if (!item) return null
  const move = (delta) => setIndex((index + delta + services.length) % services.length)
  return <section className={s.carousel} aria-roledescription="carousel" aria-label="Υπηρεσίες" onKeyDown={(e) => { if (e.key === 'ArrowRight') move(1); if (e.key === 'ArrowLeft') move(-1) }} onTouchStart={(e) => { touchStart.current = e.changedTouches[0].clientX }} onTouchEnd={(e) => { const start = touchStart.current; touchStart.current = null; if (start === null) return; const distance = e.changedTouches[0].clientX - start; if (Math.abs(distance) > 40) move(distance < 0 ? 1 : -1) }} tabIndex="0"><div className={s.visual}><span>{String(index + 1).padStart(2, '0')}</span><b>{item.category}</b></div><article><small>{index + 1} / {services.length}</small><h1>{item.name}</h1><p>{item.longDescription}</p><div className={s.carouselControls}><button onClick={() => move(-1)} aria-label="Προηγούμενη υπηρεσία">←</button><button onClick={() => move(1)} aria-label="Επόμενη υπηρεσία">→</button></div></article></section>
}

export function SpatialGridExplorer({ items, intro }) {
  const [selected, setSelected] = useState(null)
  return <section className={s.spatialGrid} aria-label="Έργα">
    {items.map((item, index) => <button className={s.spatialCard} key={`${item.title}-${index}`} onClick={() => setSelected({ ...item, index })} aria-haspopup="dialog">
      {item.image && <img src={item.image} alt="" />}
      <span>0{index + 1}</span><strong>{item.title}</strong><small>{item.sub}</small>
    </button>)}
    {selected && <div className={s.spatialDialog} role="dialog" aria-modal="true" aria-labelledby="spatial-dialog-title" onKeyDown={(e) => { if (e.key === 'Escape') setSelected(null) }}>
      <button className={s.spatialClose} onClick={() => setSelected(null)} aria-label="Κλείσιμο">×</button>
      <span>0{selected.index + 1} / {String(items.length).padStart(2, '0')}</span>
      <h2 id="spatial-dialog-title">{selected.title}</h2><p>{selected.desc || intro}</p>
    </div>}
  </section>
}

export function InventorySelector({ options }) {
  const available = useMemo(() => options.filter((x) => inventoryAvailability(x).selectable), [options])
  const [selected, setSelected] = useState(available[0] || options[0] || null)
  if (!selected) return null
  const state = inventoryAvailability(selected)
  return <section className={s.inventory} aria-labelledby="selector-title"><header><span className={s.kicker}>Ζωντανές επιλογές</span><h2 id="selector-title">Διάλεξε αυτό που σου ταιριάζει.</h2></header><div className={s.optionGrid}>{options.map((x) => { const a = inventoryAvailability(x); return <button key={x.id} disabled={!a.selectable} aria-pressed={selected.id === x.id} onClick={() => setSelected(x)}>{x.image && <img src={x.image} alt="" />}<span><b>{x.label}</b><small>{a.label}</small></span></button> })}</div><div className={s.selection} role="status"><div><small>Η επιλογή σου</small><strong>{selected.label}</strong><span>{state.label}{selected.leadTime ? ` · ${selected.leadTime}` : ''}</span></div><button disabled={!state.selectable}>{state.selectable ? 'Ζήτησε αυτή την επιλογή' : 'Ειδοποίησέ με'}</button></div></section>
}
