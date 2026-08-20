import s from './KlassyTable.module.css'
import Brand from './Brand'
import FindUs from './FindUs'
import SocialLinks from './SocialLinks'

export default function KlassyTable({ data: d }) {
  const serviceImages = d.gallery && d.gallery.length ? d.gallery : []
  const aboutMainImage = d.STORY_IMAGE || (serviceImages[0] ? serviceImages[0].image : null)
  const aboutMainAlt = d.STORY_IMAGE ? d.NAME : (serviceImages[0] ? serviceImages[0].title : d.NAME)

  return (
    <div className={s.root}>
      <nav className={s.nav} aria-label="Κύρια πλοήγηση">
        <div className={s.navIn}>
          <a href="#home" className={s.logo}><Brand data={d} className={s.brand} /></a>
          <div className={s.navLinks}>
            <a href="#home">Αρχική</a>
            <a href="#service">Υπηρεσίες</a>
            <a href="#portfolio">Έργα</a>
            <a href="#contact">Επικοινωνία</a>
          </div>
        </div>
      </nav>

      <header id="home" className={serviceImages.length ? s.hero : `${s.hero} ${s.heroNoMedia}`}>
        <div className={s.heroLeft}>
          <p className={s.heroKicker}>{d.TRADE || d.KICKER || d.INITIAL}</p>
          <h1 className={s.heroTitle}>{d.HERO_WORD || d.NAME}</h1>
          {d.TAGLINE ? <p className={s.heroTag}>{d.TAGLINE}</p> : null}
          <a className={s.heroButton} href="#service">Ανακαλύψτε μας</a>
        </div>
        {serviceImages.length > 0 ? (
          <div className={s.heroSlider} aria-label="Φωτογραφίες">
            {serviceImages.map((g, i) => (
              <div className={s.heroSlide} key={i}>
                <img src={g.image} alt={g.title} />
              </div>
            ))}
          </div>
        ) : null}
      </header>

      {d.story && d.story.length > 0 ? (
        <section id="about" className={s.about}>
          <div className={s.aboutText}>
            <span className={s.kicker}>Η ιστορία μας</span>
            <h2>{d.STORY_TITLE}</h2>
            {d.story.map((p, i) => <p key={i}>{p.p}</p>)}
          </div>
          <div className={s.aboutMedia}>
            {aboutMainImage ? (
              <div className={s.aboutMain}>
                <img src={aboutMainImage} alt={aboutMainAlt} />
              </div>
            ) : null}
            {serviceImages.length > 1 ? (
              <div className={s.aboutThumbs}>
                {serviceImages.slice(1, 4).map((g, i) => <img key={i} src={g.image} alt={g.title} />)}
              </div>
            ) : null}
          </div>
        </section>
      ) : null}

      {d.services && d.services.length > 0 ? (
        <section id="service" className={s.services}>
          <div className={s.sectionHead}>
            <span className={s.kicker}>Το μενού</span>
            <h2>Οι γεύσεις μας</h2>
          </div>
          <div className={s.menuTrack}>
            {d.services.map((item, i) => {
              const img = serviceImages[i]
              return (
                <article className={s.menuCard} key={item.num || i}>
                  {img ? <img className={s.menuImg} src={img.image} alt={img.title} /> : null}
                  <div className={s.menuBody}>
                    <span className={s.menuNum}>{item.num}</span>
                    <h3>{item.title}</h3>
                    <p>{item.desc}</p>
                  </div>
                </article>
              )
            })}
          </div>
        </section>
      ) : null}

      {serviceImages.length > 0 ? (
        <section id="portfolio" className={s.gallery}>
          <div className={s.sectionHead}>
            <span className={s.kicker}>Η συλλογή μας</span>
            <h2>Στιγμιότυπα</h2>
          </div>
          <div className={s.galleryGrid}>
            {serviceImages.map((g, i) => (
              <figure className={s.galleryItem} key={i}>
                <img src={g.image} alt={g.title} />
                <figcaption>
                  <h3>{g.title}</h3>
                  <p>{g.sub}</p>
                </figcaption>
              </figure>
            ))}
          </div>
        </section>
      ) : null}

      <section id="contact" className={s.contact}>
        <div className={s.contactInner}>
          <div className={s.contactInfo}>
            <span className={s.kicker}>Επικοινωνία</span>
            <h2>{d.CTA_TITLE || 'Επικοινωνία'}</h2>
            {d.INTRO ? <p>{d.INTRO}</p> : null}
            <dl className={s.contactList}>
              {d.PHONE ? <div><dt>Τηλέφωνο</dt><dd>{d.PHONE}</dd></div> : null}
              {d.PHONE_INTL ? <div><dt>Διεθνές</dt><dd>{d.PHONE_INTL}</dd></div> : null}
              {d.HOURS ? <div><dt>Ωράριο</dt><dd>{d.HOURS}</dd></div> : null}
              {d.AREAS ? <div><dt>Περιοχές</dt><dd>{d.AREAS}</dd></div> : null}
              {d.POSTCODE ? <div><dt>Ταχ. Κώδικας</dt><dd>{d.POSTCODE}</dd></div> : null}
              {d.DOMAIN ? <div><dt>Ιστοσελίδα</dt><dd>{d.DOMAIN}</dd></div> : null}
            </dl>
            <SocialLinks data={d} />
          </div>
        </div>
        <div className={s.contactCard}>
          <FindUs data={d} />
        </div>
      </section>

      <footer className={s.footer}>
        <div className={s.footerInner}>
          <Brand data={d} dark />
          <p>{d.NAME}{d.CITY ? ` — ${d.CITY}` : ''}</p>
        </div>
      </footer>
    </div>
  )
}
