import MapEmbed from './MapEmbed'
import s from './FindUs.module.css'

// «Πού θα μας βρεις» — χάρτης + διεύθυνση + οδηγίες + τηλέφωνο.
// Το Google Maps embed δεν χρειάζεται API key με αυτή τη μορφή. Φορτώνει μόνο
// μετά από κλικ του επισκέπτη — βλ. MapEmbed.jsx για το γιατί.
//
// Εμφανίζεται μόνο αν ξέρουμε πού είναι η επιχείρηση.
export default function FindUs({ data: d, dark = false }) {
  const query = [d.ADDRESS, d.CITY, 'Ελλάδα'].filter(Boolean).join(', ')
  const hasGeo = d.GEO_LAT && d.GEO_LNG
  if (!d.CITY && !d.ADDRESS) return null

  const point = hasGeo ? `${d.GEO_LAT},${d.GEO_LNG}` : query
  const embed = `https://www.google.com/maps?q=${encodeURIComponent(point)}&hl=el&z=15&output=embed`
  const directions = `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(point)}`
  const tel = `tel:+${d.PHONE_INTL}`

  return (
    <section id="find-us" className={`${s.wrap} ${dark ? s.dark : ''}`}>
      <div className={s.info}>
        <span className={s.eyebrow}>Πού θα μας βρεις</span>
        <h2 className={s.title}>{d.CITY}</h2>
        <address className={s.address}>
          {d.ADDRESS && <span>{d.ADDRESS}</span>}
          <span>{d.CITY}</span>
          {d.AREAS && <span className={s.areas}>Εξυπηρετούμε: {d.AREAS}</span>}
        </address>
        {d.HOURS && <p className={s.hours}>🕒 {d.HOURS}</p>}
        <div className={s.actions}>
          <a className={s.primary} href={directions} target="_blank" rel="noreferrer">
            Οδηγίες πρόσβασης ↗
          </a>
          <a className={s.secondary} href={tel}>📞 {d.PHONE}</a>
        </div>
        {d.GBP_URL && (
          <a className={s.gbp} href={d.GBP_URL} target="_blank" rel="noreferrer">
            Δες μας στο Google ↗
          </a>
        )}
      </div>
      <div className={s.mapBox}>
        <MapEmbed embed={embed} directions={directions}
                  title={`Χάρτης — ${d.NAME}, ${d.CITY}`} />
      </div>
    </section>
  )
}
