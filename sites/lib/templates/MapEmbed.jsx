'use client'

import { useState } from 'react'
import s from './FindUs.module.css'

// Ο χάρτης της Google φορτώνει ΜΟΝΟ αν τον ζητήσει ο επισκέπτης.
//
// Ένα iframe της Google που φορτώνει μόνο του στέλνει IP και cookies στην Google
// πριν προλάβει ο επισκέπτης να πει κουβέντα — αυτό θέλει συγκατάθεση. Το
// click-to-load είναι η ίδια συγκατάθεση, χωρίς banner που χαλάει το site.
//
// Η διεύθυνση, το ωράριο και ο σύνδεσμος οδηγιών μένουν server-rendered στο
// FindUs, οπότε η Google τα διαβάζει κανονικά: δεν χάνουμε τίποτα σε SEO.
export default function MapEmbed({ embed, directions, title }) {
  const [show, setShow] = useState(false)

  if (show) {
    return (
      <iframe
        className={s.map}
        src={embed}
        title={title}
        loading="lazy"
        referrerPolicy="no-referrer-when-downgrade"
        allowFullScreen
      />
    )
  }

  return (
    <button type="button" className={s.mapHolder} onClick={() => setShow(true)}>
      <span className={s.pin} aria-hidden="true">📍</span>
      <span className={s.mapCta}>Δες τον χάρτη</span>
      <span className={s.mapNote}>
        Φορτώνει από την Google. Ή άνοιξε{' '}
        <a href={directions} target="_blank" rel="noreferrer"
           onClick={(e) => e.stopPropagation()}>
          κατευθείαν οδηγίες ↗
        </a>
      </span>
    </button>
  )
}
