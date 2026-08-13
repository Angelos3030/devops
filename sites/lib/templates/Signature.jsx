import s from './Signature.module.css'
import FindUs from './FindUs'
import Brand from './Brand'

// "Signature" — ΤΟ ΠΡΟΣΩΠΟ ΕΙΝΑΙ Η ΜΑΡΚΑ.
//
// Για τον μονοπρόσωπο επαγγελματία: λογιστής, ψυχολόγος, διαιτολόγος, coach,
// φωτογράφος, μεσίτης. Δεν είναι «γραφείο» — είναι ένας άνθρωπος. Τα υπόλοιπα
// αρχέτυπά μας πουλάνε εταιρεία (`marble`), εργασία (`canvas`) ή επείγον
// (`callout`). Εδώ το όνομα ΕΙΝΑΙ ο τίτλος και η υπογραφή.
//
// ΔΥΟ ΤΡΟΠΟΙ, ΙΔΙΑ ΑΞΙΑ:
//   portrait  — υπάρχει πραγματική φωτογραφία του επαγγελματία
//   no-photo  — ΜΟΝΟΓΡΑΜΜΑ + κάρτα ταυτότητας με ΑΛΗΘΙΝΑ στοιχεία
//
// Το no-photo δεν κρύβει τη στήλη· τη γεμίζει με πληροφορία που ο πελάτης
// έχει ούτως ή άλλως (τίτλος, περιοχές, ώρες, τηλέφωνο). Ποτέ stock πορτρέτο:
// ψεύτικο πρόσωπο σε site προσώπου είναι το χειρότερο δυνατό ψέμα.
//
// Οι υπηρεσίες είναι ΤΥΠΟΓΡΑΦΙΚΟ ευρετήριο, όχι πλέγμα με εικόνες — έτσι οι δύο
// τρόποι έχουν την ίδια δομή και το 2 ή το 9 δείχνουν εξίσου σκόπιμα.

const APPROACH = [
  { t: 'Μιλάμε πρώτα', d: 'Ακούω τι χρειάζεσαι πριν προτείνω οτιδήποτε.' },
  { t: 'Καθαρή εικόνα', d: 'Ξέρεις τι γίνεται, πότε και με τι κόστος.' },
  { t: 'Ένας συνομιλητής', d: 'Δεν αλλάζεις άτομο σε κάθε επικοινωνία.' },
]

