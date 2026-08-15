import Brand from './Brand'
import s from './MasterEditorial.module.css'

const phoneHref = (d) => d.PHONE_INTL ? `tel:+${d.PHONE_INTL}` : '#contact'

export default function MasterEditorial({ data: d }) {
  const rows = [
    ...(d.services || []).map((service, index) => ({ title: service.title, body: service.desc, tag: `0${index + 1}` })),
    { title: 'Η ιστορία μας', body: d.INTRO, tag: 'ΣΧ' },
    { title: 'Επικοινωνία', body: `${d.CITY} · ${d.HOURS}`, tag: 'ΕΠ' },
  ]

  return <main id="top" className={s.root}>
    <header className={s.header}>
      <a href="#top" aria-label="Αρχική"><Brand data={d} /></a>
      <nav><a href="#index">Ευρετήριο</a><a href="#about">Σχετικά</a><a href="#contact">Επικοινωνία</a></nav>
      <span>{d.CITY}, {d.YEAR}</span>
    </header>
    <section className={s.masthead}>
      <p>{d.TRADE} / {d.CITY}</p>
      <h1>{d.NAME}</h1>
      <div><strong>{d.TAGLINE}</strong><span>{d.INTRO}</span></div>
    </section>
    <section id="index" className={s.index}>
      <div className={s.indexHead}><span>Α/Α</span><span>Υπηρεσία</span><span>Πληροφορίες</span><span>Άνοιγμα</span></div>
      {rows.map((row) => <details key={row.tag}>
        <summary><span>{row.tag}</span><strong>{row.title}</strong><small>{row.body}</small><b aria-hidden="true">+</b></summary>
        <div className={s.detail}><p>{row.body}</p><a href={phoneHref(d)}>Ρώτησέ μας ↗</a></div>
      </details>)}
    </section>
    <section id="about" className={s.statement}>
      <span>Σημείωση 01</span>
      <p>{d.STORY_TITLE || d.INTRO}</p>
    </section>
    <footer id="contact" className={s.footer}>
      <p>{d.AREAS || d.CITY}</p>
      <a href={phoneHref(d)}>{d.PHONE}</a>
      <p>{d.HOURS}</p>
      <a href="#top">Πάνω ↑</a>
    </footer>
  </main>
}
