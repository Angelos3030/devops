import s from './EleganceSalon.module.css'
import Brand from './Brand'
import FindUs from './FindUs'

export default function EleganceSalon({ data: d }) {
  const tel = `tel:+${d.PHONE_INTL}`
  const book = d.BOOKING_URL || tel
  const services = Array.isArray(d.services) ? d.services : []
  const gallery = (Array.isArray(d.gallery) ? d.gallery : []).filter((item) => item?.image)
  return <div className={s.root}>
    <nav className={s.nav}><a href="#top"><Brand data={d}/></a><div><a href="#services">Υπηρεσίες</a><a href="#work">Lookbook</a><a href="#find-us">Επίσκεψη</a></div><a className={s.book} href={book}>Ραντεβού</a></nav>
    <header id="top" className={`${s.hero} ${gallery.length ? '' : s.noPhoto}`}>
      <div className={s.heroCopy}><p>{d.KICKER || `${d.TRADE} · ${d.CITY}`}</p><h1>{d.HERO_TITLE || d.NAME}</h1><span>{d.TAGLINE}</span><a href={book}>{d.PRIMARY_CTA || 'Κλείσε ραντεβού'}</a></div>
      <div className={s.heroMedia}>{d.HERO_IMAGE ? <img src={d.HERO_IMAGE} alt={`${d.NAME} — ${d.TRADE}`}/> : <div className={s.monogram}>{d.NAME?.slice(0, 2)}</div>}<i>01</i></div>
    </header>
    <main>
      <section id="services" className={s.services}><header><p>Service ritual</p><h2>{d.SERVICES_TITLE || 'Η φροντίδα, όπως τη θέλεις.'}</h2></header><div className={s.serviceList}>{services.map((item, i)=><article key={i}><span>{String(i+1).padStart(2,'0')}</span><div><h3>{item.title}</h3><p>{item.desc}</p></div>{(item.price || item.duration) && <small>{[item.duration,item.price].filter(Boolean).join(' · ')}</small>}<a href={book} aria-label={`${item.title}: ραντεβού`}>↗</a></article>)}</div></section>
      {gallery.length > 0 && <section id="work" className={s.lookbook}><div><p>Selected looks</p><h2>Λεπτομέρειες που σε εκφράζουν.</h2></div>{gallery.slice(0,4).map((item,i)=><figure key={i}><img src={item.image} alt={item.title || `${d.NAME} look ${i+1}`} loading="lazy"/><figcaption>{item.title}</figcaption></figure>)}</section>}
      <section className={s.story}><strong>{d.HERO_WORD || 'YOU'}</strong><div><p>Η εμπειρία</p><h2>{d.STORY_TITLE || `Μια επίσκεψη στο ${d.NAME}`}</h2>{(d.story || []).slice(0,3).map((item,i)=><p key={i}>{item.p}</p>)}<a href={book}>Κλείσε τη δική σου ώρα ↗</a></div></section>
      <section className={s.cta}><p>{d.HOURS}</p><h2>{d.CTA_TITLE || 'Η επόμενη αλλαγή ξεκινά εδώ.'}</h2><a href={book}>{d.BOOKING_URL ? 'Κλείσε online' : d.PHONE}</a></section>
      <FindUs data={d}/>
    </main>
    <footer className={s.footer}><Brand data={d}/><span>{d.CITY} · {d.YEAR}</span><span>Site από Vitrina</span></footer>
  </div>
}
