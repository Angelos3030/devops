import s from './VexCounter.module.css'
import Brand from './Brand'
import FindUs from './FindUs'

// "Vex Counter" — τοπικό λιανικό, εξειδικευμένο προϊόν, product-first επιχείρηση.
//
// PORT από: https://github.com/themefisher/vex-hugo
// LICENSE: MIT (Themefisher, 2018–present) — επαληθεύτηκε στο αρχείο LICENSE του
// repository. Απαιτείται διατήρηση σημείωσης· βλ. `licenses/THIRD-PARTY.md`.
//
// ΤΙ ΚΡΑΤΗΘΗΚΕ: η product-first ιεραρχία — το προϊόν πριν την εταιρεία. Ο
// τεράστιος τίτλος με μία μόνο δράση, η οριζόντια λωρίδα κατηγοριών, το πλέγμα
// προϊόντων με μεγάλη αρίθμηση, και το κλείσιμο με διεύθυνση αντί για φόρμα:
// σε τοπικό μαγαζί η μετατροπή είναι «πέρνα να το δεις», όχι «στείλε αίτημα».
//
// ΤΙ ΔΕΝ ΜΕΤΑΦΕΡΘΗΚΕ: καμία demo φωτογραφία ή εικονίδιο, κανένα κείμενο. Το
// πρωτότυπο δείχνει τιμές και «bestseller» σήματα — και τα δύο είναι
// ισχυρισμοί που απαγορεύονται χωρίς δεδομένα (docs/ai/DECISIONS.md §D4).

export default function VexCounter({ data: d }) {
  const tel = d.PHONE_INTL ? `tel:+${d.PHONE_INTL}` : ''
  const services = Array.isArray(d.services) ? d.services : []
  const gallery = (Array.isArray(d.gallery) ? d.gallery : []).filter((g) => g?.image)
  const story = Array.isArray(d.story) ? d.story.slice(0, 2) : []
  // Η λωρίδα κατηγοριών βγαίνει από τις ΔΗΛΩΜΕΝΕΣ υπηρεσίες/προϊόντα του πελάτη.
  const strip = services.slice(0, 6).map((x) => x.title)

  return (
    <div className={s.root}>
      <nav className={s.nav} aria-label="Κύρια πλοήγηση">
        <a href="#top" className={s.brandLink}><Brand data={d} className={s.brand} /></a>
        <div className={s.navLinks}>
          <a href="#shelf">Τι θα βρεις</a>
          <a href="#about">Το μαγαζί</a>
          <a href="#find-us">Πού είμαστε</a>
        </div>
        {tel && <a href={tel} className={s.navCall}>{d.PHONE}</a>}
      </nav>

      <header id="top" className={s.hero}>
        <p className={s.eyebrow}>{d.KICKER || [d.TRADE, d.CITY].filter(Boolean).join(' · ')}</p>
        <h1 className={s.title}>{d.HERO_TITLE || d.TAGLINE || d.NAME}</h1>
        {d.INTRO && <p className={s.lede}>{d.INTRO}</p>}
        <div className={s.heroActions}>
          <a href="#shelf" className={s.primary}>Δες τι έχουμε</a>
          {tel && <a href={tel} className={s.ghost}>{d.PRIMARY_CTA || 'Ρώτησε για διαθεσιμότητα'}</a>}
        </div>
        {gallery[0] && (
          <figure className={s.heroFig}>
            <img src={gallery[0].image} alt={gallery[0].title || d.NAME} />
            {gallery[0].illustrative && <figcaption>Ενδεικτική εικόνα</figcaption>}
          </figure>
        )}
      </header>

      {strip.length > 1 && (
        <div className={s.strip} aria-label="Κατηγορίες">
          {strip.map((t) => <span key={t}>{t}</span>)}
        </div>
      )}

      <main>
        <section id="shelf" className={s.shelf}>
          <header className={s.secHead}>
            <p className={s.eyebrow}>{d.SERVICES_EYEBROW || 'Στο ράφι'}</p>
            <h2 className={s.secTitle}>{d.SERVICES_TITLE || 'Τι θα βρεις σε εμάς'}</h2>
          </header>
          <ol className={s.shelfGrid}>
            {services.map((sv, i) => {
              const pic = gallery[i + 1]
              return (
                <li className={s.item} key={sv.title + i}>
                  {pic && (
                    <figure className={s.itemFig}>
                      <img src={pic.image} alt={sv.title} loading="lazy" />
                      {pic.illustrative && <figcaption>Ενδεικτική εικόνα</figcaption>}
                    </figure>
                  )}
                  <div className={s.itemBody}>
                    <span className={s.itemNum}>{String(i + 1).padStart(2, '0')}</span>
                    <h3>{sv.title}</h3>
                    {sv.desc && <p>{sv.desc}</p>}
                  </div>
                </li>
              )
            })}
          </ol>
          {d.SERVICES_TOTAL > services.length && (
            <p className={s.more}>+ {d.SERVICES_TOTAL - services.length} ακόμη στο κατάστημα</p>
          )}
        </section>

        {(story.length > 0 || d.INTRO) && (
          <section id="about" className={s.about}>
            <div className={s.aboutIn}>
              <h2 className={s.aboutTitle}>{d.STORY_TITLE || `Το ${d.NAME}`}</h2>
              {(story.length ? story.map((p) => p.p) : [d.INTRO]).map((text, i) => (
                <p key={i}>{text}</p>
              ))}
            </div>
          </section>
        )}

        <section className={s.visit}>
          <h2>{d.CTA_TITLE || 'Πέρνα από το μαγαζί'}</h2>
          <dl className={s.visitFacts}>
            {(d.AREAS || d.CITY) && <div><dt>Περιοχή</dt><dd>{d.AREAS || d.CITY}</dd></div>}
            {d.HOURS && <div><dt>Ωράριο</dt><dd>{d.HOURS}</dd></div>}
            {d.PHONE && <div><dt>Τηλέφωνο</dt><dd><a href={tel}>{d.PHONE}</a></dd></div>}
          </dl>
        </section>
      </main>

      <FindUs data={d} />
      <footer className={s.footer}>
        © {d.YEAR} {[d.NAME, d.CITY].filter(Boolean).join(' · ')} · Site από Vitrina
      </footer>
    </div>
  )
}
