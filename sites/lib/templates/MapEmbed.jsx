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
      {/* Ο σύνδεσμος οδηγιών ΔΕΝ μπαίνει εδώ.
          Ήταν `<a>` μέσα σε `<button>` — μη έγκυρο HTML και ασάφεια κλικ: ο
          ίδιος στόχος αφής ανήκε σε δύο χειριστήρια. Μετρήθηκε στα 16px ύψος
          σε 43 themes, το συχνότερο ελάττωμα προσβασιμότητας της βιβλιοθήκης.
          Δεν χάνεται τίποτα: το FindUs έχει ήδη κανονικό κουμπί «Οδηγίες
          πρόσβασης ↗» με τον ίδιο προορισμό, λίγα εκατοστά πιο πάνω. */}
      <span className={s.mapNote}>Φορτώνει από την Google μόνο αν το ζητήσεις.</span>
    </button>
  )
}
