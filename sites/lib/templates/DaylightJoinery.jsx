import s from './DaylightJoinery.module.css'
import Brand from './Brand'
import FindUs from './FindUs'

// Ξυλουργείο — ψηφιδωτό πάνελ.
//
// ΤΟ ΠΛΕΓΜΑ ΕΙΝΑΙ ΜΕΤΡΗΜΕΝΟ, ΟΧΙ ΑΙΣΘΗΤΙΚΗ ΕΠΙΛΟΓΗ. Προέκυψε από σάρωση
// computed styles σε site του κλάδου (research/koutrakis-redesign-v3):
//   hero 100% → λευκή ζώνη → 60/40 → τέσσερις στήλες 25% → λωρίδα 30%×3
//   → 33/67 → μπεζ ζώνη με λωρίδες 24% → τρεις σχίσεις 50/50 → σκούρα ζώνη
// Τα πάνελ ακουμπούν μεταξύ τους: μηδέν περιθώρια σελίδας, μηδέν κενά,
// μηδέν border-radius. Το λευκό είναι ΠΑΝΕΛ, όχι φόντο γύρω από τα πάντα.
//
// ΓΙΑΤΙ ΔΥΟ ΠΡΟΗΓΟΥΜΕΝΕΣ ΑΠΟΠΕΙΡΕΣ ΑΠΕΤΥΧΑΝ: η μέτρηση διάβαζε μόνο `<img>`.
// Η αναφορά βάζει τις φωτογραφίες ως CSS background, οπότε «φαινόταν» λιτή με
// πολύ λευκό — και χτίστηκε δύο φορές κεντραρισμένο container με αέρα, που
// είναι το ακριβώς αντίθετο. Η σάρωση πλέον κοιτά ΚΑΘΕ στοιχείο με background.
//
// ΥΠΟΒΑΘΜΙΣΗ. Το πλέγμα θέλει ~14 εικόνες. Οι περισσότεροι πελάτες έχουν
// λιγότερες. Κάθε ζώνη ζητά όσες χρειάζεται με το `take()` και ΔΕΝ αποδίδεται
// αν δεν τις πάρει — αντί να μείνει τρύπα ή placeholder κουτί.
export default function DaylightJoinery({ data: d }) {
  const tel = `tel:+${d.PHONE_INTL}`
  const services = Array.isArray(d.services) ? d.services : []
  const pool = (Array.isArray(d.gallery) ? d.gallery : []).filter((x) => x?.image)
  let cursor = 0
  const take = (n) => {
    const got = pool.slice(cursor, cursor + n)
    if (got.length < n) return null          // ζώνη χωρίς αρκετό υλικό: δεν μπαίνει
    cursor += n
    return got
  }
  const alt = (x, i) => x.title || `${d.NAME} — έργο ${i + 1}`

  const hero = d.HERO_IMAGE || (take(1) || [])[0]?.image || pool[0]?.image
  const splitA = take(1)
  const strip3 = take(3)
  const splitB = take(1)
  const beige2 = take(2)
  const beige3 = take(3)
  const halves = [take(1), take(1), take(1)].filter(Boolean)
  const areas = (d.AREAS || '').split(/[,·]/).map((x) => x.trim()).filter(Boolean)
  const steps = [
    ['Μέτρηση', 'Ερχόμαστε στον χώρο και μετράμε εμείς.'],
    ['Σχέδιο', 'Βλέπεις το έπιπλο πριν κοπεί το πρώτο φύλλο.'],
    ['Κατασκευή', 'Στο εργαστήριο, με υλικά που διαλέγεις μαζί μας.'],
    ['Τοποθέτηση', 'Τελειώματα, ρυθμίσεις και καθαρός χώρος.'],
  ]
  const arrow = <span className={s.arrow} aria-hidden="true">→</span>

  const Split = ({ img, label, text, photoLeft, media, textw }) => (
    <section className={`${s.split} ${photoLeft ? s.photoLeft : s.photoRight}`}>
      <figure className={s[media]}>
        <img src={img.image} alt={img.title || `${d.NAME} — ${label}`} loading="lazy" />
      </figure>
      <div className={s[textw]}>
        <h2>{label}</h2>
        <p>{text}</p>
        <a className={s.arrowLink} href={tel} aria-label={`Ζήτησε προσφορά — ${label}`}>
          Ζήτησε προσφορά {arrow}
        </a>
      </div>
    </section>
  )

  return <div className={s.root}>
    <header className={`${s.hero} ${hero ? '' : s.heroBare}`} id="top">
      {hero && <img className={s.heroImg} src={hero}
        alt={`${d.NAME} — ολοκληρωμένη κατασκευή, ${d.CITY}`} />}
      <nav className={s.nav}>
        <a className={s.brandLink} href="#top"><Brand data={d} className={s.brand} /></a>
        <div className={s.navRight}>
          <span className={s.links}>
            <a href="#work">Έργα</a><a href="#services">Υπηρεσίες</a><a href="#find-us">Επικοινωνία</a>
          </span>
          <a className={s.navPhone} href={tel}>{d.PHONE}</a>
        </div>
      </nav>
      <a className={s.scroll} href="#intro" aria-label="Κύλισε στο περιεχόμενο">↓</a>
    </header>

    <main>
      <section id="intro" className={s.intro}>
        <h1 className={s.h1}>{d.HERO_TITLE
          || [d.TRADE, d.CITY].filter(Boolean).join(' στον ') || d.NAME}</h1>
        <p className={s.lede}>{d.TAGLINE
          || 'Σχεδιάζουμε και κατασκευάζουμε έπιπλα πάνω στον χώρο σου.'}</p>
      </section>

      {splitA && <Split img={splitA[0]} photoLeft media="media60" textw="text40"
        label={services[0]?.title || 'Εντοιχισμός κουζίνας'}
        text={services[0]?.desc || d.INTRO
          || 'Κουζίνα φτιαγμένη για τον δικό σου χώρο, όχι για κατάλογο.'} />}

      {/* Τέσσερις στήλες 25%, στα μετρημένα χρώματα. Δεν θέλουν φωτογραφία. */}
      <section id="process" className={s.steps}>
        {steps.map(([t, p], i) => <div key={i} className={`${s.step} ${s['step' + i]}`}>
          <h3>{t}</h3><p>{p}</p>
        </div>)}
      </section>

      {strip3 && <section id="work" className={s.strip}>
        {strip3.map((x, i) => <figure key={i} className={s.stripItem}>
          <figcaption>{x.title || services[i]?.title || 'Έργο'}</figcaption>
          <img src={x.image} alt={alt(x, i)} loading="lazy" />
        </figure>)}
      </section>}

      {splitB && <Split img={splitB[0]} photoLeft={false} media="media67" textw="text33"
        label={services[1]?.title || 'Ντουλάπες & αποθήκευση'}
        text={services[1]?.desc || 'Αποθήκευση που χωράει εκεί που δεν χωρούσε τίποτα.'} />}

      {(beige2 || beige3) && <section className={s.beige}>
        {beige2 && <div className={s.rowTwo}>
          {beige2.map((x, i) => <figure key={i} className={s.gItem}>
            <figcaption>{x.title || 'Έργο'}</figcaption>
            <img src={x.image} alt={alt(x, i)} loading="lazy" />
          </figure>)}
        </div>}
        {beige3 && <div className={s.rowThree}>
          {beige3.map((x, i) => <figure key={i} className={s.gItem}>
            <figcaption>{x.title || 'Έργο'}</figcaption>
            <img src={x.image} alt={alt(x, i)} loading="lazy" />
          </figure>)}
        </div>}
      </section>}

      {halves.map((g, i) => <Split key={i} img={g[0]} photoLeft={i % 2 === 0}
        media="media50" textw="text50"
        label={services[(i + 2) % Math.max(services.length, 1)]?.title || 'Ειδικές κατασκευές'}
        text={services[(i + 2) % Math.max(services.length, 1)]?.desc
          || 'Κατασκευή στα μέτρα του χώρου και της χρήσης.'} />)}

      <section className={s.band}>
        <h2>{d.CTA_TITLE || 'Μίλησέ μας για τον χώρο σου'}</h2>
        <p>Στείλε διαστάσεις ή μια φωτογραφία και σου λέμε τι γίνεται.</p>
        <a className={s.bandPhone} href={tel}>{d.PHONE}</a>
      </section>

      {services.length > 0 && <section id="services" className={s.services}>
        <ol>{services.map((x, i) => <li key={i}>
          <span className={s.num}>{String(i + 1).padStart(2, '0')}</span>
          <div><h3>{x.title}</h3>{x.desc && <p>{x.desc}</p>}</div>
          <a className={s.rowCta} href={tel} aria-label={`Προσφορά για ${x.title}`}>Προσφορά</a>
        </li>)}</ol>
      </section>}

      {areas.length > 0 && <section className={s.areas}>
        <p className={s.eyebrow}>Περιοχές εξυπηρέτησης</p>
        <ul>{areas.map((a, i) => <li key={i}>{a}</li>)}</ul>
      </section>}

      <FindUs data={d} />
    </main>

    <footer className={s.footer}>
      <Brand data={d} className={s.brandFoot} />
      <span>{[d.TRADE, d.CITY].filter(Boolean).join(' · ')}</span>
      <span className={s.by}>Site από Vitrina</span>
    </footer>
  </div>
}
