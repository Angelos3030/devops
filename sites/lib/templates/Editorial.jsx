import s from './Editorial.module.css'

export default function Editorial({ data: d }) {
  const tel = `tel:+${d.PHONE_INTL}`
  return (
    <div className={s.root}>
      <nav className={s.nav}>
        <a href="#top" className={s.logo}>{d.NAME}<b>.</b></a>
        <div className={s.links}>
          <a href="#services">Υπηρεσίες</a><a href="#work">Έργα</a><a href="#story">Ποιοι είμαστε</a>
        </div>
        <a href={tel} className={s.navCall}>{d.PHONE}</a>
      </nav>

      <header id="top" className={s.hero}>
        <span className={s.kicker}>{d.KICKER}</span>
        <h1>{d.NAME} <em>με {d.HERO_WORD}.</em></h1>
        <p>{d.INTRO || d.TAGLINE}</p>
        <div className={s.heroActions}>
          <a href={tel} className={s.btn}>📞 {d.PHONE}</a>
          <a href="#work" className={s.btnLine}>Δες τα έργα</a>
        </div>
        <figure className={s.heroFig}>
          <img src={d.HERO_IMAGE} alt={`${d.NAME} — ${d.TRADE}`} />
        </figure>
      </header>

      <section id="services" className={s.section}>
        <div className={s.head}><span className={s.kicker}>01 — Υπηρεσίες</span><h2>Τι κάνουμε.</h2></div>
        <div className={s.idx}>
          {d.services?.map((sv, i) => (
            <a key={i} href={tel} className={s.idxRow}>
              <span className={s.num}>{sv.num}</span>
              <div><h3>{sv.title}</h3><p>{sv.desc}</p></div>
              <span className={s.arrow}>→</span>
            </a>
          ))}
        </div>
      </section>

      <section id="work" className={s.section}>
        <div className={s.head}><span className={s.kicker}>02 — Έργα</span><h2>Επιλογή από τη δουλειά μας.</h2></div>
        <div className={s.gal}>
          {d.gallery?.map((g, i) => (
            <figure key={i}><img src={g.image} alt={g.title} loading="lazy" /><figcaption>{g.title}</figcaption></figure>
          ))}
        </div>
      </section>

      <section id="story" className={`${s.section} ${s.story}`}>
        <figure className={s.storyMedia}><img src={d.STORY_IMAGE} alt={d.NAME} /></figure>
        <div>
          <span className={s.kicker}>03 — Ποιοι είμαστε</span>
          <h2>{d.STORY_TITLE}</h2>
          {d.story?.map((p, i) => <p key={i} className={s.storyP}>{p.p}</p>)}
          <div className={s.sign}>— {d.NAME}</div>
        </div>
      </section>

      <section id="contact" className={`${s.section} ${s.cta}`}>
        <span className={s.kicker}>Ας ξεκινήσουμε</span>
        <h2>{d.CTA_TITLE}</h2>
        <a href={tel} className={s.phone}>📞 {d.PHONE}</a>
        <p className={s.sub}>Δωρεάν εκτίμηση · {d.AREAS}</p>
      </section>

      <footer className={s.footer}>© {d.YEAR} {d.NAME} — {d.CITY} · Site από Vitrina</footer>
    </div>
  )
}
