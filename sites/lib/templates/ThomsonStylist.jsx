import s from './ThomsonStylist.module.css'
import Brand from './Brand'
import FindUs from './FindUs'

// "Thomson Stylist" — ΠΙΣΤΟ PORT.
//
// Πηγή: https://github.com/themefisher/thomson-bootstrap (επίσημο repo, όχι mirror)
// Άδεια: MIT — Themefisher. Βλ. licenses/THIRD-PARTY.md.
//
// Το πρωτότυπο σερβιρίστηκε τοπικά από το `theme/index.html` και φωτογραφήθηκε σε
// 1440/390 πριν γραφτεί κώδικας. Είναι portfolio ελεύθερου επαγγελματία σχεδιαστή.
//
// ΑΝΤΙΣΤΟΙΧΙΣΗ — ανεξάρτητος κομμωτής / hair artist, ΟΧΙ γενικό κατάστημα:
//   δήλωση σχεδιαστή  → τοποθέτηση του κομμωτή («Κάνω …»)
//   πλέγμα έργων      → πραγματική δουλειά μαλλιών
//   core services     → υπηρεσίες κόμμωσης
//   contact           → στοιχεία και τοποθεσία Vitrina
//
// Η δομή μένει ίδια: αριστερή δήλωση με τεράστια τυπογραφία και πολύ λευκό →
// πλέγμα εικόνων → «Υπηρεσίες.» με εικονίδια σε δύο σειρές → σκούρο footer.
//
// ΑΦΑΙΡΕΣΕΙΣ (ενότητες χωρίς αντίστοιχα δεδομένα Vitrina — τεκμηριωμένες
// αποκλίσεις πιστότητας, ΟΧΙ αντικατάσταση με νέες δομές):
//   • φίλτρα κατηγοριών έργων — δεν υπάρχει ταξινόμηση έργων στο data model
//   • blog (grid/sidebar/single) — δεν υπάρχει blog
//   • δευτερεύουσες σελίδες και dropdown menus — το Vitrina είναι μονοσέλιδο
// Καμία δεν αντικαταστάθηκε· η σειρά των υπολοίπων μένει ακριβώς ως έχει.

const ICONS = [
  'M4 5h16v14H4zM4 9h16',                                  // πλαίσιο
  'M4 18l6-8 4 5 3-4 3 7z',                                // εικόνα
  'M12 3v18M5 8l7-5 7 5',                                  // ψαλίδι/κατεύθυνση
  'M6 4h12l-1 16H7z',                                      // φιάλη
  'M12 4a6 6 0 016 6c0 4-6 10-6 10S6 14 6 10a6 6 0 016-6z', // σταγόνα
  'M4 12h16M9 6l-5 6 5 6',                                 // βέλος
]

export default function ThomsonStylist({ data: d }) {
  const tel = d.PHONE_INTL ? `tel:+${d.PHONE_INTL}` : ''
  const services = Array.isArray(d.services) ? d.services : []
  const gallery = (Array.isArray(d.gallery) ? d.gallery : []).filter((g) => g?.image)
  const story = Array.isArray(d.story) ? d.story.slice(0, 2) : []

  return (
    <div className={s.root}>
      <nav className={s.nav} aria-label="Κύρια πλοήγηση">
        <a href="#top" className={s.logo}><Brand data={d} className={s.brand} /></a>
        <div className={s.navLinks}>
          <a href="#top">Αρχική</a>
          <a href="#work">Δουλειά</a>
          <a href="#services">Υπηρεσίες</a>
          <a href="#find-us">Επικοινωνία</a>
        </div>
      </nav>

      {/* Η δήλωση του πρωτοτύπου: δύο γραμμές, η δεύτερη σε κόκκινο. Εδώ δηλώνει
          τι κάνει ο κομμωτής, όχι τι πουλάει ένα κατάστημα. */}
      <header id="top" className={s.hero}>
        <h1 className={s.heroTitle}>
          <span className={s.heroLine}>{d.HERO_LEAD || 'Κάνω'}</span>
          <span className={s.heroAccent}>{d.TRADE || d.NAME}</span>
        </h1>
        {(d.TAGLINE || d.INTRO) && <p className={s.heroLede}>{d.TAGLINE || d.INTRO}</p>}
        {tel && <a href={tel} className={s.heroCta}>{d.PRIMARY_CTA || 'Κλείσε ραντεβού'}</a>}
      </header>

      <main>
        {gallery.length > 0 && (
          <section id="work" className={s.work} aria-label={d.GALLERY_TITLE || 'Η δουλειά μου'}>
            <div className={s.workGrid}>
              {gallery.slice(0, 6).map((g, i) => (
                <figure key={i} className={s.workItem}>
                  <img src={g.image} alt={g.title || d.NAME} loading="lazy" />
                  {g.illustrative && <figcaption>Ενδεικτική εικόνα</figcaption>}
                </figure>
              ))}
            </div>
          </section>
        )}

        <section id="services" className={s.services}>
          <h2 className={s.secTitle}>{d.SERVICES_TITLE || 'Υπηρεσίες.'}</h2>
          {(story[0]?.p || d.INTRO) && <p className={s.secLede}>{story[0]?.p || d.INTRO}</p>}
          <div className={s.serviceGrid}>
            {services.map((sv, i) => (
              <article className={s.serviceItem} key={sv.title + i}>
                <span className={s.serviceIcon} aria-hidden="true">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                    <path d={ICONS[i % ICONS.length]} />
                  </svg>
                </span>
                <div>
                  <h3>{sv.title}</h3>
                  {sv.desc && <p>{sv.desc}</p>}
                </div>
              </article>
            ))}
          </div>
          {d.SERVICES_TOTAL > services.length && (
            <p className={s.more}>+ {d.SERVICES_TOTAL - services.length} ακόμη — ρώτησέ με</p>
          )}
        </section>

        {(story.length > 1 || d.STORY_TITLE) && (
          <section className={s.about}>
            <h2 className={s.secTitle}>{d.STORY_TITLE || 'Λίγα λόγια.'}</h2>
            {story.slice(1).map((p, i) => <p className={s.secLede} key={i}>{p.p}</p>)}
          </section>
        )}
      </main>

      <FindUs data={d} />

      <footer className={s.footer}>
        <p>© {d.YEAR} {[d.NAME, d.CITY].filter(Boolean).join(' · ')} · Site από Vitrina</p>
        <div className={s.footLinks}>
          {tel && <a href={tel}>{d.PHONE}</a>}
          {d.EMAIL && <a href={`mailto:${d.EMAIL}`}>{d.EMAIL}</a>}
        </div>
      </footer>
    </div>
  )
}
