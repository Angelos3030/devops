import s from './BigspringAdvisory.module.css'
import Brand from './Brand'
import FindUs from './FindUs'

export default function BigspringAdvisory({ data: d }) {
  const tel = `tel:+${d.PHONE_INTL}`
  const services = Array.isArray(d.services) ? d.services : []
  const gallery = (Array.isArray(d.gallery) ? d.gallery : []).filter((x)=>x?.image)
  return <div className={s.root}>
    <nav className={s.nav}><a href="#top"><Brand data={d}/></a><div><a href="#services">Υπηρεσίες</a><a href="#method">Προσέγγιση</a><a href="#find-us">Επικοινωνία</a></div><a className={s.contact} href={tel}>Συζήτηση</a></nav>
    <header id="top" className={s.hero}><div><p>{d.KICKER || `${d.TRADE} · ${d.CITY}`}</p><h1>{d.HERO_TITLE || d.TAGLINE || d.NAME}</h1><span>{d.INTRO}</span><a href={tel}>{d.PRIMARY_CTA || 'Κλείσε μια πρώτη συζήτηση'}</a></div><aside><strong>{d.NAME}</strong><span>{d.TRADE}</span><span>{d.AREAS || d.CITY}</span><b>{d.PHONE}</b></aside></header>
    <main>
      <section id="services" className={s.services}><header><p>What we solve</p><h2>{d.SERVICES_TITLE || 'Καθαρή σκέψη για τις αποφάσεις που μετράνε.'}</h2></header><div>{services.map((x,i)=><article key={i}><span>{String(i+1).padStart(2,'0')}</span><h3>{x.title}</h3><p>{x.desc}</p></article>)}</div></section>
      <section id="method" className={s.method}><div><p>Η προσέγγιση</p><h2>{d.STORY_TITLE || 'Ακούμε. Οργανώνουμε. Προχωράμε.'}</h2></div><ol>{(d.story || []).slice(0,4).map((x,i)=><li key={i}><b>{String(i+1).padStart(2,'0')}</b><p>{x.p}</p></li>)}</ol></section>
      <section className={s.signal}>{gallery[0] ? <img src={gallery[0].image} alt={gallery[0].title || `${d.NAME} — επαγγελματικός χώρος`} loading="lazy"/> : <div className={s.graph} aria-hidden="true"><i/><i/><i/><i/></div>}<div><p>{d.CTA_TITLE || 'Η επόμενη σωστή κίνηση.'}</p><a href={tel}>{d.PHONE} ↗</a></div></section>
      <FindUs data={d}/>
    </main>
    <footer className={s.footer}><Brand data={d}/><span>{d.CITY} · {d.YEAR}</span><span>Site από Vitrina</span></footer>
  </div>
}
