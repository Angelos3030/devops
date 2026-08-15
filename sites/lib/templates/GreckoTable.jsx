import s from './GreckoTable.module.css'
import Brand from './Brand'
import FindUs from './FindUs'

export default function GreckoTable({ data: d }) {
  const tel = `tel:+${d.PHONE_INTL}`
  const reserve = d.BOOKING_URL || tel
  const services = Array.isArray(d.services) ? d.services : []
  const gallery = (Array.isArray(d.gallery) ? d.gallery : []).filter((x)=>x?.image)
  return <div className={s.root}>
    <nav className={s.nav}><a href="#top"><Brand data={d}/></a><div><a href="#menu">Μενού</a><a href="#story">Η κουζίνα</a><a href="#find-us">Πού είμαστε</a></div><a className={s.reserve} href={reserve}>Κράτηση</a></nav>
    <header id="top" className={s.hero}>
      {d.HERO_IMAGE && <img src={d.HERO_IMAGE} alt={`${d.NAME} — ${d.TRADE}`}/>}<span className={s.shade}/>
      <div className={s.heroInner}><p>{d.KICKER || `${d.TRADE} · ${d.CITY}`}</p><h1>{d.NAME}</h1><h2>{d.HERO_TITLE || d.TAGLINE}</h2><a href={reserve}>{d.PRIMARY_CTA || 'Κράτησε τραπέζι'}</a></div>
      {!d.HERO_IMAGE && <div className={s.plate} aria-hidden="true"><i/><i/><i/></div>}
    </header>
    <main>
      <section id="menu" className={s.menu}><header><span>Στο τραπέζι</span><h2>{d.SERVICES_TITLE || 'Γεύσεις που φέρνουν την παρέα κοντά.'}</h2><p>{d.INTRO}</p></header><div>{services.map((item,i)=><article key={i}><span>{String(i+1).padStart(2,'0')}</span><h3>{item.title}</h3><p>{item.desc}</p>{item.price && <strong>{item.price}</strong>}</article>)}</div></section>
      <section id="story" className={s.story}>{gallery[0] ? <figure><img src={gallery[0].image} alt={gallery[0].title || `${d.NAME} — γεύσεις`} loading="lazy"/></figure> : <figure className={s.pattern} aria-hidden="true"/>}<div><p>Από την κουζίνα</p><h2>{d.STORY_TITLE || 'Απλά υλικά. Καθαρή γεύση.'}</h2>{(d.story || []).slice(0,3).map((x,i)=><p key={i}>{x.p}</p>)}<a href={reserve}>Κράτηση ↗</a></div></section>
      {gallery.length > 1 && <section className={s.gallery} aria-label="Η ατμόσφαιρά μας">{gallery.slice(1,5).map((x,i)=><figure key={i}><img src={x.image} alt={x.title || `${d.NAME} εικόνα ${i+1}`} loading="lazy"/></figure>)}</section>}
      <section className={s.visit}><div><p>Σήμερα</p><h2>{d.CTA_TITLE || 'Το τραπέζι σε περιμένει.'}</h2></div><div><span>{d.HOURS}</span><span>{d.ADDRESS || d.CITY}</span><a href={tel}>{d.PHONE}</a></div></section>
      <FindUs data={d}/>
    </main>
    <footer className={s.footer}><Brand data={d}/><span>{d.CITY}</span><span>Site από Vitrina</span></footer>
  </div>
}
