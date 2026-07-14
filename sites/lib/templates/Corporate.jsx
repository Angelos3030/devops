import s from './Corporate.module.css'

export default function Corporate({ data: d }) {
  const tel = `tel:+${d.PHONE_INTL}`
  return (
    <div className={s.root}>
      <nav className={s.nav}>
        <a href="#top" className={s.logo}><span className={s.mark}>{d.INITIAL}</span>{d.NAME}</a>
        <div className={s.links}><a href="#services">Υπηρεσίες</a><a href="#work">Έργα</a><a href="#story">Εταιρεία</a><a href="#contact">Επικοινωνία</a></div>
        <a href={tel} className={s.navBtn}>Κάλεσε</a>
      </nav>

      <header id="top" className={s.hero}>
        <div className={s.heroTxt}>
          <span className={s.eyebrow}>{d.KICKER}</span>
          <h1>{d.NAME}</h1>
          <p>{d.TAGLINE}</p>
          <div className={s.actions}>
            <a href={tel} className={s.btn}>📞 {d.PHONE}</a>
            <a href="#services" className={s.btnLine}>Οι υπηρεσίες μας</a>
          </div>
        </div>
        <figure className={s.heroImg}><img src={d.HERO_IMAGE} alt={`${d.NAME} — ${d.TRADE}`} /></figure>
      </header>

      <div className={s.stats}>
        <div><b>Στα μέτρα</b><span>κάθε έργο</span></div>
        <div><b>Δωρεάν</b><span>εκτίμηση</span></div>
        <div><b>{d.CITY}</b><span>&amp; περιοχές</span></div>
        <div><b>Συνέπεια</b><span>στον χρόνο</span></div>
      </div>

      <section id="services" className={s.section}>
        <div className={s.head}><span className={s.eyebrow}>Υπηρεσίες</span><h2>Πώς μπορούμε να βοηθήσουμε.</h2></div>
        <div className={s.cards}>
          {d.services?.map((sv, i) => (
            <article key={i} className={s.card}>
              <span className={s.cnum}>{sv.num}</span>
              <h3>{sv.title}</h3><p>{sv.desc}</p>
            </article>
          ))}
        </div>
      </section>

      <section id="work" className={`${s.section} ${s.tint}`}>
        <div className={s.head}><span className={s.eyebrow}>Έργα</span><h2>Δείγμα από τη δουλειά μας.</h2></div>
        <div className={s.gal}>
          {d.gallery?.map((g, i) => (
            <figure key={i}><img src={g.image} alt={g.title} loading="lazy" /><figcaption>{g.title}</figcaption></figure>
          ))}
        </div>
      </section>

      <section id="story" className={`${s.section} ${s.story}`}>
        <figure className={s.storyImg}><img src={d.STORY_IMAGE} alt={d.NAME} /></figure>
        <div>
          <span className={s.eyebrow}>Η εταιρεία μας</span>
          <h2>{d.STORY_TITLE}</h2>
          {d.story?.map((p, i) => <p key={i}>{p.p}</p>)}
          <div className={s.sign}>— {d.NAME}</div>
        </div>
      </section>

      <section id="contact" className={s.ctaBand}>
        <h2>{d.CTA_TITLE}</h2>
        <p>Δωρεάν εκτίμηση — {d.AREAS}.</p>
        <a href={tel} className={s.btn}>📞 Κάλεσε {d.PHONE}</a>
      </section>

      <footer className={s.footer}>
        <a href="#top" className={s.logo}><span className={s.mark}>{d.INITIAL}</span>{d.NAME}</a>
        <span>© {d.YEAR} {d.NAME} — {d.CITY} · Site από Vitrina</span>
      </footer>
    </div>
  )
}
