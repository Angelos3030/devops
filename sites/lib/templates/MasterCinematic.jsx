import Brand from './Brand'
import s from './MasterCinematic.module.css'

const phoneHref = (d) => d.PHONE_INTL ? `tel:+${d.PHONE_INTL}` : '#contact'

export default function MasterCinematic({ data: d }) {
  const media = [
    { image: d.HERO_IMAGE, eyebrow: d.KICKER, title: d.TAGLINE, copy: d.INTRO },
    ...(d.services || []).slice(0, 3).map((service, index) => ({
      image: d.gallery?.[index]?.image || d.HERO_IMAGE,
      eyebrow: `0${index + 2} / ${service.title}`,
      title: service.title,
      copy: service.desc,
    })),
  ]

  return <main id="top" className={s.root}>
    <header className={s.frame}>
      <a href="#top" className={s.wordmark} aria-label="Αρχική"><Brand data={d} /></a>
      <span className={s.location}>{d.CITY} / {d.YEAR}</span>
      <a className={s.book} href={phoneHref(d)}>Κράτηση <span>↗</span></a>
    </header>
    <nav className={s.rail} aria-label="Κεφάλαια">
      {media.map((item, index) => <a key={item.title} href={`#cinematic-${index}`}><span>0{index + 1}</span><i /></a>)}
    </nav>
    <div className={s.slides}>
      {media.map((item, index) => <section id={`cinematic-${index}`} className={s.slide} key={item.title}>
        {item.image ? <img src={item.image} alt={index === 0 ? `Η εμπειρία στο ${d.NAME}` : item.title} /> : <div className={s.noPhoto} aria-hidden="true"><span>0{index + 1}</span></div>}
        <div className={s.veil} />
        <div className={s.copy}>
          <p className={s.eyebrow}>{item.eyebrow}</p>
          {index === 0 ? <h1>{item.title}</h1> : <h2>{item.title}</h2>}
          <p className={s.body}>{item.copy}</p>
          <a className={s.action} href={index === media.length - 1 ? phoneHref(d) : `#cinematic-${index + 1}`}>
            {index === media.length - 1 ? 'Μίλησε μαζί μας' : 'Συνέχισε'} <span>↓</span>
          </a>
        </div>
        <span className={s.counter}>0{index + 1}<small>/ 0{media.length}</small></span>
      </section>)}
    </div>
  </main>
}
