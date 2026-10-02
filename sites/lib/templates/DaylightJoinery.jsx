import s from './DaylightJoinery.module.css'
import Brand from './Brand'
import FindUs from './FindUs'

// Ξυλουργείο στο φως.
//
// ΓΙΑΤΙ ΥΠΑΡΧΕΙ. Ο ξυλουργός πουλάει δύο πράγματα ταυτόχρονα: τον χώρο που
// παρέδωσε ΚΑΙ τη λεπτομέρεια που δείχνει ότι ξέρει τη δουλειά — την ένωση, το
// νερό του ξύλου, τη σόκορο, το χέρι του συρταριού. Τα γενικά site κουζίνας
// δείχνουν μόνο το πρώτο, σε πλατιά πλάνα που μοιάζουν μεταξύ τους.
//
// Εδώ η ενότητα έργων εναλλάσσει ΣΚΟΠΙΜΑ κλίμακα: μεγάλο πλάνο χώρου, μετά
// κοντινό υλικού, ξανά χώρος. Αυτό είναι και η οδηγία του προφίλ στο
// docs/18-VERTICAL-DESIGN-INTELLIGENCE.md: «project-first, tactile craft,
// detail photography» με απαιτούμενα subjects `finished-work` + `material-detail`.
//
// ΦΩΣ, ΟΧΙ ΣΚΟΤΑΔΙ. Τα σκούρα theme κολακεύουν τη φωτογραφία στούντιο και
// τιμωρούν τη φωτογραφία κινητού — που είναι ό,τι έχει ένας τεχνίτης. Σε
// ανοιχτό φόντο, μια μέτρια λήψη διαβάζεται ως «πραγματικό έργο» αντί για
// «κακό στούντιο». Γι' αυτό η παλέτα είναι ασταρωμένο λευκό και βαφή δρυός.
//
// ΤΟ ΟΝΟΜΑ ΔΕΝ ΣΠΑΕΙ. Το h1 έχει `hyphens:manual`: μετρήθηκε «ΚΟΥΤΡΑ-ΚΗΣ» σε
// 390px, που διαβάζεται ως χαλασμένη σελίδα, όχι ως σχεδιαστική επιλογή.
export default function DaylightJoinery({ data: d }) {
  const tel = `tel:+${d.PHONE_INTL}`
  const services = Array.isArray(d.services) ? d.services : []
  const gallery = (Array.isArray(d.gallery) ? d.gallery : []).filter((x) => x?.image)
  const hero = d.HERO_IMAGE || gallery[0]?.image
  // Η πρώτη εικόνα πάει στο hero· τα έργα ξεκινούν από τη δεύτερη ώστε να μη
  // δείχνουμε δύο φορές το ίδιο πράγμα στην ίδια οθόνη.
  const work = hero === gallery[0]?.image ? gallery.slice(1) : gallery
  const areas = (d.AREAS || '').split(/[,·]/).map((x) => x.trim()).filter(Boolean)
  const steps = [
    ['Μέτρηση', 'Ερχόμαστε στον χώρο και μετράμε εμείς. Καμία έκπληξη στην τοποθέτηση.'],
    ['Σχέδιο', 'Βλέπεις το έπιπλο πριν κοπεί το πρώτο φύλλο.'],
    ['Κατασκευή', 'Στο εργαστήριο, με υλικά που διαλέγεις μαζί μας.'],
    ['Τοποθέτηση', 'Τελειώματα, ρυθμίσεις και καθαρός χώρος όταν φεύγουμε.'],
  ]

  return <div className={s.root}>
    <nav className={s.nav}>
      <a className={s.brandLink} href="#top"><Brand data={d} className={s.brand} /></a>
      <div className={s.links}>
        <a href="#services">Εργασίες</a><a href="#work">Έργα</a><a href="#process">Διαδικασία</a><a href="#find-us">Επικοινωνία</a>
      </div>
      <a className={s.quote} href={tel}>Ζήτησε προσφορά</a>
    </nav>

    <header id="top" className={`${s.hero} ${hero ? '' : s.heroBare}`}>
      {hero && <img className={s.heroImg} src={hero} alt={`${d.NAME} — ολοκληρωμένη κατασκευή, ${d.CITY}`} />}
      {hero && <span className={s.heroVeil} aria-hidden="true" />}
      <div className={s.heroCopy}>
        <p className={s.kicker}>{d.KICKER || [d.TRADE, d.CITY].filter(Boolean).join(' · ')}</p>
        <h1 className={s.heroTitle}>{d.HERO_TITLE || d.NAME}</h1>
        <p className={s.heroTag}>{d.TAGLINE || 'Κατασκευές στα μέτρα του χώρου σου.'}</p>
        <div className={s.heroActions}>
          <a className={s.primary} href={tel}>{d.PRIMARY_CTA || 'Ζήτησε προσφορά'}</a>
          <a className={s.secondary} href={tel}>{d.PHONE}</a>
        </div>
      </div>
    </header>

    <section className={s.proof} aria-label="Με μια ματιά">
      {[d.AREAS || d.CITY, d.HOURS, d.PHONE].filter(Boolean).map((x, i) =>
        <span key={i}>{x}</span>)}
    </section>

    <main>
      <section id="services" className={s.services}>
        <div className={s.sectionHead}>
          <p className={s.eyebrow}>Τι φτιάχνουμε</p>
          <h2>{d.SERVICES_TITLE || 'Έπιπλο που κουμπώνει στον χώρο.'}</h2>
          {d.INTRO && <p className={s.lede}>{d.INTRO}</p>}
        </div>
        <ol className={s.serviceList}>
          {services.map((x, i) => <li key={i}>
            <span className={s.num}>{String(i + 1).padStart(2, '0')}</span>
            <div><h3>{x.title}</h3>{x.desc && <p>{x.desc}</p>}</div>
            <a className={s.rowCta} href={tel} aria-label={`Προσφορά για ${x.title}`}>Προσφορά</a>
          </li>)}
        </ol>
      </section>

      {work.length > 0 && <section id="work" className={s.work}>
        <div className={s.sectionHead}>
          <p className={s.eyebrow}>Επιλεγμένα έργα</p>
          <h2>{d.GALLERY_TITLE || 'Ο χώρος, και η λεπτομέρεια που τον κρατά.'}</h2>
        </div>
        <div className={s.workGrid}>
          {work.slice(0, 7).map((x, i) => <figure key={i} className={i % 3 === 0 ? s.wide : s.tall}>
            <img src={x.image} alt={x.title || `${d.NAME} — έργο ${i + 1}`} loading="lazy" />
            {x.title && <figcaption>{x.title}</figcaption>}
          </figure>)}
        </div>
      </section>}

      <section id="process" className={s.process}>
        <div className={s.sectionHead}>
          <p className={s.eyebrow}>Πώς δουλεύουμε</p>
          <h2>Τέσσερα βήματα, καμία έκπληξη.</h2>
        </div>
        <ol className={s.steps}>
          {steps.map(([t, p], i) => <li key={i}>
            <span className={s.num}>{String(i + 1).padStart(2, '0')}</span>
            <h3>{t}</h3><p>{p}</p>
          </li>)}
        </ol>
      </section>

      {areas.length > 0 && <section className={s.areas}>
        <p className={s.eyebrow}>Περιοχές εξυπηρέτησης</p>
        <ul>{areas.map((a, i) => <li key={i}>{a}</li>)}</ul>
      </section>}

      <section className={s.band}>
        <h2>{d.CTA_TITLE || 'Έχεις χώρο που περιμένει;'}</h2>
        <p>Στείλε διαστάσεις ή μια φωτογραφία και σου λέμε τι γίνεται.</p>
        <a className={s.primary} href={tel}>{d.PHONE}</a>
      </section>

      <FindUs data={d} />
    </main>

    <footer className={s.footer}>
      <Brand data={d} className={s.brandFoot} />
      <span>{[d.TRADE, d.CITY].filter(Boolean).join(' · ')}</span>
      <span className={s.by}>Site από Vitrina</span>
    </footer>
  </div>
}
