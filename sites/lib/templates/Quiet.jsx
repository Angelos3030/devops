import s from './Quiet.module.css'
import Brand from './Brand'

// Quiet Precision: restrained, information-first system for professional services,
// architects and technical practices. Its identity comes from rhythm and detail,
// not decoration, and it is intentionally independent of photography.
export default function Quiet({ data: d }) {
  const tel = `tel:+${d.PHONE_INTL}`
  const images = d.gallery?.filter((item) => item?.image).slice(0, 3) || []

  return (
    <div className={s.root}>
      <header id="top" className={s.header}>
        <nav className={s.nav} aria-label="Κύρια πλοήγηση">
          <a href="#top" className={s.brand}><Brand data={d} /></a>
          <div className={s.links}><a href="#practice">Γραφείο</a><a href="#services">Υπηρεσίες</a><a href="#contact">Επικοινωνία</a></div>
          <a href={tel} className={s.call}>{d.PHONE}</a>
        </nav>
        <div className={s.hero}>
          <span className={s.index}>Q—01 / {d.YEAR}</span>
          <div className={s.heroTitle}>
            <span>{d.KICKER}</span>
            <h1>{d.TAGLINE || d.NAME}</h1>
          </div>
          <div className={s.heroMeta}><p>{d.TRADE}</p><p>{d.AREAS}</p><a href={tel}>Ζήτα συνάντηση <span aria-hidden="true">→</span></a></div>
        </div>
      </header>

      <main>
        <section id="practice" className={s.practice} aria-labelledby="practice-title">
          <span className={s.index}>Q—02 / Προσέγγιση</span>
          <div className={s.practiceBody}>
            <h2 id="practice-title">{d.STORY_TITLE}</h2>
            <div className={s.copy}>{d.story?.map((paragraph, index) => <p key={index}>{paragraph.p}</p>)}</div>
          </div>
        </section>

        {images.length > 0 && (
          <section className={s.imageBand} aria-label="Επιλεγμένα έργα">
            {images.map((item, index) => (
              <figure key={`${item.image}-${index}`}><img src={item.image} alt={item.title || `Έργο ${index + 1}`} loading="lazy" /><figcaption>{String(index + 1).padStart(2, '0')} / {item.title}</figcaption></figure>
            ))}
          </section>
        )}

        <section id="services" className={s.services} aria-labelledby="quiet-services-title">
          <header><span className={s.index}>Q—03 / Υπηρεσίες</span><h2 id="quiet-services-title">Πεδίο εργασίας</h2></header>
          <div className={s.serviceGrid}>
            {d.services?.map((service, index) => (
              <article key={index}>
                <span>{service.num || String(index + 1).padStart(2, '0')}</span>
                <h3>{service.title}</h3>
                <p>{service.desc}</p>
              </article>
            ))}
          </div>
        </section>

        <section className={s.facts} aria-label="Στοιχεία επιχείρησης">
          <div><span>Τοποθεσία</span><strong>{d.CITY}</strong></div>
          <div><span>Διαθεσιμότητα</span><strong>{d.HOURS}</strong></div>
          <div><span>Περιοχές</span><strong>{d.AREAS}</strong></div>
        </section>

        <section id="contact" className={s.contact} aria-labelledby="quiet-contact-title">
          <span className={s.index}>Q—04 / Επικοινωνία</span>
          <div><h2 id="quiet-contact-title">{d.CTA_TITLE}</h2><a href={tel}>{d.PHONE}<span aria-hidden="true">↗</span></a></div>
        </section>
      </main>

      <footer className={s.footer}><span>{d.NAME} / {d.CITY}</span><span>© {d.YEAR}</span><span>Site από Vitrina</span></footer>
    </div>
  )
}
