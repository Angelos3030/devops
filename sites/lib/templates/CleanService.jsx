import s from './CleanService.module.css'
import Brand from './Brand'
import FindUs from './FindUs'
import SocialLinks from './SocialLinks'

export default function CleanService({ data: d }) {
  return (
    <div className={s.root}>
      <div className={s.topbar}>
        <div className={s.container}>
          <p className={s.topbarText}>{d.TAGLINE}</p>
          <p className={s.topbarText}>{d.HOURS}</p>
          <a className={s.topbarPhone} href={`tel:${d.PHONE_INTL}`}>{d.PHONE}</a>
        </div>
      </div>

      <nav className={s.nav} aria-label='Κύρια πλοήγηση'>
        <div className={`${s.container} ${s.navIn}`}>
          <a href='#home' className={s.logo}><Brand data={d} className={s.brand} dark /></a>
          <div className={s.navLinks}>
            <a href='#home'>Αρχική</a>
            <a href='#story'>Η ιστορία μας</a>
            <a href='#services'>Υπηρεσίες</a>
            <a href='#contact'>Επικοινωνία</a>
            <a href='#contact' className={s.navCta}>Ραντεβού</a>
          </div>
        </div>
      </nav>

      <header id='home' className={s.hero} style={{ backgroundImage: `url(${d.HERO_IMAGE})` }}>
        <div className={s.heroOverlay} />
        <div className={`${s.container} ${s.heroContent}`}>
          <p className={s.heroKicker}>{d.KICKER}</p>
          <h1 className={s.heroTitle}>{d.HERO_WORD}</h1>
          <p className={s.heroLead}>{d.TAGLINE}</p>
          <div className={s.heroActions}>
            <a href='#story' className={s.btnPrimary}>Η ιστορία μας</a>
            <a href='#services' className={s.btnGhost}>Υπηρεσίες</a>
          </div>
        </div>
        <svg className={s.wave} viewBox='0 0 1440 320' preserveAspectRatio='none' aria-hidden='true'>
          <path d='M0,224L40,229.3C80,235,160,245,240,250.7C320,256,400,256,480,240C560,224,640,192,720,176C800,160,880,160,960,138.7C1040,117,1120,75,1200,80C1280,85,1360,139,1400,165.3L1440,192L1440,320L1400,320C1360,320,1280,320,1200,320C1120,320,1040,320,960,320C880,320,800,320,720,320C640,320,560,320,480,320C400,320,320,320,240,320C160,320,80,320,40,320L0,320Z' />
        </svg>
      </header>

      <section id='story' className={s.story}>
        <div className={`${s.container} ${s.storyGrid}`}>
          <div className={s.storyText}>
            <p className={s.sectionKicker}>Η ομάδα μας</p>
            <h2 className={s.sectionTitle}>{d.STORY_TITLE}</h2>
            <p className={s.storyIntro}>{d.INTRO}</p>
            {d.story.map((item, i) => (
              <p key={i} className={s.storyParagraph}>{item.p}</p>
            ))}
          </div>
          <div className={s.storyMedia}>
            <img src={d.STORY_IMAGE} alt={d.STORY_TITLE} className={s.storyImage} />
            <div className={s.callCard}>
              <strong>Χρειάζεστε βοήθεια;</strong>
              <a href={`tel:${d.PHONE_INTL}`}>{d.PHONE}</a>
            </div>
          </div>
        </div>
      </section>

      <section id='services' className={s.services}>
        <div className={s.container}>
          <div className={s.sectionHead}>
            <p className={s.sectionKicker}>Τι προσφέρουμε</p>
            <h2 className={s.sectionTitle}>Οι υπηρεσίες μας</h2>
          </div>
          <div className={s.servicesGrid}>
            {d.services.map((item, i) => (
              <article key={item.num || i} className={s.serviceCard}>
                <div className={s.serviceMedia}>
                  {d.gallery[i] ? <img src={d.gallery[i].image} alt={d.gallery[i].title} className={s.serviceImage} /> : null}
                </div>
                <div className={s.serviceInfo}>
                  <span className={s.serviceNum}>{item.num}</span>
                  <h3 className={s.serviceTitle}>{item.title}</h3>
                  <p className={s.serviceDesc}>{item.desc}</p>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section id='contact' className={s.contact}>
        <div className={s.container}>
          <div className={s.contactGrid}>
            <div className={s.contactInfo}>
              <p className={s.sectionKicker}>Επικοινωνία</p>
              <h2 className={s.sectionTitle}>{d.CTA_TITLE}</h2>
              <p className={s.contactText}>Εξυπηρετούμε: {d.AREAS}</p>
              <a href={`tel:${d.PHONE_INTL}`} className={s.contactPhone}>{d.PHONE}</a>
              <p className={s.contactHours}>{d.HOURS}</p>
              <SocialLinks data={d} className={s.socialInline} />
            </div>
            <div className={s.mapWrap}>
              <FindUs data={d} />
            </div>
          </div>
        </div>
      </section>

      <footer className={s.footer}>
        <div className={s.container}>
          <div className={s.footerTop}>
            <a href='#home' className={s.footerBrand}><Brand data={d} dark /></a>
            <p className={s.footerTag}>{d.TAGLINE}</p>
          </div>
          <div className={s.footerGrid}>
            <div className={s.footerCol}>
              <h4>Υπηρεσίες</h4>
              <ul>
                {d.services.map((item, i) => <li key={i}>{item.title}</li>)}
              </ul>
            </div>
            <div className={s.footerCol}>
              <h4>Ώρες λειτουργίας</h4>
              <p>{d.HOURS}</p>
              <p>Περιοχή: {d.CITY}</p>
            </div>
            <div className={s.footerCol}>
              <h4>Επικοινωνία</h4>
              <a href={`tel:${d.PHONE_INTL}`}>{d.PHONE}</a>
              <SocialLinks data={d} className={s.socialInline} />
            </div>
          </div>
          <div className={s.footerBottom}>
            <span>© {d.YEAR} {d.NAME}.</span>
            <span>{d.DOMAIN}</span>
          </div>
        </div>
      </footer>

      <a className={s.callFab} href={`tel:${d.PHONE_INTL}`} style={{ color: 'var(--vt-on-accent)' }}>
        <span className={s.callFabIcon}>📞</span>
        <span>{d.PHONE}</span>
      </a>
    </div>
  )
}
