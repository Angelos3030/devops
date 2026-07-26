import s from './Terra.module.css'
import Brand from './Brand'

// "Terra" — παραγωγοί (λάδι/μέλι/κρασί): γη & χαρτί kraft, ελιά, ζεστή Alegreya.
// Signature: η ετικέτα — τα προϊόντα παρουσιάζονται σαν ετικέτες φιάλης με
// σειρά παρτίδας, ό,τι πιο οικείο έχει ένας παραγωγός.
export default function Terra({ data: d }) {
  const tel = `tel:+${d.PHONE_INTL}`
  return (
    <div className={s.root}>
      <nav className={s.nav}>
        <Brand data={d} className={s.brand} />
        <span className={s.navArea}>{d.CITY}</span>
        <a href={tel} className={s.navCall}>Παραγγελία</a>
      </nav>

      <header id="top" className={s.hero}>
        <div className={s.heroText}>
          <span className={s.eyebrow}>{d.KICKER}</span>
          <h1 className={s.title}>{d.NAME}</h1>
          <p className={s.lede}>{d.TAGLINE}</p>
          <a href={tel} className={s.cta}>Παράγγειλε · {d.PHONE}</a>
        </div>
        {d.HERO_IMAGE && (
          <figure className={s.heroFig}>
            <img src={d.HERO_IMAGE} alt={`${d.NAME} — ${d.TRADE}`} />
          </figure>
        )}
      </header>

      <section id="products" className={s.labels}>
        <h2 className={s.secTitle}>Τα προϊόντα μας</h2>
        <div className={s.labelGrid}>
          {d.services?.map((sv, i) => (
            <div key={i} className={s.labelCard}>
              <span className={s.batch}>Παρτίδα {sv.num} · {d.YEAR}</span>
              <h3>{sv.title}</h3>
              <span className={s.rule} aria-hidden="true" />
              <p>{sv.desc}</p>
              <span className={s.origin}>{d.CITY} · Ελλάδα</span>
            </div>
          ))}
        </div>
      </section>

      <section id="land" className={s.land}>
        {d.gallery?.slice(0, 4).map((g, i) => (
          <figure key={i} className={s.plot}>
            <img src={g.image} alt={g.title} loading="lazy" />
            <figcaption>{g.title} — {g.sub}</figcaption>
          </figure>
        ))}
      </section>

      <section id="story" className={s.story}>
        <div className={s.storyIn}>
          <span className={s.eyebrowLight}>Η ιστορία της γης μας</span>
          <h2 className={s.storyTitle}>{d.STORY_TITLE}</h2>
          {d.story?.map((p, i) => <p key={i}>{p.p}</p>)}
          <span className={s.sig}>— {d.NAME}</span>
        </div>
      </section>

      <section id="contact" className={s.cta2}>
        <h2>{d.CTA_TITLE}</h2>
        <a href={tel} className={s.cta}>📞 {d.PHONE}</a>
        <p className={s.cta2Sub}>{d.HOURS} · {d.AREAS}</p>
      </section>

      <footer className={s.footer}>© {d.YEAR} {d.NAME} · {d.CITY} · Site από Vitrina</footer>
    </div>
  )
}
