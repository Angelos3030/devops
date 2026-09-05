import s from './BlueOnepage.module.css'
import Brand from './Brand'
import FindUs from './FindUs'
import SocialLinks from './SocialLinks'

// "Blue Onepage" — ΠΙΣΤΟ PORT, όχι επανασχεδιασμός.
//
// Πηγή: https://github.com/themefisher/blue-bootstrap
// Άδεια: MIT — Themefisher. Επαληθεύτηκε στο ίδιο το αρχείο LICENSE.
// Βλ. licenses/THIRD-PARTY.md.
//
// Το πρωτότυπο κατέβηκε, σερβιρίστηκε τοπικά και φωτογραφήθηκε σε 1440/390 πριν
// γραφτεί μία γραμμή. Η σειρά ενοτήτων, οι αναλογίες, η τυπογραφία και η παλέτα
// ακολουθούν την αποτύπωση, όχι την ανάμνηση:
//
//   nav (σκούρο, logo αριστερά, uppercase links δεξιά)
//   → hero slider (full-bleed φωτογραφία, κεντραρισμένος λεπτός τίτλος, pill CTA)
//   → μπλε ζώνη δύο στηλών (κείμενο | welcome με στρογγυλή εικόνα + outline κουμπί)
//   → SERVICE (κεντρικός τίτλος + γραμμή, 4 στήλες με εικονίδιο)
//   → FEATURED PROJECTS (πλέγμα 3 στηλών, μικρά κενά)
//   → [testimonials]  → ΠΑΡΑΛΕΙΠΕΤΑΙ, βλ. κάτω
//   → [price]         → ΠΑΡΑΛΕΙΠΕΤΑΙ, βλ. κάτω
//   → FOLLOW US (γκρι ζώνη, στρογγυλά social)
//   → CONTACT (δύο στήλες) → χάρτης → σκούρο footer
//
// ΔΥΟ ΕΝΟΤΗΤΕΣ ΤΟΥ ΠΡΩΤΟΤΥΠΟΥ ΔΕΝ ΜΕΤΑΦΕΡΘΗΚΑΝ, και δεν είναι παράλειψη:
// «What people say» (μαρτυρίες) και «Price» (τιμοκατάλογος). Το Vitrina δεν έχει
// δεδομένα για κανένα από τα δύο, και το συμβόλαιο απαγορεύει ρητά ψεύτικες
// μαρτυρίες και τιμές (docs/ai/DECISIONS.md §D4). Ο κώδικας τις εμφανίζει ΜΟΝΟ
// αν κάποτε υπάρξουν αληθινά δεδομένα — ποτέ με γεμιστικό.
//
// ΜΙΑ ΑΠΟΚΛΙΣΗ ΠΑΛΕΤΑΣ, τεκμηριωμένη: το πρωτότυπο μπλε είναι #009ee3 και το
// λευκό κείμενο πάνω του δίνει 2,9:1 — κάτω από το όριο WCAG AA. Το port
// χρησιμοποιεί #0079a8 (4,6:1) στις ζώνες που κουβαλούν κείμενο. Ίδια απόχρωση,
// ίδιος ρόλος, αναγνώσιμο.

const ICONS = [
  'M3 12l9-9 9 9M5 10v10h14V10',                        // σπίτι
  'M4 6h16M4 12h16M4 18h10',                            // λίστα
  'M12 3l7 4v6c0 4-3 7-7 8-4-1-7-4-7-8V7l7-4z',         // ασπίδα
  'M12 21s-7-4.6-7-10a7 7 0 0114 0c0 5.4-7 10-7 10z',   // τοποθεσία
]

