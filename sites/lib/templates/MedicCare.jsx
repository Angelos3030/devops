import s from './MedicCare.module.css'
import Brand from './Brand'
import FindUs from './FindUs'
import SocialLinks from './SocialLinks'

export default function MedicCare({ data: d }) {
  return (
    <div className={s.root}>
      <nav className={s.nav} aria-label="Κύρια πλοήγηση">
        <div className={s.navIn}>
          <a href="#home" className={s.logo}><Brand data={d} className={s.brand} dark /></a>
          <div className={s.navLinks}>
            <a href="#home">Αρχική</a>
            <a href="#about">Σχετικά</a>
            <a href="#timeline">Υπηρεσίες</a>
            <a href="#contact">Επικοινωνία</a>
          </div>
        </div>
      </nav>

      <header id="home" className={s.hero}>
        <div className={s.heroTrack}>
          {d.gallery.map((item, i) => (
            <div key={i} className={s.heroSlide}>
              <img src={item.image} alt={item.title} />
            </div>
          ))}
        </div>
        <div className={s.heroText}>
          <h1>{d.HERO_WORD}</h1>
          <p>{d.TAGLINE}</p>
          <div className={s.heroLinks}>
            <a className={s.customLink} href="#about">{d.CTA_TITLE}</a>
            <p className={s.contactPhone}><a href={`tel:${d.PHONE_INTL}`}>{d.PHONE}</a></p>
          </div>
        </div>
      </header>

      <section id="about" className={`${s.section} ${s.about}`}>
        <div className={s.container}>
          <h2 className={s.sectionTitle}>{d.STORY_TITLE}</h2>
          {d.story.map((para, i) => (
            <p key={i}>{para.p}</p>
          ))}
        </div>
      </section>

      <section className={`${s.section} ${s.gallery}`}>
        <div className={s.container}>
          <div className={s.galleryGrid}>
            {d.gallery.slice(0, 2).map((item, i) => (
              <img key={i} src={item.image} alt={item.title} className={s.galleryImage} />
            ))}
          </div>
        </div>
      </section>

      <section id="timeline" className={`${s.section} ${s.timelineSection}`}>
        <div className={s.container}>
          <h2 className={s.sectionTitle}>Υπηρεσίες</h2>
          <div className={s.timeline}>
            {d.services.map((service, i) => (
              <div key={i} className={s.timelineNode}>
                <div className={s.timelineContent}>
                  <h3 className={s.timelineTitle}>{service.title}</h3>
                  <p>{service.desc}</p>
                  <p className={s.serviceMeta}>
                    {service.duration} {service.price ? `• ${service.price} €` : ''}
                  </p>
                </div>
                <div className={s.timelineIcon}>
                  <span className={s.iconCircle}>{i + 1}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <footer id="contact" className={s.footer}>
        <div className={s.container}>
          <div className={s.footerGrid}>
            <div className={s.footerCol}>
              <h5>Ωράριο</h5>
              <p>{d.HOURS}</p>
            </div>
            <div className={s.footerCol}>
              <h5>Η Κλινική μας</h5>
              <p><a href={`tel:${d.PHONE_INTL}`}>{d.PHONE}</a></p>
              <p>{d.CITY} {d.POSTCODE}</p>
              <p>{d.AREAS}</p>
            </div>
            <div className={s.footerCol}>
              <h5>Social</h5>
              <SocialLinks data={d} className={s.socialLinks} />
            </div>
          </div>
          <FindUs data={d} />
        </div>
      </footer>
    </div>
  )
}
