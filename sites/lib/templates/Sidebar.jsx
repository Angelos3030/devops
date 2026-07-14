import s from './Sidebar.module.css'

export default function Sidebar({ data: d }) {
  const tel = `tel:+${d.PHONE_INTL}`
  return (
    <div className={s.root}>
      <nav className={s.topnav}>
        <a href="#top" className={s.logo}><span className={s.mark}>{d.INITIAL}</span>{d.NAME}</a>
        <a href={tel} className={s.navCall}>📞 {d.PHONE}</a>
      </nav>

      <div className={s.layout}>
        <main className={s.main} id="top">
          <header className={s.hero}>
            <span className={s.eyebrow}>{d.KICKER}</span>
            <h1>{d.NAME}</h1>
            <p className={s.lede}>{d.TAGLINE}</p>
          </header>
          <figure className={s.heroImg}><img src={d.HERO_IMAGE} alt={`${d.NAME} — ${d.TRADE}`} /></figure>

          <section id="services" className={s.block}>
            <h2>Υπηρεσίες</h2>
            {d.services?.map((sv, i) => (
              <div key={i} className={s.svc}><span className={s.num}>{sv.num}</span><div><h3>{sv.title}</h3><p>{sv.desc}</p></div></div>
            ))}
          </section>

          <section id="work" className={s.block}>
            <h2>Έργα</h2>
            <div className={s.gal}>
              {d.gallery?.map((g, i) => (
                <figure key={i}><img src={g.image} alt={g.title} loading="lazy" /><figcaption>{g.title}</figcaption></figure>
              ))}
            </div>
          </section>

          <section id="story" className={s.block}>
            <h2>{d.STORY_TITLE}</h2>
            {d.story?.map((p, i) => <p key={i} className={s.para}>{p.p}</p>)}
            <div className={s.sign}>— {d.NAME}</div>
          </section>
        </main>

        <aside className={s.rail}>
          <div className={s.card}>
            <span className={s.eyebrow}>Επικοινωνία</span>
            <a href={tel} className={s.phone}>{d.PHONE}</a>
            <a href={tel} className={s.btn}>📞 Κάλεσε τώρα</a>
            <dl className={s.info}>
              <dt>Ώρες</dt><dd>{d.HOURS}</dd>
              <dt>Περιοχές</dt><dd>{d.AREAS}</dd>
              <dt>Έδρα</dt><dd>{d.CITY}</dd>
            </dl>
            <p className={s.note}>Δωρεάν εκτίμηση — χωρίς δέσμευση.</p>
          </div>
        </aside>
      </div>

      <footer className={s.footer}>© {d.YEAR} {d.NAME} — {d.CITY} · Site από Vitrina</footer>
    </div>
  )
}