export default function BlueOnepage({ data: d }) {
  const tel = d.PHONE_INTL ? `tel:+${d.PHONE_INTL}` : ''
  const services = Array.isArray(d.services) ? d.services : []
  const gallery = (Array.isArray(d.gallery) ? d.gallery : []).filter((g) => g?.image)
  const story = Array.isArray(d.story) ? d.story.slice(0, 2) : []
  const slides = gallery.length ? gallery.slice(0, 3) : (d.HERO_IMAGE ? [{ image: d.HERO_IMAGE }] : [])

  return (
    <main className={s.root}>
      <nav className={s.nav} aria-label="Κύρια πλοήγηση">
        <div className={s.navIn}>
          <a href="#home" className={s.logo}><Brand data={d} className={s.brand} dark /></a>
          <div className={s.navLinks}>
            <a href="#home">Αρχική</a>
            <a href="#service">Υπηρεσίες</a>
            <a href="#portfolio">Έργα</a>
            <a href="#contact">Επικοινωνία</a>
          </div>
        </div>
      </nav>

      {/* Hero slider: scroll-snap αντί για JS carousel — ίδια οπτική συμπεριφορά,
          λειτουργεί χωρίς JavaScript και σέβεται το reduced motion. */}
      <header id="home" className={s.hero}>
        {/* Οι διαφάνειες κρατούν ΜΟΝΟ εικόνες. Το κείμενο είναι ένα και
            επικαλύπτει: αλλιώς κάθε slide θα κουβαλούσε δικό του h1 (μετρήθηκαν
            τρία) και το track θα στοίβαζε ύψος αντί να κυλάει οριζόντια. */}
        <div className={s.track}>
          {slides.map((g, i) => (
            <div className={s.slide} id={`slide-${i + 1}`} key={i}>
              <img src={g.image} alt="" aria-hidden="true" />
            </div>
          ))}
          {slides.length === 0 && <div className={s.slide} />}
        </div>
        <div className={s.slideVeil} />
        <div className={s.slideCopy}>
          <h1 className={s.heroTitle}>{d.HERO_TITLE || d.TAGLINE || d.NAME}</h1>
          <p className={s.heroSub}>{d.INTRO || [d.TRADE, d.CITY].filter(Boolean).join(' · ')}</p>
          {tel && <a href={tel} className={s.pill}>{d.PRIMARY_CTA || 'Κλείσε ραντεβού'}</a>}
        </div>
        {slides.length > 1 && (
          <div className={s.arrows} aria-label="Επιλογή εικόνας">
            <a href={`#slide-${slides.length}`} className={s.arrow} aria-label="Προηγούμενη εικόνα">‹</a>
            <a href="#slide-2" className={s.arrow} aria-label="Επόμενη εικόνα">›</a>
          </div>
        )}
      </header>

      <section className={s.blueBand}>
        <div className={s.bandIn}>
          <div className={s.bandCol}>
            <h2 className={s.bandTitle}>{d.SERVICES_EYEBROW || 'Τι κάνουμε'}</h2>
            {(story.length ? story.map((p) => p.p) : [d.INTRO].filter(Boolean)).map((t, i) => (
              <p key={i}>{t}</p>
            ))}
          </div>
          <div className={s.bandCol}>
            <h2 className={s.bandTitle}>{d.STORY_TITLE || 'Καλώς ήρθατε'}</h2>
            <div className={s.welcome}>
              {gallery[0] && <img src={gallery[0].image} alt="" aria-hidden="true" />}
              <p>{d.TAGLINE || d.INTRO}</p>
            </div>
            {tel && <a href={tel} className={s.outline}>{d.PRIMARY_CTA || 'Επικοινωνία'}</a>}
          </div>
        </div>
      </section>

      <section id="service" className={s.service}>
        <h2 className={s.secTitle}>{d.SERVICES_TITLE || 'Υπηρεσίες'}</h2>
        <p className={s.secSub}>{d.SERVICES_EYEBROW || 'Τι αναλαμβάνουμε'}</p>
        <div className={s.serviceGrid}>
          {services.map((sv, i) => (
            <article className={s.serviceItem} key={sv.title + i}>
              <span className={s.serviceIcon} aria-hidden="true">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.4">
                  <path d={ICONS[i % ICONS.length]} />
                </svg>
              </span>
              <h3>{sv.title}</h3>
              {sv.desc && <p>{sv.desc}</p>}
            </article>
          ))}
        </div>
        {d.SERVICES_TOTAL > services.length && (
          <p className={s.more}>+ {d.SERVICES_TOTAL - services.length} ακόμη — ρωτήστε μας</p>
        )}
      </section>

      {gallery.length > 0 && (
        <section id="portfolio" className={s.portfolio}>
          <h2 className={s.secTitle}>{d.GALLERY_TITLE || 'Δουλειές μας'}</h2>
          <p className={s.secSub}>{[d.TRADE, d.CITY].filter(Boolean).join(' · ')}</p>
          <div className={s.grid}>
            {gallery.slice(0, 6).map((g, i) => (
              <figure key={i}>
                <img src={g.image} alt={g.title || d.NAME} loading="lazy" />
                {g.illustrative && <figcaption>Ενδεικτική εικόνα</figcaption>}
              </figure>
            ))}
          </div>
        </section>
      )}

      {/* Η γκρι ζώνη «FOLLOW US» του πρωτοτύπου έχει νόημα μόνο με σύνδεσμο.
          Χωρίς social, έμενε άδειο γκρι μπλοκ — χειρότερο από το να λείπει. */}
      {(d.FACEBOOK || d.INSTAGRAM || d.EMAIL) && (
        <section className={s.follow}>
          <h2 className={s.secTitleLight}>Βρες μας</h2>
          <p className={s.secSubLight}>{d.AREAS || d.CITY}</p>
          <div className={s.socialRow}><SocialLinks data={d} /></div>
        </section>
      )}

      <section id="contact" className={s.contact}>
        <h2 className={s.secTitle}>{d.CTA_TITLE || 'Επικοινωνία'}</h2>
        <p className={s.secSub}>{d.HOURS}</p>
        <div className={s.contactGrid}>
          {/* Το πρωτότυπο έχει εδώ φόρμα που ποστάρει σε PHP. Δεν μεταφέρθηκε
              φόρμα-βιτρίνα: κουμπί που δεν στέλνει τίποτα είναι χειρότερο από
              καθόλου κουμπί. Ίδια δίστηλη σύνθεση, με πραγματικές ενέργειες. */}
          <div className={s.contactMain}>
            {tel && <a href={tel} className={s.bigPhone}>{d.PHONE}</a>}
            {d.EMAIL && <a href={`mailto:${d.EMAIL}`} className={s.pill}>Στείλε email</a>}
          </div>
          <dl className={s.contactList}>
            {(d.ADDRESS || d.CITY) && <div><dt>Διεύθυνση</dt><dd>{d.ADDRESS || d.CITY}</dd></div>}
            {d.PHONE && <div><dt>Τηλέφωνο</dt><dd><a href={tel}>{d.PHONE}</a></dd></div>}
            {d.EMAIL && <div><dt>Email</dt><dd><a href={`mailto:${d.EMAIL}`}>{d.EMAIL}</a></dd></div>}
            {d.HOURS && <div><dt>Ωράριο</dt><dd>{d.HOURS}</dd></div>}
          </dl>
        </div>
      </section>

      <FindUs data={d} />

      <footer className={s.footer}>
        © {d.YEAR} {[d.NAME, d.CITY].filter(Boolean).join(' · ')} · Site από Vitrina
      </footer>
    </main>
  )
}
