import s from './Ember.module.css'

// "Νυχτερινή ψησταριά" — smoky night palette, living ember glow, services served as a
// taverna κατάλογος with brass dotted leaders. Built for food/hospitality briefs.
export default function Ember({ data: d }) {
  const tel = `tel:+${d.PHONE_INTL}`
  return (
    <div className={s.root}>
      <nav className={s.nav}>
        <span className={s.brand}>{d.NAME}</span>
        <span className={s.navMeta}>{d.HOURS}</span>
        <a href={tel} className={s.navCall}>{d.PHONE}</a>
      </nav>

      <header id="top" className={s.hero}>
        <div className={s.glow} aria-hidden="true" />
        <div className={s.heroInner}>
          <span className={s.eyebrow}>{d.KICKER}</span>
          <h1 className={s.title}>{d.NAME}</h1>
          <p className={s.lede}>{d.TAGLINE}</p>
          <div className={s.heroActions}>
            <a href={tel} className={s.cta}>Κλείσε τραπέζι · {d.PHONE}</a>
            <span className={s.open}><i className={s.dot} />Ανοιχτά {d.HOURS}</span>
          </div>
        </div>
        {d.HERO_IMAGE && (
          <figure className={s.heroFig}>
            <img src={d.HERO_IMAGE} alt={`${d.NAME} — ${d.TRADE}`} />
          </figure>
        )}
      </header>

      <section id="menu" className={s.menu}>
        <div className={s.secHead}>
          <span className={s.label}>Ο κατάλογός μας</span>
          <h2 className={s.secTitle}>{d.TRADE}</h2>
        </div>
        <ul className={s.list}>
          {d.services?.map((sv, i) => (
            <li key={i} className={s.row} style={{ '--i': i }}>
              <span className={s.rowNo}>{sv.num}</span>
              <span className={s.rowName}>{sv.title}</span>
              <span className={s.leader} aria-hidden="true" />
              <span className={s.rowDesc}>{sv.desc}</span>
            </li>
          ))}
        </ul>
      </section>

      <section id="work" className={s.wall}>
        {d.gallery?.map((g, i) => (
          <figure key={i} className={s.tile} style={{ '--i': i }}>
            <img src={g.image} alt={g.title} loading="lazy" />
            <figcaption>
              <span className={s.tileTitle}>{g.title}</span>
              <span className={s.tileSub}>{g.sub}</span>
            </figcaption>
          </figure>
        ))}
      </section>

      <section id="story" className={s.story}>
        <div className={s.storyText}>
          <span className={s.labelBrass}>Η ιστορία μας</span>
          <blockquote className={s.pull}>{d.STORY_TITLE}</blockquote>
          {d.story?.map((p, i) => <p key={i}>{p.p}</p>)}
          <span className={s.sign}>— {d.NAME}, {d.CITY}</span>
        </div>
        {d.STORY_IMAGE && (
          <figure className={s.storyFig}>
            <img src={d.STORY_IMAGE} alt={`${d.NAME} — ο χώρος`} loading="lazy" />
          </figure>
        )}
      </section>

      <section id="contact" className={s.cta2}>
        <div className={s.glow2} aria-hidden="true" />
        <span className={s.eyebrow}>{d.AREAS}</span>
        <h2 className={s.cta2Title}>{d.CTA_TITLE}</h2>
        <a href={tel} className={s.cta2Btn}>📞 {d.PHONE}</a>
      </section>

      <footer className={s.footer}>
        <span>© {d.YEAR} {d.NAME}</span>
        <span>{d.CITY} · {d.AREAS}</span>
        <span className={s.by}>Site από Vitrina</span>
      </footer>
    </div>
  )
}
