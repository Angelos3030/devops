import s from './Canvas.module.css'
import FindUs from './FindUs'

// ── Canvas (οικογένεια `project-canvas`) ────────────────────────────────────
// Για μάστορα που η δουλειά του ΦΑΙΝΕΤΑΙ: ξυλουργό, κουζίνες, ανακαινίσεις.
//
// Η διαφορά από τα υπόλοιπα templates δεν είναι χρωματική — είναι ότι εδώ οι
// υπηρεσίες ΔΕΝ είναι λίστα με κουτάκια. Κάθε δουλειά είναι ένα «έργο» με δική
// της φωτογραφία σε πλήρες πλάτος, αριθμημένο σαν κατάλογος εργαστηρίου. Ο
// επισκέπτης δεν διαβάζει τι κάνει· το βλέπει.
//
// Γι' αυτό είναι φωτεινό και αραιό: οι φωτογραφίες ξύλου θέλουν λευκό γύρω
// τους για να αναπνεύσουν. Σκούρο φόντο θα τις έπνιγε.
export default function Canvas({ data: d }) {
  const tel = `tel:+${d.PHONE_INTL}`
  const projects = d.gallery?.slice(0, 4) || []
  const rest = d.gallery?.slice(4) || []

  return (
    <div className={s.root}>
      <nav className={s.nav}>
        <span className={s.mark}>{d.NAME}</span>
        <span className={s.navMeta}>{d.KICKER}</span>
        <a href={tel} className={s.navCall}>{d.PHONE}</a>
      </nav>

      {/* Η δουλειά του, σε πλήρες πλάτος, πριν από κάθε λέξη. */}
      <header id="top" className={s.hero}>
        {d.HERO_IMAGE && (
          <figure className={s.heroFig}>
            <img src={d.HERO_IMAGE} alt={`${d.NAME} — ${d.TRADE}`} />
          </figure>
        )}
        <div className={s.heroText}>
          <h1 className={s.title}>{d.TAGLINE}</h1>
          <div className={s.heroMeta}>
            <span>{d.TRADE}</span>
            <span>{d.AREAS}</span>
          </div>
          <a href={tel} className={s.cta}>Ζήτα προσφορά · {d.PHONE}</a>
        </div>
      </header>

      {/* Κάθε υπηρεσία = έργο με εικόνα. Εναλλάξ αριστερά/δεξιά, ώστε το μάτι
          να μη «βαρεθεί» τη στήλη. */}
      <section id="services" className={s.works}>
        {d.services?.map((sv, i) => (
          <article key={i} className={s.work}>
            <div className={s.workImg}>
              {projects[i] && <img src={projects[i].image} alt={sv.title} loading="lazy" />}
            </div>
            <div className={s.workText}>
              <span className={s.workNo}>Έργο {String(i + 1).padStart(2, '0')}</span>
              <h2 className={s.workTitle}>{sv.title}</h2>
              <p className={s.workDesc}>{sv.desc}</p>
              {projects[i] && <span className={s.workWhere}>{projects[i].sub}</span>}
            </div>
          </article>
        ))}
      </section>

      {/* Λεπτομέρειες υλικών — μικρές, πυκνές, σαν δείγματα σε εργαστήριο. */}
      {rest.length > 0 && (
        <section id="work" className={s.details}>
          <span className={s.label}>Λεπτομέρειες</span>
          <div className={s.detailGrid}>
            {rest.map((g, i) => (
              <figure key={i} className={s.detail}>
                <img src={g.image} alt={g.title} loading="lazy" />
                <figcaption>{g.title}</figcaption>
              </figure>
            ))}
          </div>
        </section>
      )}

      <section id="story" className={s.story}>
        <div className={s.storyInner}>
          <span className={s.label}>Το εργαστήριο</span>
          <h2 className={s.storyTitle}>{d.STORY_TITLE}</h2>
          {d.story?.map((p, i) => <p key={i} className={s.storyP}>{p.p}</p>)}
          <span className={s.sign}>— {d.NAME}, {d.CITY}</span>
        </div>
        {d.STORY_IMAGE && (
          <figure className={s.storyFig}>
            <img src={d.STORY_IMAGE} alt={`${d.NAME} — το εργαστήριο`} loading="lazy" />
          </figure>
        )}
      </section>

      <section id="contact" className={s.close}>
        <h2 className={s.closeTitle}>{d.CTA_TITLE}</h2>
        <a href={tel} className={s.ctaBig}>{d.PHONE}</a>
        <span className={s.closeMeta}>{d.HOURS} · {d.AREAS}</span>
      </section>

      <FindUs data={d} />

      <footer className={s.footer}>
        <span>© {d.YEAR} {d.NAME}</span>
        <span className={s.by}>Site από Vitrina</span>
      </footer>
    </div>
  )
}