export default function Signature({ data: d }) {
  const tel = d.PHONE_INTL ? `tel:+${d.PHONE_INTL}` : ''
  const services = Array.isArray(d.services) ? d.services.slice(0, 8) : []
  const story = Array.isArray(d.story) ? d.story.slice(0, 2) : []
  // Ενδεικτικές εικόνες δεν μπαίνουν ΕΔΩ: σε προσωπική μάρκα μια λωρίδα από
  // stock γραφεία διαβάζεται ως «δουλειά μου» — δηλαδή ως ψεύτικη απόδειξη.
  const gallery = Array.isArray(d.gallery)
    ? d.gallery.filter((g) => g?.image && !g.illustrative).slice(0, 3) : []
  // ΟΧΙ `d.HERO_IMAGE`: το mediaFallback βάζει πάντα κάτι εκεί, και το set
  // `professional` περιέχει stock φωτογραφία ανθρώπων. Πορτρέτο μόνο αν είναι
  // πραγματικά του πελάτη — αλλιώς μονόγραμμα.
  const portrait = d.HERO_IS_REAL ? d.HERO_IMAGE || '' : ''
  // Μόνο ό,τι υπάρχει πραγματικά. Κενό πεδίο δεν γίνεται γραμμή-φάντασμα.
  const facts = [
    ['Ειδικότητα', d.TRADE],
    ['Περιοχές', d.AREAS || d.CITY],
    ['Ώρες', d.HOURS],
  ].filter(([, v]) => v)

  return (
    <main className={`${s.root} ${portrait ? s.hasPortrait : s.noPortrait}`}>
      <nav className={s.nav}>
        <a className={s.brandLink} href="#top"><Brand data={d} /></a>
        {tel && <a className={s.navCall} href={tel}>{d.PHONE}</a>}
      </nav>

      <header className={s.hero} id="top">
        <div className={s.heroType}>
          <p className={s.eyebrow}>{[d.TRADE, d.CITY].filter(Boolean).join(' · ')}</p>
          <h1 className={s.name}>{d.NAME}</h1>
          {d.TAGLINE && <p className={s.lede}>{d.TAGLINE}</p>}
          <div className={s.actions}>
            {tel && <a className={s.primary} href={tel}>{d.PRIMARY_CTA || 'Κλείσε ραντεβού'}</a>}
            {d.EMAIL && <a className={s.secondary} href={`mailto:${d.EMAIL}`}>Στείλε μήνυμα</a>}
          </div>
        </div>

        {portrait ? (
          <figure className={s.portrait}>
            <img src={portrait} alt={`${d.NAME}${d.TRADE ? ' — ' + d.TRADE : ''}`} />
          </figure>
        ) : (
          // Η στήλη δεν αδειάζει: γίνεται κάρτα ταυτότητας.
          <aside className={s.card}>
            <span className={s.monogram} aria-hidden="true">{d.INITIAL}</span>
            <dl className={s.facts}>
              {facts.map(([k, v]) => (
                <div className={s.fact} key={k}><dt>{k}</dt><dd>{v}</dd></div>
              ))}
            </dl>
            {tel && <a className={s.cardCall} href={tel}>{d.PHONE}</a>}
          </aside>
        )}
      </header>

      <section className={s.services}>
        <div className={s.secHead}>
          <p className={s.eyebrowDark}>{d.SERVICES_EYEBROW || 'Τι κάνω'}</p>
          <h2 className={s.secTitle}>{d.SERVICES_TITLE || 'Πώς μπορώ να βοηθήσω'}</h2>
        </div>
        <ol className={s.index}>
          {services.map((svc, i) => (
            <li className={s.row} key={svc.title + i}>
              <span className={s.num}>{String(i + 1).padStart(2, '0')}</span>
              <h3 className={s.rowTitle}>{svc.title}</h3>
              {svc.desc && <p className={s.rowDesc}>{svc.desc}</p>}
            </li>
          ))}
        </ol>
      </section>

      <section className={s.approach}>
        {APPROACH.map((a) => (
          <article className={s.approachCard} key={a.t}>
            <h3>{a.t}</h3>
            <p>{a.d}</p>
          </article>
        ))}
      </section>

      {(story.length > 0 || d.INTRO) && (
        <section className={s.story}>
          <div className={s.storyIn}>
            <p className={s.eyebrowDeep}>{d.STORY_EYEBROW || 'Λίγα λόγια'}</p>
            <h2 className={s.storyTitle}>{d.STORY_TITLE || 'Ποιος είμαι'}</h2>
            {(story.length ? story.map((p) => p.p) : [d.INTRO]).map((text, i) => (
              <p className={s.storyP} key={i}>{text}</p>
            ))}
            {/* Η υπογραφή: το όνομα ξανά, με το χέρι του ίδιου ανθρώπου. */}
            <p className={s.sign}>{d.NAME}</p>
          </div>
        </section>
      )}

      {gallery.length > 0 && (
        <section className={s.strip}>
          {gallery.map((g, i) => (
            <figure className={s.shot} key={i}>
              <img src={g.image} alt={g.title || d.NAME} />
              {g.title && <figcaption>{g.title}</figcaption>}
            </figure>
          ))}
        </section>
      )}

      <section className={s.cta}>
        <h2 className={s.ctaTitle}>{d.CTA_TITLE || 'Ας τα πούμε.'}</h2>
        {tel && <a className={s.ctaCall} href={tel}>{d.PHONE}</a>}
        {d.HOURS && <p className={s.ctaSub}>{d.HOURS}</p>}
      </section>

      <FindUs data={d} />
      <footer className={s.footer}>© {d.YEAR} {[d.NAME, d.CITY].filter(Boolean).join(' · ')} · Site από Vitrina</footer>
    </main>
  )
}
