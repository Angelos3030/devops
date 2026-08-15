import s from './PropertyAtlas.module.css'
import Brand from './Brand'
import FindUs from './FindUs'

export default function PropertyAtlas({ data: d }) {
  const tel = `tel:+${d.PHONE_INTL}`
  const services = Array.isArray(d.services) ? d.services : []
  const gallery = (Array.isArray(d.gallery) ? d.gallery : []).filter((x)=>x?.image)
  const listings = (gallery.length ? gallery : services).slice(0,6)
  return <div className={s.root}>
    <nav className={s.nav}><a href="#top"><Brand data={d}/></a><div><a href="#listings">Ακίνητα</a><a href="#services">Υπηρεσίες</a><a href="#find-us">Περιοχή</a></div><a className={s.enquire} href={tel}>Επικοινωνία</a></nav>
    <header id="top" className={s.hero}><div className={s.copy}><p>{d.KICKER || `${d.TRADE} · ${d.CITY}`}</p><h1>{d.HERO_TITLE || d.TAGLINE || d.NAME}</h1><span>{d.INTRO}</span><a href="#listings">Ανακάλυψε επιλογές ↓</a></div><div className={s.map} aria-label="Περιοχή εξυπηρέτησης"><i/><i/><i/><i/><strong>{d.CITY}</strong></div></header>
    <main>
      <section id="listings" className={s.listings}><header><p>Selected places</p><h2>{d.GALLERY_TITLE || 'Χώροι που αξίζει να γνωρίσεις.'}</h2></header><div>{listings.map((x,i)=><article key={i}>{x.image ? <img src={x.image} alt={x.title || `${d.NAME} ακίνητο ${i+1}`} loading="lazy"/> : <div className={s.listingFallback}><span>{String(i+1).padStart(2,'0')}</span></div>}<footer><span>{x.title || `Επιλογή ${i+1}`}</span><b>{x.sub || x.desc || d.CITY}</b><a href={tel} aria-label={`Πληροφορίες για ${x.title || `επιλογή ${i+1}`}`}>↗</a></footer></article>)}</div></section>
      <section id="services" className={s.services}><header><p>Πώς βοηθάμε</p><h2>{d.SERVICES_TITLE || 'Από την αναζήτηση έως το επόμενο βήμα.'}</h2></header><ol>{services.map((x,i)=><li key={i}><span>{String(i+1).padStart(2,'0')}</span><h3>{x.title}</h3><p>{x.desc}</p></li>)}</ol></section>
      <section className={s.cta}><div><p>{d.CTA_TITLE || 'Πες μας τι αναζητάς.'}</p><span>{d.AREAS || d.CITY}</span></div><a href={tel}>{d.PHONE}</a></section>
      <FindUs data={d}/>
    </main>
    <footer className={s.footer}><Brand data={d}/><span>{d.CITY} · {d.YEAR}</span><span>Site από Vitrina</span></footer>
  </div>
}
