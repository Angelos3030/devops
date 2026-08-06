import s from './CallBar.module.css'

// Σταθερή μπάρα κλήσης — ΜΟΝΟ σε κινητό.
//
// Τα καλύτερα site εστίασης παγκοσμίως κρατάνε τη δράση μόνιμα μπροστά
// (παραγγελία, κράτηση) αντί να τη θάβουν σε ένα μενού. Για ελληνικό μαγαζί η
// δράση είναι μία και συγκεκριμένη: **το τηλέφωνο**. Ο πελάτης σκρολάρει στο
// κινητό, βλέπει μια φωτογραφία που του αρέσει, και το κουμπί κλήσης είναι
// ήδη κάτω από τον αντίχειρά του — δεν χρειάζεται να ψάξει.
//
// Στον υπολογιστή δεν εμφανίζεται: εκεί το τηλέφωνο φαίνεται στο πάνω μέρος
// και μια μπάρα θα έτρωγε χώρο χωρίς λόγο (κανείς δεν καλεί από desktop).
//
// Μπαίνει μία φορά, στο layout του site — όχι σε κάθε template ξεχωριστά.
export default function CallBar({ data: d }) {
  if (!d?.PHONE_INTL) return null
  const query = [d.ADDRESS, d.CITY, 'Ελλάδα'].filter(Boolean).join(', ')
  const point = d.GEO_LAT && d.GEO_LNG ? `${d.GEO_LAT},${d.GEO_LNG}` : query

  return (
    <>
      <div className={s.spacer} aria-hidden="true" />
    <div className={s.bar}>
      <a className={s.call} href={`tel:+${d.PHONE_INTL}`}>
        <svg className={s.icon} viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.24c1.1.37 2.3.57 3.5.57a1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.2.2 2.4.57 3.5a1 1 0 0 1-.25 1l-2.2 2.3Z"
                fill="currentColor"/>
        </svg>
        <span className={s.callText}>
          <strong>Κάλεσέ μας</strong>
          <span className={s.num}>{d.PHONE}</span>
        </span>
      </a>
      {(d.ADDRESS || d.CITY) && (
        <a className={s.dir}
           href={`https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(point)}`}
           target="_blank" rel="noreferrer">
          <svg className={s.pin} viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M12 21s7-5.4 7-11a7 7 0 1 0-14 0c0 5.6 7 11 7 11Z" stroke="currentColor" strokeWidth="1.8"/>
            <circle cx="12" cy="10" r="2.4" fill="currentColor"/>
          </svg>
          <span>Οδηγίες</span>
        </a>
      )}
    </div>
    </>
  )
}
