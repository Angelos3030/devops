import s from './Longform.module.css'
import Brand from './Brand'

export default function Longform({ data: d }) {
  const tel = `tel:+${d.PHONE_INTL}`
  const g = d.gallery || []
  return (
    <div className={s.root}>
      <nav className={s.nav}>
        <a href="#top" className={s.logo}><Brand data={d} /></a>
        <a href={tel} className={s.navCall}>{d.PHONE}</a>
      </nav>

      <article className={s.col} id="top">
        <header className={s.head}>
          <span className={s.kicker}>{d.KICKER}</span>
          <h1>{d.NAME}</h1>
          <p className={s.lede}>{d.TAGLINE}</p>
          <a href={tel} className={s.btn}>📞 {d.PHONE}</a>
        </header>
      </article>

      {g[0] && <figure className={s.full}><img src={g[0].image} alt={g[0].title} /><figcaption>{g[0].title}</figcaption></figure>}

      <article className={s.col}>
        <h2 id="services">Υπηρεσίες</h2>
        <ol className={s.svc}>
          {d.services?.map((sv, i) => (
            <li key={i}><a href={tel}><b>{sv.title}</b><span>{sv.desc}</span></a></li>
          ))}
        </ol>
      </article>

      {g[1] && <figure className={s.full}><img src={g[1].image} alt={g[1].title} /><figcaption>{g[1].title}</figcaption></figure>}

      <article className={s.col}>
        <h2 id="story">{d.STORY_TITLE}</h2>
        {d.story?.map((p, i) => <p key={i} className={i === 0 ? s.drop : ''}>{p.p}</p>)}
        <p className={s.sign}>— {d.NAME}</p>
      </article>

      <div className={s.thumbs}>
        {g.slice(2, 6).map((it, i) => (
          <figure key={i}><img src={it.image} alt={it.title} loading="lazy" /></figure>
        ))}
      </div>

      <article className={`${s.col} ${s.cta}`} id="contact">
        <h2>{d.CTA_TITLE}</h2>
        <p className={s.lede}>Δωρεάν εκτίμηση — {d.AREAS}.</p>
        <a href={tel} className={s.btn}>📞 Κάλεσε {d.PHONE}</a>
      </article>

      <footer className={s.footer}>© {d.YEAR} {d.NAME} — {d.CITY} · Site από Vitrina</footer>
    </div>
  )
}
