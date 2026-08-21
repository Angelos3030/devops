import s from './BarberSidebar.module.css'
import Brand from './Brand'
import FindUs from './FindUs'
import SocialLinks from './SocialLinks'

export default function BarberSidebar({ data: d }) {
  const services = Array.isArray(d.services) ? d.services : []
  const gallery = Array.isArray(d.gallery) ? d.gallery : []
  const story = Array.isArray(d.story) ? d.story : []
  const phoneHref = d.PHONE_INTL
    ? 'tel:' + d.PHONE_INTL
    : d.PHONE
      ? 'tel:' + d.PHONE
      : null

  return (
    <div className={s.root}>
      <nav className={s.nav} aria-label='Κύρια πλοήγηση'>
        <div className={s.navInner}>
          <a href='#home' className={s.logo}>
            <Brand data={d} className={s.brand} dark />
          </a>
          <div className={s.navLinks}>
            <a href='#home'>Αρχική</a>
            <a href='#story'>Ιστορία</a>
            <a href='#services'>Υπηρεσίες</a>
            <a href='#pricing'>Τιμοκατάλογος</a>
            <a href='#contact'>Επικοινωνία</a>
          </div>
        </div>
      </nav>

      <main className={s.main}>
        <header id='home' className={s.hero}>
          {d.HERO_IMAGE ? <img src={d.HERO_IMAGE} alt='' className={s.heroImage} /> : null}
          <div className={s.heroOverlay} aria-hidden='true'></div>
          <div className={s.heroContent}>
            {d.KICKER ? <p className={s.kicker}>{d.KICKER}</p> : null}
            <h1 className={s.heroTitle}>{d.NAME || d.HERO_WORD}</h1>
            {d.INTRO || d.TAGLINE ? (
              <p className={s.heroTagline}>{d.INTRO || d.TAGLINE}</p>
            ) : null}
            <div className={s.heroActions}>
              <a className={s.heroButton} href='#story'>Η ιστορία μας</a>
              <a className={s.heroButtonGhost} href='#services'>Οι υπηρεσίες μας</a>
            </div>
          </div>
        </header>

        {story.length > 0 ? (
          <section id='story' className={s.section}>
            <div className={s.sectionInner}>
              <div className={s.storyGrid}>
                <div className={s.storyBody}>
                  <p className={s.eyebrow}>Η ιστορία μας</p>
                  <h2 className={s.sectionTitle}>{d.STORY_TITLE || 'Η ιστορία μας'}</h2>
                  {story.map((item, i) => (
                    <p key={i} className={s.storyParagraph}>{item.p}</p>
                  ))}
                </div>
                {d.STORY_IMAGE ? (
                  <div className={s.storyImageWrap}>
                    <img src={d.STORY_IMAGE} alt={d.STORY_TITLE || ''} className={s.storyImage} />
                  </div>
                ) : null}
              </div>
            </div>
          </section>
        ) : null}

        {gallery.length > 0 ? (
          <section id='portfolio' className={s.section}>
            <div className={s.sectionInner}>
              <p className={s.eyebrow}>Έργα</p>
              <h2 className={s.sectionTitle}>Πρόσφατα κουρέματα</h2>
              <div className={s.galleryGrid}>
                {gallery.map((item, i) => (
                  <figure className={s.galleryCard} key={i}>
                    {item.image ? <img src={item.image} alt={item.title || ''} loading='lazy' className={s.galleryImage} /> : null}
                    {item.title || item.sub ? (
                      <figcaption className={s.galleryCaption}>
                        {item.title ? <h3>{item.title}</h3> : null}
                        {item.sub ? <p>{item.sub}</p> : null}
                      </figcaption>
                    ) : null}
                  </figure>
                ))}
              </div>
            </div>
          </section>
        ) : null}

        {services.length > 0 ? (
          <section id='services' className={s.section}>
            <div className={s.sectionInner}>
              <p className={s.eyebrow}>Υπηρεσίες</p>
              <h2 className={s.sectionTitle}>Τι προσφέρουμε</h2>
              <div className={s.servicesGrid}>
                {services.map((item, i) => {
                  const media = gallery[i]
                  const image = media ? media.image : null
                  const alt = media && media.title ? media.title : item.title || ''
                  return (
                    <article className={s.serviceCard} key={i}>
                      {image ? <img src={image} alt={alt} loading='lazy' className={s.serviceImage} /> : null}
                      <div className={s.serviceInfo}>
                        <h3 className={s.serviceTitle}>{item.title}</h3>
                        {item.desc ? <p className={s.serviceDesc}>{item.desc}</p> : null}
                        {item.duration ? <span className={s.serviceDuration}>{item.duration}</span> : null}
                      </div>
                      {item.price ? <span className={s.servicePrice}>{item.price}</span> : null}
                    </article>
                  )
                })}
              </div>
            </div>
          </section>
        ) : null}

        {services.length > 0 ? (
          <section id='pricing' className={s.section}>
            <div className={s.sectionInner}>
              <div className={s.pricingHeader}>
                <div>
                  <p className={s.eyebrow}>Τιμοκατάλογος</p>
                  <h2 className={s.sectionTitle}>Η λίστα τιμών μας</h2>
                </div>
                {services[0] && services[0].price ? (
                  <strong className={s.priceStarting}>Από {services[0].price}</strong>
                ) : null}
              </div>
              <ul className={s.priceList}>
                {services.map((item, i) => (
                  <li className={s.priceItem} key={i}>
                    <span className={s.priceName}>
                      {item.title}
                      {item.duration ? <span className={s.priceDuration}> · {item.duration}</span> : null}
                    </span>
                    <span className={s.priceDivider} aria-hidden='true'></span>
                    {item.price ? <strong className={s.priceValue}>{item.price}</strong> : null}
                  </li>
                ))}
              </ul>
            </div>
          </section>
        ) : null}

        <section id='contact' className={s.section}>
          <div className={s.sectionInner}>
            <p className={s.eyebrow}>Επικοινωνία</p>
            <h2 className={s.sectionTitle}>{d.CTA_TITLE || 'Πες ένα γεια'}</h2>
            <div className={s.contactGrid}>
              <div className={s.contactInfo}>
                {d.PHONE && phoneHref ? (
                  <a className={s.contactLink} href={phoneHref}>{d.PHONE}</a>
                ) : null}
                {d.DOMAIN ? (
                  <a className={s.contactDomain} href={'https://' + d.DOMAIN} target='_blank' rel='noreferrer'>{d.DOMAIN}</a>
                ) : null}
                {d.AREAS ? <p className={s.contactArea}>{d.AREAS}</p> : null}
                {d.TRADE || d.CITY ? (
                  <p className={s.contactMeta}>
                    {d.TRADE ? <span>{d.TRADE}</span> : null}
                    {d.TRADE && d.CITY ? ' · ' : null}
                    {d.CITY ? <span>{d.CITY}</span> : null}
                    {d.POSTCODE ? <span> {d.POSTCODE}</span> : null}
                  </p>
                ) : null}
                <SocialLinks data={d} className={s.social} />
              </div>
              <div className={s.openWrap}>
                <div className={s.openCard}>
                  <h3>Ανοιχτά καθημερινά</h3>
                  {d.HOURS ? <p className={s.openHours}>{d.HOURS}</p> : null}
                </div>
              </div>
            </div>
            <div className={s.findUs}>
              <FindUs data={d} />
            </div>
          </div>
        </section>
      </main>

      <footer className={s.footer}>
        <div className={s.footerInner}>
          {d.YEAR || d.NAME ? <p>© {d.YEAR || ''} {d.NAME || ''}. Με επιφύλαξη παντός δικαιώματος.</p> : null}
          <a href='#home' className={s.backTop}>Επιστροφή στην αρχή</a>
        </div>
      </footer>
    </div>
  )
}
