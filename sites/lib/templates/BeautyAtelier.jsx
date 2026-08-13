import s from './BeautyAtelier.module.css'
import Brand from './Brand'
import FindUs from './FindUs'

export default function BeautyAtelier({ data: d }) {
  const tel = `tel:+${d.PHONE_INTL}`
  const booking = d.BOOKING_URL || tel
  const gallery = d.gallery || []
  // Το «Επαγγελματικά προϊόντα» ήταν ισχυρισμός για προϊόντα που κανείς δεν είχε
  // δηλώσει. Η λωρίδα δείχνει πρώτα δηλωμένα στοιχεία (ώρες, περιοχές) και μετά
  // μόνο μη-επαληθεύσιμο ΥΦΟΣ, όχι γεγονότα.
  const proof = d.PROOF_ITEMS || [
    d.HOURS, d.AREAS || d.CITY, 'Με ραντεβού', 'Φροντίδα στη λεπτομέρεια',
  ].filter(Boolean).slice(0, 4)
  return <div className={s.root}>
    <nav className={s.nav} aria-label="Κύρια πλοήγηση"><a href="#top" className={s.brandLink}><Brand data={d} className={s.brand}/></a><div className={s.navLinks}><a href="#services">Υπηρεσίες</a><a href="#work">Έργα</a><a href="#find-us">Επίσκεψη</a></div><a href={booking} className={s.book}>Κλείσε ραντεβού</a></nav>
    <header id="top" className={`${s.hero} ${d.HERO_IMAGE ? '' : s.heroNoPhoto}`}>
      {d.HERO_IMAGE && <img className={s.heroImage} src={d.HERO_IMAGE} alt={`${d.NAME} — ${d.TRADE}`}/>}<div className={s.heroShade}/>
      <div className={s.heroContent}><p className={s.kicker}>{d.KICKER || `${d.TRADE} · ${d.CITY}`}</p><h1>{d.HERO_TITLE || d.NAME}</h1><p className={s.tagline}>{d.TAGLINE}</p><div className={s.heroActions}><a href={booking} className={s.primary}>Κλείσε ραντεβού</a><a href="#services" className={s.secondary}>Δες τις υπηρεσίες</a></div></div>
      <span className={s.heroIndex}>Beauty atelier / {d.CITY}</span>
    </header>
    <section className={s.proof} aria-label="Γιατί να μας επιλέξεις">{proof.map((item,i)=><span key={i}>{item}</span>)}</section>
    <section id="services" className={s.services}>
      <div className={s.sectionIntro}><p className={s.eyebrow}>Menu υπηρεσιών</p><h2>{d.SERVICES_TITLE || 'Φροντίδα σχεδιασμένη για εσένα.'}</h2><p>{d.INTRO}</p></div>
      <div className={s.serviceList}>{d.services?.map((service,i)=><a href={booking} className={s.service} key={i}><span className={s.serviceNum}>{service.num || String(i+1).padStart(2,'0')}</span><span className={s.serviceCopy}><strong>{service.title}</strong><small>{service.desc}</small></span>{(service.duration || service.price) && <span className={s.serviceMeta}>{service.duration}{service.duration && service.price ? ' · ' : ''}{service.price}</span>}<span className={s.serviceArrow}>↗</span></a>)}</div>
    </section>
    {gallery.length>0 && <section id="work" className={s.work}><div className={s.workHead}><p className={s.eyebrow}>Selected work</p><h2>Η λεπτομέρεια κάνει τη διαφορά.</h2></div><div className={s.gallery}>{gallery.slice(0,6).map((item,i)=><figure key={i} className={s[`gallery${i%4+1}`]}><img src={item.image} alt={item.title || `${d.NAME} έργο ${i+1}`} loading="lazy"/><figcaption><span>{item.title}</span><small>{item.sub}</small></figcaption></figure>)}</div></section>}
    <section id="story" className={s.story}><div className={s.storyVisual}>{d.STORY_IMAGE?<img src={d.STORY_IMAGE} alt={`${d.NAME} — ο χώρος μας`} loading="lazy"/>:<span>{d.HERO_WORD || 'atelier'}</span>}</div><div className={s.storyCopy}><p className={s.eyebrow}>Η εμπειρία</p><h2>{d.STORY_TITLE}</h2>{d.story?.map((item,i)=><p key={i}>{item.p}</p>)}<a href={booking} className={s.textLink}>Κλείσε τη δική σου ώρα ↗</a></div></section>
    <section id="contact" className={s.finalCta}><p className={s.eyebrow}>Το επόμενο ραντεβού είναι δικό σου</p><h2>{d.CTA_TITLE || 'Ας δημιουργήσουμε κάτι όμορφο.'}</h2><a href={booking}>{d.BOOKING_URL?'Κλείσε online':`Κάλεσε ${d.PHONE}`}</a><div><span>{d.HOURS}</span><span>{d.AREAS}</span></div></section>
    <FindUs data={d}/><footer className={s.footer}><Brand data={d} className={s.footerBrand}/><span>© {d.YEAR} · {d.CITY} · Site από Vitrina</span></footer>
  </div>
}
