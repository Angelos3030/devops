import s from './Magazine.module.css'

export default function Magazine({ data: d }) {
  const tel = `tel:+${d.PHONE_INTL}`
  return (
    <div className={s.root}>
      <header className={s.masthead}>
        <div className={s.mtop}><span>{d.KICKER}</span><span>{d.CITY}</span><a href={tel}>{d.PHONE}</a></div>
        <h1 className={s.title}>{d.NAME}</h1>
        <div className={s.rule}><span>Est. — {d.TRADE}</span></div>
      </header>

      <section className={s.feature} id="top">
        <figure className={s.featImg}><img src={d.HERO_IMAGE} alt={`${d.NAME} — ${d.TRADE}`} /></figure>
        <div className={s.featTxt}>
          <span className={s.label}>Το θέμα μας</span>
          <h2>{d.TAGLINE}</h2>
          <p className={s.lead}>{d.INTRO || d.TAGLINE}</p>
          <a href={tel} className={s.btn}>📞 {d.PHONE}</a>
        </div>
      </section>

      <section id="services" className={s.cols}>
        <div className={s.secHead}><span className={s.label}>Υπηρεσίες</span></div>
        <div className={s.colGrid}>
          {d.services?.map((sv, i) => (
            <a key={i} href={tel} className={s.art}>
              <span className={s.num}>{sv.num}</span>
              <h3>{sv.title}</h3>
              <p>{sv.desc}</p>
            </a>
          ))}
        </div>
      </section>

      <section id="work" className={s.galSec}>
        <div className={s.secHead}><span className={s.label}>Πορτφόλιο</span></div>
        <div className={s.gal}>
          {d.gallery?.map((g, i) => (
            <figure key={i} className={i === 0 ? s.galBig : ''}><img src={g.image} alt={g.title} loading="lazy" /><figcaption>{g.title}</figcaption></figure>
          ))}
        </div>
      </section>

      <section id="story" className={s.storySec}>
        <div className={s.secHead}><span className={s.label}>Η ιστορία</span></div>
        <h2 className={s.storyH}>{d.STORY_TITLE}</h2>
        <div className={s.storyCols}>
          {d.story?.map((p, i) => <p key={i} className={i === 0 ? s.drop : ''}>{p.p}</p>)}
        </div>
        <div className={s.sign}>— {d.NAME}</div>
      </section>

      <section id="contact" className={s.cta}>
        <h2>{d.CTA_TITLE}</h2>
        <p>{d.AREAS} · {d.HOURS}</p>
        <a href={tel} className={s.btn}>📞 Κάλεσε {d.PHONE}</a>
      </section>

      <footer className={s.footer}>© {d.YEAR} {d.NAME} — {d.CITY} · Site από Vitrina</footer>
    </div>
  )
}
