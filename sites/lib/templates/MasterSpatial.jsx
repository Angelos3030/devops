import Brand from './Brand'
import s from './MasterSpatial.module.css'

const phoneHref = (d) => d.PHONE_INTL ? `tel:+${d.PHONE_INTL}` : '#contact'

export default function MasterSpatial({ data: d }) {
  const scenes = [
    { n: '00', title: d.NAME, copy: d.TAGLINE, image: d.HERO_IMAGE },
    ...(d.services || []).slice(0, 3).map((service, index) => ({ n: `0${index + 1}`, title: service.title, copy: service.desc, image: d.gallery?.[index]?.image || d.HERO_IMAGE })),
    { n: '04', title: d.CTA_TITLE, copy: `${d.CITY} · ${d.PHONE}`, image: d.gallery?.[3]?.image || d.STORY_IMAGE },
  ]

  return <main id="top" className={s.root}>
    <header className={s.header}>
      <a href="#top" aria-label="Αρχική"><Brand data={d} /></a>
      <span>{d.TRADE}</span>
      <a href={phoneHref(d)}>Επικοινωνία ↗</a>
    </header>
    <div className={s.track} tabIndex="0" aria-label="Οριζόντια παρουσίαση υπηρεσιών">
      {scenes.map((scene, index) => <section className={s.scene} key={scene.n}>
        <div className={s.number}>{scene.n}</div>
        <div className={s.visual}>
          {scene.image ? <img src={scene.image} alt={index === 0 ? `Η επιχείρηση ${d.NAME}` : scene.title} /> : <span>{scene.n}</span>}
        </div>
        <div className={s.copy}>
          {index === 0 ? <h1>{scene.title}</h1> : <h2>{scene.title}</h2>}
          <p>{scene.copy}</p>
          {index === scenes.length - 1 && <a href={phoneHref(d)}>Κάλεσε τώρα ↗</a>}
        </div>
        <div className={s.axis}><span>{d.CITY}</span><i /><span>0{scenes.length}</span></div>
      </section>)}
    </div>
    <div className={s.hint}>DRAG / SCROLL <span>→</span></div>
  </main>
}
