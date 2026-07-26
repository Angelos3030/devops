import s from './Runway.module.css'
import Brand from './Brand'

// "Runway" — high-fashion editorial για κομμωτήρια/beauty: B&W φωτογραφία που
// «ανάβει» σε χρώμα στο hover, oversized italic display, μία κοφτερή fuchsia.
// Signature: το runway — οριζόντια λωρίδα έργων με scroll-snap, σαν πασαρέλα.
export default function Runway({ data: d }) {
  const tel = `tel:+${d.PHONE_INTL}`
  return (
    <div className={s.root}>
      <nav className={s.nav}>
        <Brand data={d} className={s.brand} />
        <span className={s.navCity}>{d.CITY}</span>
        <a href={tel} className={s.navCall}>Ραντεβού</a>
      </nav>

      <header id="top" className={s.hero}>
        <h1 className={s.title}>
          <span className={s.titleLine}>{d.NAME}</span>
          <em className={s.titleWord}>{d.HERO_WORD}</em>
        </h1>
        {d.HERO_IMAGE && (
          <figure className={s.heroFig}>
            <img src={d.HERO_IMAGE} alt={`${d.NAME} — ${d.TRADE}`} />
          </figure>
        )}
        <p className={s.lede}>{d.TAGLINE}</p>
        <a href={tel} className={s.cta}>Κλείσε ραντεβού · {d.PHONE}</a>
      </header>

      <section id="services" className={s.svc}>
        {d.services?.map((sv, i) => (
          <a key={i} href={tel} className={s.svcRow}>
            <span className={s.svcNum}>{sv.num}</span>
            <span className={s.svcName}>{sv.title}</span>
            <span className={s.svcDesc}>{sv.desc}</span>
          </a>
        ))}
      </section>

      <section id="work" className={s.runwayWrap}>
        <div className={s.runwayHead}>
          <h2>Δουλειές μας</h2>
          <span className={s.hint}>σύρε →</span>
        </div>
        <div className={s.runway}>
          {d.gallery?.map((g, i) => (
            <figure key={i} className={s.look}>
              <img src={g.image} alt={g.title} loading="lazy" />
              <figcaption>
                <span className={s.lookNo}>{String(i + 1).padStart(2, '0')}</span>
                <span>{g.title}</span>
              </figcaption>
            </figure>
          ))}
        </div>
      </section>

      <section id="story" className={s.story}>
        <blockquote className={s.pull}>“{d.STORY_TITLE}”</blockquote>
        {d.story?.map((p, i) => <p key={i} className={s.storyP}>{p.p}</p>)}
        <span className={s.sig}>— {d.NAME}</span>
      </section>

      <section id="contact" className={s.cta2}>
        <h2 className={s.cta2Title}>{d.CTA_TITLE}</h2>
        <div className={s.cta2Meta}>
          <a href={tel} className={s.cta}>📞 {d.PHONE}</a>
          <span>{d.HOURS}</span>
          <span>{d.AREAS}</span>
        </div>
      </section>

      <footer className={s.footer}>© {d.YEAR} {d.NAME} · {d.CITY} · Site από Vitrina</footer>
    </div>
  )
}
