import s from './Cinematic.module.css'
import Brand from './Brand'

// Cinematic Residence: editorial architecture portfolio for interiors, homes and
// premium craft. Images lead, while every image-dependent block has a text-first
// fallback so the theme remains complete before the client supplies photography.
export default function Cinematic({ data: d }) {
  const tel = `tel:+${d.PHONE_INTL}`
  const projects = d.gallery?.filter((item) => item?.image).slice(0, 4) || []

  return (
    <div className={s.root}>
      <header id="top" className={`${s.hero} ${d.HERO_IMAGE ? '' : s.heroNoImage}`}>
        {d.HERO_IMAGE && <img className={s.heroImage} src={d.HERO_IMAGE} alt="" aria-hidden="true" />}
        <div className={s.shade} aria-hidden="true" />
        <nav className={s.nav} aria-label="Κύρια πλοήγηση">
          <a className={s.brand} href="#top" aria-label={`${d.NAME} — αρχική`}><Brand data={d} dark /></a>
          <div className={s.navLinks}>
            <a href="#projects">Έργα</a>
            <a href="#services">Υπηρεσίες</a>
            <a href="#contact">Επικοινωνία</a>
          </div>
          <a className={s.navCall} href={tel}>Κλήση</a>
        </nav>

        <div className={s.heroCopy}>
          <span className={s.kicker}>{d.KICKER}</span>
          <h1>{d.TAGLINE || d.NAME}</h1>
          <p>{d.TRADE} · {d.AREAS}</p>
          <a className={s.primary} href={tel}>Συζήτησε το έργο σου</a>
        </div>
        <span className={s.scrollCue}>Επιλεγμένα έργα <i aria-hidden="true" /></span>
      </header>

      <main>
        <section id="projects" className={s.projects} aria-labelledby="projects-title">
          <header className={s.sectionHead}>
            <span>01 / Έργα</span>
            <h2 id="projects-title">Χώροι με καθαρή ταυτότητα</h2>
          </header>

          {projects.length > 0 ? (
            <div className={s.projectList}>
              {projects.map((project, index) => (
                <article className={s.project} key={`${project.image}-${index}`}>
                  <figure><img src={project.image} alt={project.title || `Έργο ${index + 1}`} loading="lazy" /></figure>
                  <div className={s.projectMeta}>
                    <span>{String(index + 1).padStart(2, '0')}</span>
                    <h3>{project.title}</h3>
                    {project.sub && <p>{project.sub}</p>}
                  </div>
                </article>
              ))}
            </div>
          ) : (
            <div className={s.projectFallback}>
              {d.services?.slice(0, 3).map((service, index) => (
                <article key={index}>
                  <span>{String(index + 1).padStart(2, '0')}</span>
                  <h3>{service.title}</h3>
                  <p>{service.desc}</p>
                </article>
              ))}
            </div>
          )}
        </section>

        <section id="services" className={s.services} aria-labelledby="services-title">
          <div className={s.serviceIntro}>
            <span>02 / Υπηρεσίες</span>
            <h2 id="services-title">Από την ιδέα μέχρι την τελευταία λεπτομέρεια.</h2>
          </div>
          <ol className={s.serviceList}>
            {d.services?.map((service, index) => (
              <li key={index}>
                <span>{service.num || String(index + 1).padStart(2, '0')}</span>
                <div><h3>{service.title}</h3><p>{service.desc}</p></div>
              </li>
            ))}
          </ol>
        </section>

        <section className={s.story} aria-labelledby="story-title">
          <span>03 / Προσέγγιση</span>
          <div>
            <h2 id="story-title">{d.STORY_TITLE}</h2>
            {d.story?.map((paragraph, index) => <p key={index}>{paragraph.p}</p>)}
          </div>
        </section>

        <section id="contact" className={s.contact} aria-labelledby="contact-title">
          <span>{d.CITY} · {d.HOURS}</span>
          <h2 id="contact-title">{d.CTA_TITLE}</h2>
          <a href={tel}>{d.PHONE}<span aria-hidden="true">↗</span></a>
        </section>
      </main>

      <footer className={s.footer}><span>© {d.YEAR} {d.NAME}</span><span>Site από Vitrina</span></footer>
    </div>
  )
}
