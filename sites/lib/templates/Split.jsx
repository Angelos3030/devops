import s from './Split.module.css'

export default function Split({ data: d }) {
  const tel = `tel:+${d.PHONE_INTL}`
  return (
    <div className={s.shell}>
      <aside className={s.panel}>
        <div>
          <div className={s.kicker}>{d.KICKER}</div>
          <div className={s.brand}>{d.NAME}<em>.</em></div>
          <p className={s.tag}>{d.TAGLINE}</p>
        </div>
        <nav className={s.pnav}>
          <a href="#work">Έργα</a><a href="#services">Υπηρεσίες</a>
          <a href="#story">Ποιοι είμαστε</a><a href="#contact">Επικοινωνία</a>
        </nav>
        <div className={s.contact}>
          <a href={tel} className={s.phone}>📞 {d.PHONE}</a>
          <span>{d.AREAS}</span><span>{d.HOURS}</span>
        </div>
      </aside>

      <main className={s.content} id="top">
        <figure className={s.heroImg}>
          <img src={d.HERO_IMAGE} alt={`${d.NAME} — ${d.TRADE}`} />
          <figcaption>{d.TRADE} — {d.CITY}</figcaption>
        </figure>

        <section className={s.blk} id="services">
          <span className={s.eyebrow}>Υπηρεσίες</span><h2>Τι κάνουμε.</h2>
          {d.services?.map((sv, i) => (
            <a key={i} href={tel} className={s.svc}>
              <span className={s.n}>{sv.num}</span>
              <div><h3>{sv.title}</h3><p>{sv.desc}</p></div>
            </a>
          ))}
        </section>

        <section className={`${s.blk} ${s.tint}`} id="work">
          <span className={s.eyebrow}>Έργα</span><h2>Επιλογή από τη δουλειά μας.</h2>
          <div className={s.gal}>
            {d.gallery?.map((g, i) => (
              <figure key={i}><img src={g.image} alt={g.title} loading="lazy" /><figcaption>{g.title}</figcaption></figure>
            ))}
          </div>
        </section>

        <section className={`${s.blk} ${s.story}`} id="story">
          <span className={s.eyebrow}>Ποιοι είμαστε</span><h2>{d.STORY_TITLE}</h2>
          {d.story?.map((p, i) => <p key={i}>{p.p}</p>)}
          <div className={s.sign}>— {d.NAME}</div>
        </section>

        <section className={`${s.blk} ${s.ctaBlk}`} id="contact">
          <span className={s.eyebrow} style={{ color: 'var(--accent-soft)' }}>Ας ξεκινήσουμε</span>
          <h2>{d.CTA_TITLE}</h2>
          <p>Δωρεάν εκτίμηση — {d.AREAS}.</p>
          <a href={tel} className={s.btn}>📞 Κάλεσε {d.PHONE}</a>
        </section>

        <div className={`${s.blk} ${s.foot}`}>© {d.YEAR} {d.NAME} — {d.CITY} · Site από Vitrina</div>
      </main>
    </div>
  )
}
