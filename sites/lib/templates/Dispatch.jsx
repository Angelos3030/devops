import s from './Dispatch.module.css'

// ── Dispatch ────────────────────────────────────────────────────────────────
// ΜΙΑ ΟΘΟΝΗ. ΜΗΔΕΝ ΣΚΡΟΛ.
//
// Κάθε άλλο μας template ρωτάει τον επισκέπτη «θες να μάθεις για εμάς;». Ο
// άνθρωπος που ψάχνει υδραυλικό στις 11 το βράδυ με σπασμένο σωλήνα δεν θέλει
// να μάθει τίποτα — θέλει να τηλεφωνήσει. Κάθε γραμμή κειμένου που πρέπει να
// προσπεράσει είναι εμπόδιο.
//
// Γι' αυτό εδώ δεν υπάρχει ιστορία, δεν υπάρχει γκαλερί, δεν υπάρχει σκρολ.
// Ήρωας της σελίδας είναι το ΤΗΛΕΦΩΝΟ, γραμμένο τόσο μεγάλα όσο το όνομα.
// Γύρω του μόνο ό,τι απαντά στις τρεις ερωτήσεις που έχει ήδη στο μυαλό του:
// «είναι ανοιχτά;», «έρχεται στην περιοχή μου;», «τι ακριβώς κάνει;».
//
// Η φωτογραφία της δουλειάς του γεμίζει την οθόνη και το πάνελ επιπλέει από
// πάνω σαν γυαλί: ο ιδιοκτήτης εντυπωσιάζεται όταν το πρωτοβλέπει, ο πελάτης
// του βρίσκει το τηλέφωνο σε δύο δευτερόλεπτα. Δεν χρειάζεται να διαλέξουμε.
export default function Dispatch({ data: d }) {
  const tel = `tel:+${d.PHONE_INTL}`
  const areas = String(d.AREAS || d.CITY || '').split(/[·,]/).map((a) => a.trim()).filter(Boolean)

  return (
    <div className={s.root}>
      {/* Η δουλειά του γεμίζει την οθόνη — αυτό είναι που εντυπωσιάζει. */}
      {d.HERO_IMAGE && (
        <div className={s.bg} aria-hidden="true">
          <img src={d.HERO_IMAGE} alt="" />
        </div>
      )}
      <div className={s.veil} aria-hidden="true" />

      <div className={s.panel}>
        <header className={s.head}>
          <span className={s.trade}>{d.TRADE}</span>
          <h1 className={s.name}>{d.NAME}</h1>
        </header>

        {/* Ο λόγος που υπάρχει η σελίδα. Τίποτα δεν του κλέβει χώρο. */}
        <a href={tel} className={s.dial}>
          <span className={s.dialLabel}>Κάλεσε τώρα</span>
          <span className={s.dialNum}>{d.PHONE}</span>
        </a>

        <dl className={s.facts}>
          <div className={s.fact}>
            <dt>Ωράριο</dt>
            <dd><i className={s.live} aria-hidden="true" />{d.HOURS}</dd>
          </div>
          <div className={s.fact}>
            <dt>Περιοχές</dt>
            <dd className={s.areas}>
              {areas.slice(0, 5).map((a, i) => <span key={i} className={s.chip}>{a}</span>)}
            </dd>
          </div>
        </dl>

        <ul className={s.jobs}>
          {d.services?.slice(0, 5).map((sv, i) => (
            <li key={i} className={s.job}>
              <span className={s.jobNo}>{String(i + 1).padStart(2, '0')}</span>
              <span className={s.jobName}>{sv.title}</span>
              <span className={s.jobDesc}>{sv.desc}</span>
            </li>
          ))}
        </ul>

        <footer className={s.foot}>
          <span>{d.TAGLINE}</span>
          <span className={s.by}>© {d.YEAR} {d.NAME} · Site από Vitrina</span>
        </footer>
      </div>
    </div>
  )
}
