import s from './Kinetic.module.css'
import Brand from './Brand'
import FindUs from './FindUs'

export default function Kinetic({ data: d }) {
  const tel = `tel:+${d.PHONE_INTL}`
  const services = d.services || []
  const gallery = d.gallery || []

  return (
    <div className={s.root}>
      <nav className={s.nav} aria-label="Κύρια πλοήγηση">
        <a href="#top" className={s.brand}><Brand data={d} /></a>
        <div className={s.navLinks}><a href="#services">Υπηρεσίες</a><a href="#work">Έργα</a></div>
        <a href={tel} className={s.navCall}>{d.PHONE}</a>
      </nav>

      <header id="top" className={`${s.hero} ${!d.HERO_IMAGE ? s.heroNoMedia : ''}`}>
        <div className={s.heroCopy}>
          <span className={s.eyebrow}>{d.KICKER}</span>
          <h1 className={s.title}><span>{d.NAME}</span><em>{d.HERO_WORD || d.TRADE}</em></h1>
          <p className={s.lede}>{d.TAGLINE}</p>
          <div className={s.actions}><a href={tel} className={s.cta}>Κάλεσε τώρα</a><a href="#work" className={s.ghost}>Δες έργα</a></div>
        </div>
        {d.HERO_IMAGE ? <figure className={s.heroMedia}><img src={d.HERO_IMAGE} alt={`${d.NAME} — ${d.TRADE}`} /></figure> : <div className={s.typeStage} aria-hidden="true"><span>{d.TRADE}</span><span>{d.CITY}</span></div>}
        <div className={s.runner} aria-hidden="true"><span>{d.TRADE} · {d.CITY} · {d.TRADE} · {d.CITY} ·</span></div>
      </header>

      <main>
        <section id="services" className={s.services}>
          <header className={s.sectionHead}><span>01 / Υπηρεσίες</span><h2>Από την ιδέα<br />στην πράξη.</h2></header>
          <div className={s.serviceList}>{services.map((item, i) => <a href={tel} className={s.service} key={i}><span className={s.number}>{item.num || String(i + 1).padStart(2, '0')}</span><h3>{item.title}</h3><p>{item.desc}</p><span className={s.arrow} aria-hidden="true">↗</span></a>)}</div>
        </section>

        <section id="work" className={s.work}>
          <header className={s.workHead}><span>02 / Επιλεγμένα έργα</span><h2>Δουλειά σε κίνηση.</h2></header>
          {gallery.length > 0 ? <div className={s.workGrid}>{gallery.map((item, i) => <figure className={s.project} key={i}><img src={item.image} alt={item.title} loading="lazy" /><figcaption><b>{item.title}</b><span>{item.sub}</span></figcaption></figure>)}</div> : <div className={s.noPhotoWork}>{services.slice(0, 4).map((item, i) => <article key={i}><span>0{i + 1}</span><h3>{item.title}</h3><p>{item.desc}</p></article>)}</div>}
        </section>

        <section id="story" className={s.story}>
          <span className={s.storyLabel}>03 / Η προσέγγιση</span><blockquote>{d.STORY_TITLE}</blockquote>
          <div className={s.storyText}>{d.story?.map((item, i) => <p key={i}>{item.p}</p>)}</div><span className={s.signature}>{d.NAME} · {d.CITY}</span>
        </section>

        <section id="contact" className={s.contact}><span>{d.AREAS}</span><h2>{d.CTA_TITLE}</h2><a href={tel}>{d.PHONE}<i aria-hidden="true">↗</i></a><p>{d.HOURS}</p></section>
      </main>
      <FindUs data={d} />
      <footer className={s.footer}><span>© {d.YEAR} {d.NAME}</span><span>Site από Vitrina</span></footer>
    </div>
  )
}
