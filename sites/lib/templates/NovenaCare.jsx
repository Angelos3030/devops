import s from './NovenaCare.module.css'
import Brand from './Brand'
import FindUs from './FindUs'

export default function NovenaCare({ data: d }) {
  const tel = `tel:+${d.PHONE_INTL}`
  const book = d.BOOKING_URL || tel
  const services = Array.isArray(d.services) ? d.services : []
  const gallery = (Array.isArray(d.gallery) ? d.gallery : []).filter((x)=>x?.image)
  const proof = [d.HOURS, d.AREAS || d.CITY, ...(d.PROOF_ITEMS || [])].filter(Boolean).slice(0,3)
  return <div className={s.root}>
    <div className={s.top}><span>{d.HOURS}</span><a href={tel}>{d.PHONE}</a></div>
    <nav className={s.nav}><a href="#top"><Brand data={d}/></a><div><a href="#services">Υπηρεσίες</a><a href="#approach">Προσέγγιση</a><a href="#find-us">Επίσκεψη</a></div><a className={s.appointment} href={book}>Ραντεβού</a></nav>
    <header id="top" className={s.hero}><div className={s.copy}><p>{d.KICKER || `${d.TRADE} · ${d.CITY}`}</p><h1>{d.HERO_TITLE || d.NAME}</h1><span>{d.TAGLINE}</span><div><a href={book}>{d.PRIMARY_CTA || 'Κλείσε ραντεβού'}</a><a href="#services">Δες τις υπηρεσίες</a></div></div><figure className={d.HERO_IMAGE ? '' : s.medicalMark}>{d.HERO_IMAGE ? <img src={d.HERO_IMAGE} alt={`${d.NAME} — ${d.TRADE}`}/> : <><i/><i/></>}</figure></header>
    <main>
      <section className={s.proof}>{proof.map((x,i)=><div key={i}><b>{String(i+1).padStart(2,'0')}</b><span>{x}</span></div>)}</section>
      <section id="services" className={s.services}><header><p>Πώς μπορούμε να βοηθήσουμε</p><h2>{d.SERVICES_TITLE || 'Φροντίδα με καθαρή ενημέρωση.'}</h2></header><div className={s.grid}>{services.map((x,i)=><article key={i}><span>{String(i+1).padStart(2,'0')}</span><h3>{x.title}</h3><p>{x.desc}</p><a href={book}>Ραντεβού ↗</a></article>)}</div></section>
      <section id="approach" className={s.approach}>{gallery[0] && <figure><img src={gallery[0].image} alt={gallery[0].title || `${d.NAME} — ο χώρος`} loading="lazy"/></figure>}<div><p>Η προσέγγισή μας</p><h2>{d.STORY_TITLE || 'Ο άνθρωπος πριν από τη διαδικασία.'}</h2>{(d.story || []).slice(0,3).map((x,i)=><p key={i}>{x.p}</p>)}<a href={book}>Μίλησε μαζί μας</a></div></section>
      <section className={s.call}><div><p>{d.CTA_TITLE || 'Χρειάζεσαι ραντεβού;'}</p><h2>{d.PHONE}</h2></div><a href={book}>{d.PRIMARY_CTA || 'Επικοινώνησε'}</a></section>
      <FindUs data={d}/>
    </main>
    <footer className={s.footer}><Brand data={d}/><span>{d.TRADE} · {d.CITY}</span><span>Site από Vitrina</span></footer>
  </div>
}
