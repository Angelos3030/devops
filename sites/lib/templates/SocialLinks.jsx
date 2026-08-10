import s from './SocialLinks.module.css'

// Κοινά social/επικοινωνία για ΟΛΑ τα templates. Μπαίνει μέσα στο FindUs ώστε
// να μην χρειαστεί να αγγίξουμε 37 αρχεία — και ώστε ένα νέο δίκτυο αύριο να
// μπει σε ένα σημείο.
//
// Δείχνει μόνο ό,τι υπάρχει: ο πελάτης χωρίς Instagram δεν βλέπει άδειο κουτί.
// Τα URL έχουν ήδη κανονικοποιηθεί από το backend (_social) — εδώ δεν μαντεύουμε.
const ICONS = {
  facebook: 'M14 9h3V6h-3c-2.2 0-4 1.8-4 4v2H8v3h2v7h3v-7h3l1-3h-4v-2c0-.6.4-1 1-1z',
  instagram: 'M12 8.5a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7zM17.5 6.5h.01M4 7.5A3.5 3.5 0 0 1 7.5 4h9A3.5 3.5 0 0 1 20 7.5v9a3.5 3.5 0 0 1-3.5 3.5h-9A3.5 3.5 0 0 1 4 16.5v-9z',
  email: 'M3 7l9 6 9-6M3 6h18v12H3z',
}

export default function SocialLinks({ data: d, className = '' }) {
  const items = [
    d.FACEBOOK && { key: 'facebook', href: d.FACEBOOK, label: 'Facebook' },
    d.INSTAGRAM && { key: 'instagram', href: d.INSTAGRAM, label: 'Instagram' },
    d.EMAIL && { key: 'email', href: `mailto:${d.EMAIL}`, label: d.EMAIL },
  ].filter(Boolean)

  if (!items.length) return null

  return (
    <div className={`${s.row} ${className}`}>
      {items.map((it) => (
        <a key={it.key} href={it.href} className={s.link}
           {...(it.key === 'email' ? {} : { target: '_blank', rel: 'noopener noreferrer' })}
           aria-label={it.label}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7"
               strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d={ICONS[it.key]} />
          </svg>
          <span className={s.text}>{it.label}</span>
        </a>
      ))}
    </div>
  )
}
