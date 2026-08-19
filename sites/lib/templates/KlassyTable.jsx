import s from './KlassyTable.module.css'
import Brand from './Brand'
import FindUs from './FindUs'
import SocialLinks from './SocialLinks'

export default function KlassyTable({ data: d }) {
  return (
    <div className={s.root}>
      <nav className={s.nav} aria-label='Κύρια πλοήγηση'>
        <div className={s.navIn}>
          <a href='#home' className={s.logo}><Brand data={d} className={s.brand} dark /></a>
          <div className={s.navLinks}>
            <a href='#home'>Αρχική</a>
            <a href='#story'>Σχετικά</a>
            <a href='#menu'>Μενού</a>
            <a href='#gallery'>Έργα</a>
            <a href='#contact'>Επικοινωνία</a>
          </div>
        </div>
      </nav>

      <header id='home' className={s.hero}>
        <div className={s.heroPanel}>
          <div className={s.heroInner}>
            <Brand data={d} className={s.heroBrand} />
            <h1 className={s.heroTitle}>{d.NAME}</h1>
            <p className={s.heroKicker}>{d.TAGLINE || d.KICKER}</p>
            <a className={s.heroButton} href='#contact'>{d.CTA_TITLE || 'Επικοινωνήστε μαζί μας'}</a>
          </div>
        </div>
        <div className={s.heroSlides}>
          {d.gallery.slice(0, 3).map((item) => (
            <div key={item.title} className={s.heroSlide}>
              <img src={item.image} alt={item.title} />
            </div>
          ))}
        </div>
      </header>

      <section id='story' className={s.about}>
        <div className={s.aboutGrid}>
          <div className={s.aboutText}>
            <p className={s.eyebrow}>Σχετικά</p>
            <h2 className={s.title}>{d.STORY_TITLE}</h2>
            {d.story.map((block) => (
              <p key={block.p.slice(0, 24)} className={s.paragraph}>{block.p}</p>
            ))}
          </div>
          <div className={s.aboutVisual}>
            <div className={s.aboutMain}>
              <img src={d.STORY_IMAGE} alt={d.STORY_TITLE} />
            </div>
            <div className={s.aboutThumbs}>
              {d.gallery.slice(0, 3).map((item) => (
                <img key={item.title} src={item.image} alt={item.title} />
              ))}
            </div>
          </div>
        </div>
      </section>

      <section id='menu' className={s.menu}>
        <div className={s.sectionHead}>
          <p className={s.eyebrow}>Μενού</p>
          <h2 className={s.title}>Επιλογές που ξεχωρίζουν</h2>
        </div>
        <div className={s.menuRow}>
          {d.services.map((item, i) => {
            const img = d.gallery[i];
            return (
              <article key={item.title} className={s.menuCard}>
                {img ? <img className={s.menuImage} src={img.image} alt={img.title} /> : null}
                <span className={s.menuNum}>{item.num}</span>
                <div className={s.menuBody}>
                  <h3 className={s.menuTitle}>{item.title}</h3>
                  <p className={s.menuDesc}>{item.desc}</p>
                  <a className={s.menuLink} href='#contact'>Μάθετε περισσότερα</a>
                </div>
              </article>
            );
          })}
        </div>
      </section>

      <section id='gallery' className={s.gallery}>
        <div className={s.sectionHead}>
          <p className={s.eyebrow}>Έργα</p>
          <h2 className={s.title}>Ο χώρος μας</h2>
        </div>
        <div className={s.galleryGrid}>
          {d.gallery.map((item) => (
            <figure key={item.title} className={s.galleryItem}>
              <img src={item.image} alt={item.title} />
              <figcaption>{item.title}</figcaption>
            </figure>
          ))}
        </div>
      </section>

      <section id='contact' className={s.contact}>
        <div className={s.contactInner}>
          <div className={s.contactInfo}>
            <p className={s.eyebrow}>Επικοινωνία</p>
            <h2 className={s.title}>{d.CTA_TITLE}</h2>
            <FindUs data={d} dark />
          </div>
          <div className={s.contactCard}>
            <h3 className={s.contactCardTitle}>Επισκεφθείτε μας</h3>
            <p className={s.contactCardText}>{d.INTRO}</p>
            <SocialLinks data={d} />
          </div>
        </div>
      </section>

      <footer className={s.footer}>
        <div className={s.footerIn}>
          <Brand data={d} className={s.footerBrand} />
          <p className={s.footerText}>© {d.YEAR} {d.NAME}. Με επιφύλαξη παντός δικαιώματος.</p>
          <SocialLinks data={d} />
        </div>
      </footer>
    </div>
  )
}
