import s from './GymsoFitness.module.css'
import Brand from './Brand'
import FindUs from './FindUs'
import SocialLinks from './SocialLinks'

export default function GymsoFitness({ data: d }) {
  return (
    <div className={s.root}>
      <nav className={s.nav} aria-label="Κύρια πλοήγηση">
        <div className={s.navIn}>
          <a href="#home" className={s.logo}><Brand data={d} className={s.brand} dark /></a>
          <div className={s.navLinks}>
            <a href="#home">Αρχική</a>
            <a href="#about">Σχετικά</a>
            <a href="#classes">Μαθήματα</a>
            <a href="#contact">Επικοινωνία</a>
          </div>
        </div>
      </nav>

      <header id="home" className={s.hero}>
        <div
          className={s.heroBg}
          style={{ backgroundImage: `url(${d.gallery?.[0]?.image || d.HERO_IMAGE})` }}
        />
        <div className={s.heroOverlay} />
        <div className={s.heroInner}>
          <p className={s.heroKicker}>{d.KICKER}</p>
          <h1 className={s.heroTitle}>{d.HERO_WORD}</h1>
          <div className={s.heroCtas}>
            <a href="#contact" className={`${s.btn} ${s.btnPrimary}`}>{d.CTA_TITLE}</a>
            <a href="#about" className={`${s.btn} ${s.btnOutline}`}>Μάθετε περισσότερα</a>
          </div>
        </div>
      </header>

      <section className={s.feature} id="feature">
        <div className={s.container}>
          <div className={s.featureGrid}>
            <div className={s.featureText}>
              <h2 className={s.headingLight}>{d.STORY_TITLE}</h2>
              <p className={s.paragraphLight}>{d.INTRO}</p>
              <a href="#contact" className={`${s.btn} ${s.btnPrimary}`}>{d.CTA_TITLE}</a>
            </div>
            <div className={s.hoursCard}>
              <h3 className={s.headingLight}>Ωράριο Λειτουργίας</h3>
              <p className={s.hoursText}>{d.HOURS}</p>
            </div>
          </div>
        </div>
      </section>

      <section className={s.about} id="about">
        <div className={s.container}>
          <div className={s.aboutGrid}>
            <div className={s.aboutText}>
              <h2 className={s.headingDark}>{d.STORY_TITLE}</h2>
              {d.story?.map((block, i) => (
                <p key={i} className={s.paragraphDark}>{block.p}</p>
              ))}
              <p className={s.paragraphDark}>{d.INTRO}</p>
            </div>
            <div className={s.aboutImageWrapper}>
              <img
                src={d.STORY_IMAGE || d.gallery?.[1]?.image}
                alt={d.gallery?.[1]?.title || d.NAME}
                className={s.aboutImage}
              />
            </div>
          </div>
        </div>
      </section>

      <section className={s.classes} id="classes">
        <div className={s.container}>
          <div className={s.sectionHeader}>
            <p className={s.sectionKicker}>{d.KICKER}</p>
            <h2 className={s.headingDark}>{d.TAGLINE || 'Τα Μαθήματά μας'}</h2>
          </div>
          <div className={s.classGrid}>
            {d.services?.map((service, i) => {
              const img = d.gallery?.[i % d.gallery.length]?.image || d.HERO_IMAGE;
              const alt = d.gallery?.[i % d.gallery.length]?.title || service.title;
              return (
                <article key={service.title || i} className={s.classCard}>
                  <div className={s.classImageWrap}>
                    <img src={img} alt={alt} className={s.classImage} />
                  </div>
                  <div className={s.classInfo}>
                    <h3 className={s.classTitle}>{service.title}</h3>
                    <p className={s.classDesc}>{service.desc}</p>
                    <span className={s.classPrice}>{service.price}</span>
                    <span className={s.classDuration}>{service.duration}</span>
                  </div>
                </article>
              );
            })}
          </div>
        </div>
      </section>

      <section className={s.contact} id="contact">
        <div className={s.container}>
          <div className={s.contactGrid}>
            <div className={s.contactForm}>
              <h2 className={s.headingDark}>Επικοινωνήστε μαζί μας</h2>
              <form className={s.form} action="#" method="post">
                <input type="text" className={s.formInput} placeholder="Όνομα" />
                <input type="email" className={s.formInput} placeholder="Email" />
                <textarea className={s.formTextarea} rows="5" placeholder="Μήνυμα" />
                <button type="submit" className={s.formSubmit}>Αποστολή</button>
              </form>
            </div>
            <div className={s.contactInfo}>
              <h2 className={s.headingDark}>Πού θα μας βρείτε</h2>
              <FindUs data={d} />
              <SocialLinks data={d} className={s.socialLinks} />
            </div>
          </div>
        </div>
      </section>

      <footer className={s.footer}>
        <div className={s.container}>
          <p className={s.footerText}>&copy; {d.YEAR || new Date().getFullYear()} {d.NAME}. All rights reserved.</p>
          <p className={s.footerText}>Τηλέφωνο: <a href={`tel:${d.PHONE_INTL}`}>{d.PHONE}</a></p>
        </div>
      </footer>
    </div>
  );
}
