import s from './Bento.module.css'

export default function Bento({ data: d }) {
  const tel = `tel:+${d.PHONE_INTL}`
  const g = d.gallery || []
  return (
    <div className={s.root}>
      <nav className={s.nav}>
        <span className={s.logo}>{d.NAME}</span>
        <a href={tel} className={s.navCall}>📞 {d.PHONE}</a>
      </nav>

      <div className={s.grid}>
        <a href="#" className={`${s.tile} ${s.hero}`}>
          <img src={d.HERO_IMAGE} alt={`${d.NAME} — ${d.TRADE}`} />
          <div className={s.heroTxt}>
            <span className={s.kicker}>{d.KICKER}</span>
            <h1>{d.NAME}</h1>
          </div>
        </a>

        <div className={`${s.tile} ${s.intro}`}>
          <p>{d.TAGLINE}</p>
        </div>

        <a href={tel} className={`${s.tile} ${s.callTile}`}>
          <span className={s.kicker} style={{ color: 'rgba(255,255,255,.8)' }}>Κάλεσε τώρα</span>
          <strong>{d.PHONE}</strong>
          <span className={s.small}>{d.HOURS}</span>
        </a>

        {d.services?.slice(0, 4).map((sv, i) => (
          <div key={i} className={`${s.tile} ${s.svc}`}>
            <span className={s.num}>{sv.num}</span>
            <h3>{sv.title}</h3>
            <p>{sv.desc}</p>
          </div>
        ))}

        {g.slice(0, 4).map((it, i) => (
          <figure key={i} className={`${s.tile} ${s.photo} ${i === 0 ? s.photoWide : ''}`}>
            <img src={it.image} alt={it.title} loading="lazy" />
            <figcaption>{it.title}</figcaption>
          </figure>
        ))}

        <div className={`${s.tile} ${s.story}`}>
          <span className={s.kicker}>Ποιοι είμαστε</span>
          <h2>{d.STORY_TITLE}</h2>
          {d.story?.map((p, i) => <p key={i}>{p.p}</p>)}
          <div className={s.sign}>— {d.NAME}</div>
        </div>

        <figure className={`${s.tile} ${s.photo}`}>
          <img src={d.STORY_IMAGE} alt={d.NAME} loading="lazy" />
        </figure>

        <div className={`${s.tile} ${s.areas}`}>
          <span className={s.kicker}>Περιοχές</span>
          <p>{d.AREAS}</p>
        </div>

        <a href={tel} className={`${s.tile} ${s.cta}`}>
          <h2>{d.CTA_TITLE}</h2>
          <span className={s.ctaBtn}>📞 {d.PHONE} →</span>
        </a>
      </div>

      <footer className={s.footer}>© {d.YEAR} {d.NAME} — {d.CITY} · Site από Vitrina</footer>
    </div>
  )
}
