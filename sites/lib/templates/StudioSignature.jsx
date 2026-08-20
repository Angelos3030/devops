import s from './StudioSignature.module.css'
import Brand from './Brand'
import FindUs from './FindUs'
import SocialLinks from './SocialLinks'

export default function StudioSignature({ data: d }) {
  const heroImage = d.HERO_IMAGE || d.gallery?.[0]?.image
  const heroAlt = d.gallery?.[0]?.title || d.NAME || ''
  const storyImage = d.STORY_IMAGE || d.gallery?.[1]?.image
  const storyAlt = d.STORY_TITLE || d.gallery?.[1]?.title || d.NAME || ''

  return (
    <div className={s.root}>
      <nav className={s.nav} aria-label='Κύρια πλοήγηση'>
        <div className={s.container}>
          <div className={s.navInner}>
            <a href='#home' className={s.logo}>
              <Brand data={d} className={s.brand} dark />
            </a>
            <div className={s.navLinks}>
              <a href='#home'>Αρχική</a>
              <a href='#about'>Σχετικά</a>
              <a href='#services'>Υπηρεσίες</a>
              <a href='#work'>Έργα</a>
              <a href='#contact'>Επικοινωνία</a>
            </div>
          </div>
        </div>
      </nav>

      <header className={s.hero} id='home'>
        <div className={s.container}>
          <div className={s.heroGrid}>
            <div className={s.heroContent}>
              {d.KICKER ? <p className={s.tagline}>{d.KICKER}</p> : null}
              <h1 className={s.heroTitle}>{d.HERO_WORD || d.NAME}</h1>
              {d.INTRO ? <p className={s.heroDescription}>{d.INTRO}</p> : null}
              <div className={s.btnGroup}>
                <a href='#work' className={s.btnPrimary}>Έργα</a>
                <a href='#contact' className={s.btnSecondary}>Επικοινωνία</a>
              </div>
            </div>
            {heroImage ? (
              <div className={s.heroVisual}>
                <div className={s.albumShowcase}>
                  <div className={s.albumCover}>
                    <img src={heroImage} alt={heroAlt} />
                    <div className={s.albumReflection} aria-hidden='true' />
                  </div>
                  <div className={s.visualizer} aria-hidden='true'>
                    {Array.from({ length: 12 }, (_, i) => (
                      <span key={i} className={s.bar} />
                    ))}
                  </div>
                  <div className={s.albumInfo}>
                    <span className={s.albumBadge}>{d.gallery?.[0]?.sub || 'Εξώφυλλο'}</span>
                    <h3>{d.gallery?.[0]?.title || d.NAME}</h3>
                    {d.gallery?.[0]?.sub ? <p>{d.gallery[0].sub}</p> : null}
                  </div>
                </div>
              </div>
            ) : null}
          </div>
        </div>
      </header>

      {d.story && d.story.length > 0 ? (
        <section className={s.about} id='about'>
          <div className={s.container}>
            <div className={s.aboutGrid}>
              {storyImage ? (
                <div className={s.aboutImageWrap}>
                  <img src={storyImage} alt={storyAlt} />
                </div>
              ) : null}
              <div className={s.aboutText}>
                <span className={s.sectionLabel}>Σχετικά</span>
                {d.STORY_TITLE ? <h2>{d.STORY_TITLE}</h2> : null}
                {d.story.map((para, i) => (
                  <p key={i}>{para.p}</p>
                ))}
              </div>
            </div>
          </div>
        </section>
      ) : null}

      {d.services && d.services.length > 0 ? (
        <section className={s.services} id='services'>
          <div className={s.container}>
            <span className={s.sectionLabel}>Υπηρεσίες</span>
            <h2>Πώς μπορώ να βοηθήσω</h2>
            <div className={s.servicesGrid}>
              {d.services.map((item, i) => {
                const icon = i % 3
                return (
                  <article className={s.serviceCard} key={item.title || item.num || i}>
                    <div className={s.serviceIcon} aria-hidden='true'>
                      {icon === 0 ? (
                        <svg width={32} height={32} viewBox='0 0 24 24' fill='none' stroke='currentColor' strokeWidth={2} strokeLinecap='round' strokeLinejoin='round'>
                          <path d='M9 18V5l12-2v13' />
                          <circle cx='6' cy='18' r='3' />
                          <circle cx='18' cy='16' r='3' />
                        </svg>
                      ) : icon === 1 ? (
                        <svg width={32} height={32} viewBox='0 0 24 24' fill='none' stroke='currentColor' strokeWidth={2} strokeLinecap='round' strokeLinejoin='round'>
                          <polygon points='23 7 16 12 23 17 23 7' />
                          <rect x='1' y='5' width='15' height='14' rx='2' ry='2' />
                        </svg>
                      ) : (
                        <svg width={32} height={32} viewBox='0 0 24 24' fill='none' stroke='currentColor' strokeWidth={2} strokeLinecap='round' strokeLinejoin='round'>
                          <path d='M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2' />
                          <circle cx='9' cy='7' r='4' />
                          <path d='M23 21v-2a4 4 0 0 0-3-3.87' />
                          <path d='M16 3.13a4 4 0 0 1 0 7.75' />
                        </svg>
                      )}
                    </div>
                    {item.num ? <span className={s.serviceNum}>{item.num}</span> : null}
                    {item.title ? <h3>{item.title}</h3> : null}
                    {item.desc ? <p>{item.desc}</p> : null}
                    {item.price || item.duration ? (
                      <div className={s.serviceMeta}>
                        {item.price ? <span>{item.price}</span> : null}
                        {item.duration ? <span>{item.duration}</span> : null}
                      </div>
                    ) : null}
                  </article>
                )
              })}
            </div>
          </div>
        </section>
      ) : null}

      {d.gallery && d.gallery.length > 0 ? (
        <section className={s.work} id='work'>
          <div className={s.container}>
            <span className={s.sectionLabel}>Χαρτοφυλάκιο</span>
            <h2>Επιλεγμένα έργα</h2>
            <div className={s.workGrid}>
              {d.gallery.map((item, i) => (
                <article className={s.workCard} key={i}>
                  {item.image ? (
                    <div className={s.workImage}>
                      <img src={item.image} alt={item.title || ''} />
                    </div>
                  ) : null}
                  <div className={s.workInfo}>
                    {item.sub ? <span className={s.workCategory}>{item.sub}</span> : null}
                    {item.title ? <h3>{item.title}</h3> : null}
                  </div>
                </article>
              ))}
            </div>
          </div>
        </section>
      ) : null}

      <section className={s.contact} id='contact'>
        <div className={s.container}>
          <div className={s.contactGrid}>
            <div className={s.contactInfo}>
              <span className={s.sectionLabel}>Επικοινωνία</span>
              <h2>{d.CTA_TITLE || 'Ας συνεργαστούμε'}</h2>
              {d.TAGLINE ? <p>{d.TAGLINE}</p> : null}
              <SocialLinks data={d} className={s.socialLinks} />
            </div>
            <div className={s.contactAside}>
              <FindUs data={d} />
            </div>
          </div>
        </div>
      </section>

      <footer className={s.footer}>
        <div className={s.container}>
          <div className={s.footerInner}>
            <p className={s.footerCopyright}>
              {d.YEAR ? `© ${d.YEAR}${d.NAME ? ' ' + d.NAME : ''}` : d.NAME || null}
            </p>
            {d.DOMAIN ? (
              <a className={s.footerCredit} href={`https://${d.DOMAIN}`} rel='noreferrer'>
                {d.DOMAIN}
              </a>
            ) : null}
          </div>
        </div>
      </footer>
    </div>
  )
}
