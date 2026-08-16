import s from './VillaAgency.module.css'
import Brand from './Brand'
import FindUs from './FindUs'
import SocialLinks from './SocialLinks'

export default function VillaAgency({ data: d }) {
  const heroSlides = (d.gallery || []).slice(0, 3)
  const featuredImage = d.STORY_IMAGE || d.gallery?.[0]?.image
  const categories = (d.services || []).map((svc) => svc.title).filter(Boolean)
  const propertyCards = d.gallery || []

  return (
    <div className={s.root}>
      <div className={s.topBar}>
        <div className={s.container}>
          <div className={s.topBarInfo}>
            <span>{d.PHONE}</span>
            <span>{d.CITY} {d.POSTCODE}</span>
          </div>
          <SocialLinks data={d} className={s.socialLinksTop} />
        </div>
      </div>

      <nav className={s.nav} aria-label="Κύρια πλοήγηση">
        <div className={`${s.container} ${s.navIn}`}>
          <a href="#home" className={s.logo}>
            <Brand data={d} className={s.brand} dark />
          </a>
          <div className={s.navLinks}>
            <a href="#home">Αρχική</a>
            <a href="#featured">Χαρακτηριστικά</a>
            <a href="#properties">Ακίνητα</a>
            <a href="#contact">Επικοινωνία</a>
          </div>
        </div>
      </nav>

      <header id="home" className={s.hero}>
        <div className={s.heroTrack}>
          {heroSlides.map((item, idx) => (
            <div className={s.heroSlide} key={idx}>
              <img src={item.image} alt={item.title} />
            </div>
          ))}
        </div>
        <div className={s.heroOverlay}>
          <span className={s.heroLocation}>{d.CITY} — {d.TRADE}</span>
          <h1 className={s.heroTitle}>{d.HERO_WORD || d.NAME}</h1>
          <p className={s.heroSub}>{d.TAGLINE}</p>
        </div>
      </header>

      <section id="featured" className={s.featured}>
        <div className={s.container}>
          <div className={s.featuredGrid}>
            <div className={s.featuredImageWrap}>
              <img src={featuredImage} alt={d.STORY_TITLE || d.NAME} />
            </div>
            <div className={s.featuredContent}>
              <p className={s.sectionKicker}>| {d.KICKER || 'Featured'}</p>
              <h2>{d.STORY_TITLE || d.TAGLINE}</h2>
              <p>{d.INTRO}</p>
              {(d.story || []).map((para, idx) => (
                <p key={idx}>{para.p}</p>
              ))}
            </div>
            <div className={s.featureList}>
              {(d.services || []).slice(0, 4).map((svc, idx) => (
                <div className={s.featureItem} key={idx}>
                  <h4>{svc.title}</h4>
                  <p>{svc.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className={s.videoSection}>
        <div className={s.container}>
          <div className={s.videoHeading}>
            <p className={s.sectionKicker}>| {d.KICKER || 'Video'}</p>
            <h2>{d.CTA_TITLE || 'Δείτε περισσότερα'}</h2>
          </div>
          <div className={s.videoFrame}>
            <img src={d.gallery?.[0]?.image || featuredImage} alt={d.gallery?.[0]?.title || ''} />
            <span className={s.playButton}>▶</span>
          </div>
        </div>
      </section>

      <section className={s.categories}>
        <div className={s.container}>
          <div className={s.pills}>
            {categories.map((cat, idx) => (
              <span className={s.pill} key={idx}>{cat}</span>
            ))}
          </div>
        </div>
      </section>

      <section id="properties" className={s.properties}>
        <div className={s.container}>
          <div className={s.sectionHeading}>
            <p className={s.sectionKicker}>| {d.KICKER || 'Properties'}</p>
            <h2>{d.CTA_TITLE || 'Τα ακίνητά μας'}</h2>
          </div>
          <div className={s.cardGrid}>
            {propertyCards.map((item, idx) => {
              const svc = d.services?.[idx]
              return (
                <article className={s.card} key={idx}>
                  <img src={item.image} alt={item.title} />
                  <span className={s.cardBadge}>{item.sub || 'Ακίνητο'}</span>
                  {svc?.price && <span className={s.cardPrice}>{svc.price}</span>}
                  <h3>{item.title}</h3>
                  {svc && (
                    <ul className={s.cardFeatures}>
                      {svc.num && <li><span>Αρ.</span>{svc.num}</li>}
                      {svc.duration && <li><span>Διάρκεια</span>{svc.duration}</li>}
                      {svc.desc && <li><span>Περιγραφή</span>{svc.desc}</li>}
                    </ul>
                  )}
                </article>
              )
            })}
          </div>
        </div>
      </section>

      <section id="contact" className={s.contact}>
        <div className={s.container}>
          <div className={s.contactGrid}>
            <div className={s.contactInfo}>
              <p className={s.sectionKicker}>| {d.KICKER || 'Contact'}</p>
              <h2>{d.CTA_TITLE || 'Επικοινωνήστε μαζί μας'}</h2>
              <FindUs data={d} />
            </div>
            <div className={s.contactCard}>
              <h3>Στοιχεία επικοινωνίας</h3>
              <p>{d.PHONE}</p>
              <p>{d.CITY} {d.POSTCODE}</p>
              <p>{d.HOURS}</p>
              <SocialLinks data={d} className={s.socialLinksDark} />
            </div>
          </div>
        </div>
      </section>

      <footer className={s.footer}>
        <div className={s.container}>
          <p>© {d.YEAR || new Date().getFullYear()} {d.NAME}. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}
