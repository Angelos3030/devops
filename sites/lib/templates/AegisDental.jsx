import s from './AegisDental.module.css'
import Brand from './Brand'
import FindUs from './FindUs'
import SocialLinks from './SocialLinks'

export default function AegisDental({ data: d }) {
  return (
    <div className={s.root}>
      <nav className={s.nav} aria-label="Κύρια πλοήγηση">
        <div className={s.navIn}>
          <a href="#home" className={s.logo}>
            <Brand data={d} className={s.brand} dark />
          </a>

          <details className={s.menu}>
            <summary className={s.menuBtn} aria-label="Μενού">
              <span />
              <span />
            </summary>
            <div className={s.menuPanel}>
              <a href="#home">Αρχική</a>
              <a href="#services">Υπηρεσίες</a>
              <a href="#gallery">Έργα</a>
              <a href="#contact">Επικοινωνία</a>
              <a href={`tel:${d.PHONE_INTL}`} className={s.menuPhone}>{d.PHONE}</a>
            </div>
          </details>

          <div className={s.navLinks}>
            <a href="#home">Αρχική</a>
            <a href="#services">Υπηρεσίες</a>
            <a href="#gallery">Έργα</a>
            <a href="#contact">Επικοινωνία</a>
          </div>

          <a href={`tel:${d.PHONE_INTL}`} className={s.navPhone}>{d.PHONE}</a>
        </div>
      </nav>

      <header id="home" className={s.hero}>
        <div className={s.heroGrid}>
          <div className={s.heroText}>
            <p className={s.kicker}>{d.KICKER}</p>
            <h1 className={s.heroTitle}>
              <span className={s.heroWord}>{d.HERO_WORD}</span>
              <span className={s.heroLine}>{d.CITY}</span>
            </h1>
            <p className={s.heroMeta}>
              <Brand data={d} /> · {d.TRADE}
            </p>
            <p className={s.heroIntro}>{d.INTRO}</p>
            <div className={s.heroActions}>
              <a href={`tel:${d.PHONE_INTL}`} className={s.heroButton}>Κλείστε ραντεβού</a>
              <a href="#services" className={s.heroLink}>Οι υπηρεσίες μας</a>
            </div>
          </div>

          <div className={s.heroMedia}>
            <img src={d.HERO_IMAGE} alt="" className={s.heroImage} />
            <div className={s.heroBadge}>
              <span className={s.heroInitial}>{d.INITIAL}</span>
              <span className={s.heroTrade}>{d.TRADE}</span>
            </div>
          </div>
        </div>
      </header>

      <section id="services" className={s.services}>
        <div className={s.sectionIn}>
          <div className={s.sectionHead}>
            <p className={s.sectionKicker}>Υπηρεσίες</p>
            <h2 className={s.sectionTitle}>Ολοκληρωμένη οδοντιατρική φροντίδα</h2>
            <p className={s.sectionLead}>{d.TAGLINE}</p>
          </div>

          <div className={s.serviceGrid}>
            {d.services.map((item) => (
              <article key={item.num} className={s.serviceCard}>
                <span className={s.serviceNum} aria-hidden="true">{item.num}</span>
                <h3 className={s.serviceTitle}>{item.title}</h3>
                <p className={s.serviceDesc}>{item.desc}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className={s.story}>
        <div className={s.storyGrid}>
          <div className={s.storyMedia}>
            <img src={d.STORY_IMAGE} alt="" className={s.storyImage} />
          </div>
          <div className={s.storyText}>
            <p className={s.storyKicker}>{d.STORY_TITLE}</p>
            {d.story.map((par, i) => (
              <p key={i} className={s.storyP}>{par.p}</p>
            ))}
          </div>
        </div>
      </section>

      <section id="gallery" className={s.gallery}>
        <div className={s.sectionIn}>
          <div className={s.sectionHead}>
            <p className={s.sectionKicker}>Έργα</p>
            <h2 className={s.sectionTitle}>Χαμόγελα που μιλάνε από μόνα τους</h2>
          </div>

          <div className={s.slider} role="region" aria-label="Gallery" tabIndex={0}>
            <div className={s.sliderTrack}>
              {d.gallery.map((item, i) => (
                <figure key={i} className={s.slide}>
                  <img src={item.image} alt={item.title} className={s.slideImage} loading="lazy" />
                  <figcaption className={s.slideCaption}>
                    <strong>{item.title}</strong>
                    <span>{item.sub}</span>
                  </figcaption>
                </figure>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section id="contact" className={s.contact}>
        <div className={s.sectionIn}>
          <div className={s.contactGrid}>
            <div className={s.contactText}>
              <p className={s.contactKicker}>{d.CTA_TITLE}</p>
              <h2 className={s.contactTitle}>Είμαστε εδώ για να σας ακούσουμε</h2>
              <p className={s.contactLead}>Καλέστε μας ή επισκεφθείτε μας στο {d.CITY}.</p>
              <a href={`tel:${d.PHONE_INTL}`} className={s.contactButton}>{d.PHONE}</a>

              <div className={s.contactMeta}>
                <p><strong>Διεύθυνση</strong><br />{d.AREAS}, {d.CITY} {d.POSTCODE}</p>
                <p><strong>Ώρες λειτουργίας</strong><br />{d.HOURS}</p>
              </div>
            </div>

            <div className={s.contactFindUs}>
              <FindUs data={d} dark />
              <SocialLinks data={d} className={s.contactSocial} />
            </div>
          </div>
        </div>
      </section>

      <footer className={s.footer}>
        <div className={s.sectionIn}>
          <p className={s.footerLegal}>
            © {d.YEAR} <Brand data={d} /> · {d.DOMAIN}
          </p>
        </div>
      </footer>
    </div>
  )
}
