import s from './BillysBarber.module.css'
import Brand from './Brand'
import FindUs from './FindUs'

// "Billy's Barber" — ΠΙΣΤΟ PORT, όχι επανασχεδιασμός.
//
// Πηγή: https://github.com/joayo13/barbershop · ζωντανό: https://billysbarber.netlify.app
// Άδεια: MIT — «Copyright (c) 2023 Jordan», επαληθεύτηκε στο αρχείο LICENSE.
//
// Οι τέσσερις έλεγχοι που ζητήθηκαν, πριν από κώδικα:
//   1. LICENSE υπάρχει και είναι MIT ......................... ΝΑΙ
//   2. Το design ανήκει στο ίδιο το project ................. ΝΑΙ — καμία τρίτη
//      πίστωση, κανένα μοτίβο μαθήματος, δικό του Tailwind σχέδιο
//   3. Είναι πραγματικό site κουρείου προς πελάτες .......... ΝΑΙ — υπηρεσίες,
//      τιμοκατάλογος, κρατήσεις, ομάδα, επικοινωνία
//   4. Επαγγελματικό επίπεδο ................................ ΝΑΙ — φωτογραφήθηκε
//      το ζωντανό site σε 1440/390 και κρίθηκε από την αποτύπωση
//
// ΤΟ ΥΠΟΓΡΑΦΟ ΤΟΥ ΠΡΩΤΟΤΥΠΟΥ που κρατήθηκε: ο τεράστιος ΚΑΤΑΚΟΡΥΦΟΣ κόκκινος
// τίτλος «About Us» στο αριστερό περιθώριο, το γκρι σώμα σελίδας (#d4d4d4 αντί
// για λευκό), οι σερίφ επικεφαλίδες σε κόκκινο #991b1b, η λωρίδα τριών εικόνων
// με βέλη, και ο δίστηλος κατάλογος υπηρεσιών με γραμμή ανά υπηρεσία.
//
// ΤΙΜΕΣ: το πρωτότυπο δείχνει «$45.00+» ανά υπηρεσία. Το Vitrina δεν έχει πεδίο
// τιμής και απαγορεύει εφευρεμένες τιμές (DECISIONS §D4). Ο δίστηλος κατάλογος
// διατηρείται· η στήλη τιμής μένει κενή μέχρι να υπάρξουν αληθινά δεδομένα.

export default function BillysBarber({ data: d }) {
  const tel = d.PHONE_INTL ? `tel:+${d.PHONE_INTL}` : ''
  const services = Array.isArray(d.services) ? d.services : []
  const gallery = (Array.isArray(d.gallery) ? d.gallery : []).filter((g) => g?.image)
  const story = Array.isArray(d.story) ? d.story.slice(0, 3) : []
  // Το πρωτότυπο χωρίζει «Barber Services» / «Salon Services». Ο χωρισμός
  // ακολουθεί τα δεδομένα του πελάτη, όχι σταθερές κατηγορίες.
  const half = Math.ceil(services.length / 2)
  const colA = services.slice(0, half)
  const colB = services.slice(half)
  const strip = gallery.slice(0, 3)

  return (
    <div className={s.root}>
      <nav className={s.nav} aria-label="Κύρια πλοήγηση">
        <a href="#top" className={s.logoBox}><Brand data={d} className={s.brand} dark /></a>
        <div className={s.navLinks}>
          <a href="#services">Υπηρεσίες</a>
          <a href="#about">Το κουρείο</a>
          <a href="#find-us">Επικοινωνία</a>
        </div>
      </nav>

      <header id="top" className={s.hero}>
        {d.HERO_IMAGE && <img className={s.heroImg} src={d.HERO_IMAGE} alt="" aria-hidden="true" />}
        <div className={s.heroVeil} />
        <div className={s.heroCopy}>
          <h1 className={s.heroTitle}>{d.HERO_TITLE || d.TAGLINE || d.NAME}</h1>
          {tel && <a href={tel} className={s.bookBtn}>{d.PRIMARY_CTA || 'Κλείσε ραντεβού'}</a>}
        </div>
      </header>

      <section className={s.titleBand}>
        <h2 className={s.bandTitle}>{[d.CITY, d.TRADE].filter(Boolean).join(' ') || d.NAME}</h2>
        {d.INTRO && <p className={s.bandSub}>{d.INTRO}</p>}
      </section>

      {strip.length > 0 && (
        <div className={s.strip}>
          {strip.map((g, i) => (
            <figure className={s.stripItem} key={i}>
              <img src={g.image} alt={g.title || d.NAME} loading="lazy" />
              {g.illustrative && <figcaption>Ενδεικτική εικόνα</figcaption>}
            </figure>
          ))}
        </div>
      )}

      <main>
        {/* Η υπογραφή του πρωτοτύπου: κατακόρυφος τίτλος στο περιθώριο. */}
        <section id="about" className={s.about}>
          <span className={s.vertical} aria-hidden="true">Το κουρείο</span>
          <div className={s.aboutText}>
            <h2 className={s.aboutTitle}>{d.STORY_TITLE || 'Ποιοι είμαστε'}</h2>
            <p className={s.aboutMeta}>{[d.CITY, d.TRADE].filter(Boolean).join(' | ')}</p>
            {(story.length ? story.map((p) => p.p) : [d.INTRO].filter(Boolean)).map((t, i) => (
              <p key={i}>{t}</p>
            ))}
          </div>
          {gallery[3] || gallery[0] ? (
            <figure className={s.aboutFig}>
              <img src={(gallery[3] || gallery[0]).image} alt={d.NAME} loading="lazy" />
            </figure>
          ) : null}
        </section>

        <section id="services" className={s.services}>
          <div className={s.serviceCol}>
            <h2 className={s.colTitle}>{d.SERVICES_TITLE || 'Υπηρεσίες'}</h2>
            <ul className={s.list}>
              {colA.map((sv, i) => (
                <li key={sv.title + i}>
                  <div className={s.listHead}><span>{sv.title}</span></div>
                  {sv.desc && <p>{sv.desc}</p>}
                </li>
              ))}
            </ul>
          </div>
          {colB.length > 0 && (
            <div className={s.serviceCol}>
              <h2 className={s.colTitle}>Ακόμη</h2>
              <ul className={s.list}>
                {colB.map((sv, i) => (
                  <li key={sv.title + i}>
                    <div className={s.listHead}><span>{sv.title}</span></div>
                    {sv.desc && <p>{sv.desc}</p>}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </section>

        {d.SERVICES_TOTAL > services.length && (
          <p className={s.more}>+ {d.SERVICES_TOTAL - services.length} ακόμη — ρώτησέ μας</p>
        )}
      </main>

      <FindUs data={d} />

      <footer className={s.footer}>
        <a href="#top" className={s.logoBox}><Brand data={d} className={s.brand} dark /></a>
        <div className={s.footLinks}>
          {tel && <a href={tel}>{d.PHONE}</a>}
          {d.EMAIL && <a href={`mailto:${d.EMAIL}`}>{d.EMAIL}</a>}
          {d.HOURS && <span>{d.HOURS}</span>}
          {(d.AREAS || d.CITY) && <span>{d.AREAS || d.CITY}</span>}
        </div>
        <p className={s.copy}>© {d.YEAR} {d.NAME} · Site από Vitrina</p>
      </footer>
    </div>
  )
}
