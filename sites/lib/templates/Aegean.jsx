import s from './Aegean.module.css'
import FindUs from './FindUs'
import Brand from './Brand'

// "Aegean" — τουρισμός/δωμάτια: κυκλαδίτικο φως. Full-bleed θάλασσα, λεπτή
// Literata, ασβέστης & γαλάζιο. Signature: το «καρτ-ποστάλ» — gallery ως
// ταχυδρομικές κάρτες με κλίση, σαν αναμνήσεις καρφιτσωμένες στον τοίχο.
export default function Aegean({ data: d }) {
  const tel = `tel:+${d.PHONE_INTL}`
  const hasPhone = Boolean(d.PHONE_INTL)
  return (
    <div className={s.root}>
      <header id="top" className={s.hero}>
        {d.HERO_IMAGE && <img className={s.heroBg} src={d.HERO_IMAGE} alt="" aria-hidden="true" />}
        <div className={s.heroVeil} aria-hidden="true" />
        <nav className={s.nav}>
          <Brand data={d} className={s.brand} dark />
          {hasPhone && <a href={tel} className={s.navCall}>Κράτηση</a>}
        </nav>
        <div className={s.heroCenter}>
          <span className={s.eyebrow}>{d.KICKER}</span>
          <h1 className={s.title}>{d.NAME}</h1>
          <p className={s.lede}>{d.TAGLINE}</p>
          {hasPhone && <a href={tel} className={s.cta}>Κλείσε δωμάτιο · {d.PHONE}</a>}
        </div>
      </header>

      <section id="rooms" className={s.rooms}>
        <div className={s.secHead}>
          <span className={s.eyebrowBlue}>Φιλοξενία</span>
          <h2>Όλα όσα χρειάζεσαι για τη διαμονή σου</h2>
        </div>
        <div className={s.roomGrid}>
          {d.services?.map((sv, i) => (
            <div key={i} className={s.room}>
              <span className={s.roomNum}>{sv.num}</span>
              <h3>{sv.title}</h3>
              <p>{sv.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <section id="photos" className={s.postcards}>
        {d.gallery?.map((g, i) => (
          <figure key={i} className={s.card} style={{ '--tilt': `${(i % 3) - 1}deg` }}>
            <img src={g.image} alt={g.title} loading="lazy" />
            <figcaption>{g.title} · {g.sub}</figcaption>
          </figure>
        ))}
      </section>

      <section id="story" className={s.story}>
        <div className={s.storyFrame}>
          <span className={s.eyebrowBlue}>Η ιστορία μας</span>
          <h2 className={s.storyTitle}>{d.STORY_TITLE}</h2>
          {d.story?.map((p, i) => <p key={i}>{p.p}</p>)}
          <span className={s.sig}>{[d.NAME, d.CITY].filter(Boolean).join(' · ')}</span>
        </div>
      </section>

      <section id="contact" className={s.cta2}>
        <h2>{d.CTA_TITLE}</h2>
        {hasPhone && <a href={tel} className={s.cta}>📞 {d.PHONE}</a>}
        {(d.HOURS || d.AREAS) && <p className={s.cta2Sub}>{[d.HOURS, d.AREAS].filter(Boolean).join(' · ')}</p>}
      </section>

      <FindUs data={d} />


      <footer className={s.footer}>© {d.YEAR} {[d.NAME, d.CITY].filter(Boolean).join(' · ')} · Site από Vitrina</footer>
    </div>
  )
}
