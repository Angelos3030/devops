import s from './Marble.module.css'
import FindUs from './FindUs'
import Brand from './Brand'

// "Marble" — minimal-luxe για δικηγόρους/ιατρούς/λογιστές: πορσελάνη, βαθύ ink,
// χρυσές hairlines. Signature: οι τομείς ως ευρετήριο κώδικα (I. II. III.) με
// ledger rules — δομή που κωδικοποιεί τάξη και ακρίβεια.
export default function Marble({ data: d }) {
  const tel = `tel:+${d.PHONE_INTL}`
  const roman = ['I', 'II', 'III', 'IV', 'V', 'VI']
  return (
    <div className={s.root}>
      <nav className={s.nav}>
        <a href="#top" className={s.brand}><Brand data={d} /></a>
        <div className={s.navLinks}>
          <a href="#index">{d.SERVICES_NAV || 'Υπηρεσίες'}</a>
          <a href="#ethos">Προσέγγιση</a>
          <a href="#contact">Επικοινωνία</a>
        </div>
        <a href={tel} className={s.navCall}>{d.PHONE}</a>
      </nav>

      <header id="top" className={s.hero}>
        <div className={s.heroText}>
          <span className={s.eyebrow}>{d.KICKER}</span>
          <h1 className={s.title}>{d.NAME}</h1>
          <p className={s.lede}>{d.TAGLINE}</p>
          <div className={s.heroRow}>
            <a href={tel} className={s.cta}>{d.PRIMARY_CTA || 'Κλείσε ραντεβού'}</a>
            <span className={s.hours}>{d.HOURS}</span>
          </div>
        </div>
        {d.HERO_IMAGE && (
          <figure className={s.heroFig}>
            <img src={d.HERO_IMAGE} alt={`${d.NAME} — ${d.TRADE}`} />
            <span className={s.heroRule} aria-hidden="true" />
          </figure>
        )}
      </header>

      <section id="index" className={s.index}>
        <header className={s.secHead}>
          <span className={s.eyebrow}>{d.SERVICES_EYEBROW || 'Ιατρικές υπηρεσίες'}</span>
          <h2>{d.SERVICES_TITLE || 'Πώς μπορούμε να βοηθήσουμε'}</h2>
        </header>
        <ol className={s.ledger}>
          {d.services?.map((sv, i) => (
            <li key={i} className={s.entry}>
              <span className={s.numeral}>{roman[i] || sv.num}.</span>
              <div className={s.entryBody}>
                <h3>{sv.title}</h3>
                <p>{sv.desc}</p>
              </div>
              <a href={tel} className={s.entryLink} aria-label={`Επικοινωνία για ${sv.title}`}>→</a>
            </li>
          ))}
        </ol>
      </section>

      <section id="ethos" className={s.ethos}>
        <div className={s.ethosInner}>
          <span className={s.eyebrowLight}>{d.STORY_EYEBROW || 'Η προσέγγισή μας'}</span>
          <blockquote className={s.pull}>{d.STORY_TITLE}</blockquote>
          <div className={s.ethosCols}>
            {d.story?.map((p, i) => <p key={i}>{p.p}</p>)}
          </div>
          <span className={s.sig}>{d.NAME} · {d.CITY}</span>
        </div>
      </section>

      {d.gallery?.length > 0 && (
        <section className={s.spaces}>
          {d.gallery.slice(0, 3).map((g, i) => (
            <figure key={i} className={s.space}>
              <img src={g.image} alt={g.title} loading="lazy" />
              <figcaption>{g.title}</figcaption>
            </figure>
          ))}
        </section>
      )}

      <section id="contact" className={s.close}>
        <span className={s.eyebrow}>{d.AREAS}</span>
        <h2 className={s.closeTitle}>{d.CTA_TITLE}</h2>
        <a href={tel} className={s.cta}>{d.PHONE}</a>
      </section>

      <FindUs data={d} />


      <footer className={s.footer}>
        <span>© {d.YEAR} {d.NAME}</span>
        <span>{d.CITY}</span>
        <span>Site από Vitrina</span>
      </footer>
    </div>
  )
}
