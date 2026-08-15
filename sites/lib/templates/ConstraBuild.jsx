import s from './ConstraBuild.module.css'
import Brand from './Brand'
import FindUs from './FindUs'

export default function ConstraBuild({ data: d }) {
  const tel = `tel:+${d.PHONE_INTL}`
  const services = Array.isArray(d.services) ? d.services : []
  const gallery = (Array.isArray(d.gallery) ? d.gallery : []).filter((x)=>x?.image)
  return <div className={s.root}>
    <div className={s.utility}><span>{d.AREAS || d.CITY}</span><span>{d.HOURS}</span><a href={tel}>{d.PHONE}</a></div>
    <nav className={s.nav}><a href="#top"><Brand data={d}/></a><div><a href="#services">Εργασίες</a><a href="#projects">Έργα</a><a href="#find-us">Επικοινωνία</a></div><a className={s.quote} href={tel}>Ζήτησε προσφορά</a></nav>
    <header id="top" className={s.hero}>{d.HERO_IMAGE && <img src={d.HERO_IMAGE} alt={`${d.NAME} — ${d.TRADE}`}/>}<span/><div><p>{d.KICKER || `${d.TRADE} · ${d.CITY}`}</p><h1>{d.HERO_TITLE || d.TAGLINE || d.NAME}</h1><a href={tel}>{d.PRIMARY_CTA || 'Μίλησε με τεχνικό'}</a></div><aside><b>01</b><span>{d.AREAS || d.CITY}</span></aside></header>
    <main>
      <section id="services" className={s.services}><header><p>Από το σχέδιο στην παράδοση</p><h2>{d.SERVICES_TITLE || 'Δουλειά που αντέχει.'}</h2><span>{d.INTRO}</span></header><div>{services.map((x,i)=><article key={i}><b>{String(i+1).padStart(2,'0')}</b><h3>{x.title}</h3><p>{x.desc}</p><a href={tel}>Προσφορά ↗</a></article>)}</div></section>
      <section id="projects" className={`${s.projects} ${gallery.length ? '' : s.noProjects}`}><header><p>Επιλεγμένες εργασίες</p><h2>{d.GALLERY_TITLE || 'Λεπτομέρεια σε κάθε στάδιο.'}</h2></header>{gallery.length ? <div>{gallery.slice(0,5).map((x,i)=><figure key={i}><img src={x.image} alt={x.title || `${d.NAME} έργο ${i+1}`} loading="lazy"/><figcaption>{x.title}</figcaption></figure>)}</div> : <ol>{services.slice(0,4).map((x,i)=><li key={i}><span>{String(i+1).padStart(2,'0')}</span>{x.title}</li>)}</ol>}</section>
      <section className={s.band}><p>{d.CTA_TITLE || 'Έχεις έργο στο μυαλό σου;'}</p><a href={tel}>{d.PHONE}</a></section>
      <FindUs data={d}/>
    </main>
    <footer className={s.footer}><Brand data={d}/><span>{d.TRADE} · {d.CITY}</span><span>Site από Vitrina</span></footer>
  </div>
}
