import s from './KlassyTable.module.css'
import Brand from './Brand'
import FindUs from './FindUs'
import SocialLinks from './SocialLinks'

export default function KlassyTable({ data: d }) {
  return (
    <div className={s.root}>
      <nav className={s.nav} aria-label="Κύρια πλοήγηση">
        <div className={s.navIn}>
          <a href="#home" className={s.logo}><Brand data={d} className={s.brand} dark /></a>
          <div className={s.navLinks}>
            <a href="#home">Αρχική</a>
            <a href="#about">Σχετικά</a>
            <a href="#menu">Μενού</a>
            <a href="#contact">Επικοινωνία</a>
          </div>
        </div>
      </nav>

      <header id="home" className={s.hero}>
        <div className={s.heroLeft}>
          <Brand data={d} className={s.heroBrand} />
          <h1 className={s.heroKicker}>{d.KICKER}</h1>
          <p className={s.heroWord}>{d.HERO_WORD}</p>
          <a href="#contact" className={s.heroCta}>{d.CTA_TITLE}</a>
        </div>
        <div className={s.heroRight}>
          <img src={d.HERO_IMAGE} alt={d.NAME || d.TRADE} className={s.heroImage} />
        </div>
      </header>

      <section id="about" className={s.about}>
        <div className={s.aboutInner}>
          <div className={s.aboutText}>
            <h6 className={s.sectionLabel}>Σχετικά με εμάς</h6>
            <h2 className={s.sectionTitle}>{d.STORY_TITLE}</h2>
            <p className={s.aboutIntro}>{d.INTRO}</p>
            {d.story && d.story.map((item, i) => <p key={i}>{item.p}</p>)}
            <div className={s.aboutThumbs}>
              {d.gallery && d.gallery.slice(0, 3).map((img, i) => (
                <img key={i} src={img.image} alt={img.title} className={s.aboutThumb} />
              ))}
            </div>
          </div>
          <div className={s.aboutImageWrap}>
            <img src={d.STORY_IMAGE} alt={d.STORY_TITLE} className={s.aboutImage} />
          </div>
        </div>
      </section>

      <section id="menu" className={s.menu}>
        <div className={s.menuHeader}>
          <h6 className={s.sectionLabel}>Το Μενού μας</h6>
          <h2 className={s.sectionTitle}>{d.TRADE} επιλογές</h2>
        </div>
        <div className={s.menuGrid}>
          {d.services && d.services.map((service, i) => (
            <div key={i} className={s.menuCard}>
              <div className={s.priceBadge}>€{service.price}</div>
              <div className={s.menuInfo}>
                <h3 className={s.menuItemTitle}>{service.title}</h3>
                <p className={s.menuItemDesc}>{service.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section id="offers" className={s.offers}>
        <div className={s.offersHeader}>
          <h6 className={s.sectionLabel}>Εβδομαδιαίες Προσφορές</h6>
          <h2 className={s.sectionTitle}>Ειδικές τιμές</h2>
        </div>
        <div className={s.offersList}>
          {d.services && d.services.map((service, i) => (
            <div key={i} className={s.offerItem}>
              <div className={s.offerText}>
                <h4>{service.title}</h4>
                <p>{service.desc}</p>
              </div>
              <div className={s.offerPrice}>€{service.price}</div>
            </div>
          ))}
        </div>
      </section>

      <section id="contact" className={s.contact}>
        <div className={s.contactInner}>
          <div className={s.contactInfo}>
            <h6 className={s.sectionLabelDark}>Επικοινωνία</h6>
            <h2 className={s.sectionTitleDark}>{d.TAGLINE}</h2>
            <FindUs data={d} dark />
            <SocialLinks data={d} className={s.socialLinks} />
          </div>
          <div className={s.contactCard}>
            <h4>Στοιχεία Επικοινωνίας</h4>
            <p>{d.PHONE}</p>
            <p>{d.CITY}, {d.POSTCODE}</p>
            <p>{d.HOURS}</p>
          </div>
        </div>
      </section>

      <footer className={s.footer}>
        <div className={s.footerInner}>
          <SocialLinks data={d} className={s.footerSocial} />
          <p>© {d.YEAR} {d.NAME}. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}