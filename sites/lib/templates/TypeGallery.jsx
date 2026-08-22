import s from './TypeGallery.module.css'
import Brand from './Brand'

// Type Gallery: a typography-led cultural poster. Suitable for studios,
// restaurants, fashion and creative practices; it stays expressive without photos.
export default function TypeGallery({ data: d }) {
  const tel = `tel:+${d.PHONE_INTL}`
  const gallery = d.gallery?.filter((item) => item?.image).slice(0, 6) || []

  return (
    <div className={s.root}>
      <nav className={s.nav} aria-label="Κύρια πλοήγηση">
        <a href="#top" className={s.wordmark}><Brand data={d} /></a>
        <span>{d.CITY}</span>
        <a href={tel} className={s.navCall}>{d.PHONE}</a>
      </nav>

      <header id="top" className={s.hero}>
        <span className={s.issue}>{d.KICKER} / {d.YEAR}</span>
        <h1>{d.TAGLINE || d.NAME}</h1>
        <div className={s.heroFoot}>
          <p>{d.TRADE}<br />{d.AREAS}</p>
          <a href="#gallery">Δες τη συλλογή <span aria-hidden="true">↓</span></a>
        </div>
      </header>

      <main>
        <section id="gallery" className={s.gallery} aria-label="Επιλεγμένες δουλειές">
          {gallery.length > 0 ? gallery.map((item, index) => (
            <figure className={s.tile} key={`${item.image}-${index}`}>
              <img src={item.image} alt={item.title || `Επιλεγμένη δουλειά ${index + 1}`} loading="lazy" />
              <figcaption><span>{String(index + 1).padStart(2, '0')}</span><strong>{item.title}</strong><em>{item.sub}</em></figcaption>
            </figure>
          )) : (
            <div className={s.typePoster}>
              <span>Selected</span><strong>{d.TRADE}</strong><em>{d.CITY} / {d.YEAR}</em>
            </div>
          )}
        </section>

        <section id="services" className={s.services} aria-labelledby="type-services-title">
          <header><span>Τι κάνουμε</span><h2 id="type-services-title">Υπηρεσίες σε πρώτο πλάνο.</h2></header>
          <div className={s.serviceRows}>
            {d.services?.map((service, index) => (
              <article key={index}>
                <span>{service.num || String(index + 1).padStart(2, '0')}</span>
                <h3>{service.title}</h3>
                <p>{service.desc}</p>
              </article>
            ))}
          </div>
        </section>

        <section className={s.manifesto} aria-labelledby="manifesto-title">
          <div className={s.vertical}>Η ιστορία μας</div>
          <div>
            <h2 id="manifesto-title">{d.STORY_TITLE}</h2>
            <div className={s.storyText}>{d.story?.map((paragraph, index) => <p key={index}>{paragraph.p}</p>)}</div>
          </div>
        </section>

        <section id="contact" className={s.contact} aria-labelledby="type-contact-title">
          <span>Έναρξη συνεργασίας</span>
          <h2 id="type-contact-title">{d.CTA_TITLE}</h2>
          <a href={tel}>{d.PHONE}<span aria-hidden="true">→</span></a>
          <p>{d.HOURS} · {d.AREAS}</p>
        </section>
      </main>

      <footer className={s.footer}>© {d.YEAR} {d.NAME} <span>Site από Vitrina</span></footer>
    </div>
  )
}
