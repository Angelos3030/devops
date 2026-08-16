import s from './BarberSidebar.module.css'
import Brand from './Brand'
import FindUs from './FindUs'
import SocialLinks from './SocialLinks'

export default function BarberSidebar({ data: d }) {
  const areas = d.AREAS ? d.AREAS.split(',').map(a => a.trim()).filter(Boolean) : []
  const services = d.services || []
  const gallery = d.gallery || []
  const storyParagraphs = d.story || []

  return (
    <div className={s.root}>
      <aside className={s.sidebar}>
        <div className={s.sidebarSticky}>
          <a href="#home" className={s.logo}>
            <Brand data={d} className={s.brand} dark />
          </a>
          <nav className={s.nav} aria-label="Κύρια πλοήγηση">
            <ul className={s.navList}>
              <li><a href="#home" className={s.navLink}>Αρχική</a></li>
              <li><a href="#our-story" className={s.navLink}>Η Ιστορία μας</a></li>
              <li><a href="#services" className={s.navLink}>Υπηρεσίες</a></li>
              <li><a href="#price-list" className={s.navLink}>Τιμοκατάλογος</a></li>
              <li><a href="#contact" className={s.navLink}>Επικοινωνία</a></li>
            </ul>
          </nav>
        </div>
      </aside>

      <main className={s.main}>
        <section id="home" className={s.hero}>
          <div className={s.heroOverlay} />
          <div className={s.heroContent}>
            <h1 className={s.heroTitle}>
              <strong>{d.HERO_WORD || d.NAME}</strong> <em>{d.KICKER || d.TRADE}</em>
            </h1>
            <p className={s.heroText}>{d.TAGLINE}</p>
            <div className={s.heroButtons}>
              <a href="#our-story" className={s.btnPrimary}>Σχετικά με εμάς</a>
              <a href="#services" className={s.btnSecondary}>{d.CTA_TITLE || 'Τι κάνουμε'}</a>
            </div>
          </div>
          <div className={s.heroCard}>
            <img src={d.STORY_IMAGE} alt={d.NAME} className={s.heroCardImage} />
            <h4 className={s.heroCardTitle}><strong>{d.CTA_TITLE || 'Επικοινωνήστε μαζί μας'}</strong></h4>
            <a href="#contact" className={s.heroCardLink}>Μάθετε περισσότερα</a>
          </div>
        </section>

        <section id="our-story" className={s.section}>
          <div className={s.container}>
            <h2 className={s.sectionTitle}>{d.STORY_TITLE || 'Η Ιστορία μας'}</h2>
            <p className={s.sectionIntro}>{d.INTRO}</p>
            {storyParagraphs.length > 0 && (
              <div className={s.storyParagraphs}>
                {storyParagraphs.map((para, index) => (
                  <p key={index} className={s.storyParagraph}>{para.p}</p>
                ))}
              </div>
            )}
          </div>
        </section>

        <section id="services" className={s.section}>
          <div className={s.container}>
            <h2 className={s.sectionTitle}>Υπηρεσίες</h2>
            <div className={s.servicesGrid}>
              {services.map((service, index) => {
                const image = gallery[index % gallery.length];
                return (
                  <div key={service.num || index} className={s.serviceCard}>
                    <img src={image?.image || d.HERO_IMAGE} alt={service.title} className={s.serviceImage} />
                    <div className={s.serviceInfo}>
                      <h4 className={s.serviceTitle}>{service.title}</h4>
                      <strong className={s.servicePrice}>{service.price}</strong>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        <section id="price-list" className={s.section}>
          <div className={s.container}>
            <div className={s.priceListRow}>
              <div className={s.priceListContent}>
                <h2 className={s.sectionTitle}>Τιμοκατάλογος</h2>
                <strong className={s.priceListNote}>Από {services[0]?.price || '—'}</strong>
                <div className={s.priceListItems}>
                  {services.map((service, index) => (
                    <div key={service.num || index} className={s.priceListItem}>
                      <h6 className={s.priceListItemTitle}>
                        {service.title}
                        <span className={s.priceListDivider}></span>
                        <strong className={s.priceListItemPrice}>{service.price}</strong>
                      </h6>
                    </div>
                  ))}
                </div>
              </div>
              <div className={s.priceListImageWrap}>
                <img src={d.STORY_IMAGE} alt={d.NAME} className={s.priceListImage} />
              </div>
            </div>
          </div>
        </section>

        <section id="contact" className={s.section}>
          <div className={s.container}>
            <h2 className={s.sectionTitle}>Επικοινωνία</h2>
            <div className={s.contactRow}>
              <div className={s.contactInfo}>
                <h5 className={s.contactHeading}><strong>Πληροφορίες</strong></h5>
                <p className={s.contactLine}>
                  <a href={`tel:${d.PHONE_INTL || d.PHONE}`} className={s.contactLink}>{d.PHONE}</a>
                </p>
                <p className={s.contactLine}>
                  <a href={`mailto:${d.DOMAIN}`} className={s.contactLink}>{d.DOMAIN}</a>
                </p>
                <SocialLinks data={d} className={s.socialLinks} />
              </div>
              <div className={s.contactBlockWrap}>
                <div className={s.contactBlock}>
                  <h6 className={s.contactBlockTitle}>
                    <strong>Ανοιχτά Καθημερινά</strong>
                    <span className={s.contactBlockHours}>{d.HOURS}</span>
                  </h6>
                </div>
              </div>
            </div>
            <div className={s.map}>
              <FindUs data={d} />
            </div>
          </div>
        </section>

        <footer className={s.footer}>
          <div className={s.container}>
            <h4 className={s.footerTitle}>Περιοχές Εξυπηρέτησης</h4>
            <div className={s.footerAreas}>
              {areas.map((area, index) => (
                <div key={index} className={s.footerAreaItem}>
                  <strong>{area}</strong>
                </div>
              ))}
              {areas.length === 0 && (
                <div className={s.footerAreaItem}>
                  <strong>{d.CITY} {d.POSTCODE}</strong>
                </div>
              )}
            </div>
          </div>
          <div className={s.footerBottom}>
            <div className={s.container}>
              <p className={s.copyright}>© {d.YEAR || new Date().getFullYear()} {d.NAME}. Με επιφύλαξη παντός δικαιώματος.</p>
              <a href="#home" className={s.backTop}>↑</a>
            </div>
          </div>
        </footer>
      </main>
    </div>
  )
}
