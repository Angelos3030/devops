import Brand from './Brand'
import FindUs from './FindUs'
import { capabilityData } from '../capabilities/contracts'
import { PriceBoard, ServiceAreaChecker } from '../capabilities/CapabilityWidgets'
import s from './CapabilitySystems.module.css'

const phoneHref = (d) => d.PHONE_INTL ? `tel:+${d.PHONE_INTL}` : '#contact'
const heroImage = (d) => d.HERO_IMAGE || d.gallery?.[0]?.image || ''
const galleryImage = (d, index) => d.gallery?.[index]?.image || heroImage(d)

function BrandNav({ d, mode = 'light' }) {
  return <nav className={`${s.nav} ${s[mode]}`}>
    <a href="#top" aria-label="Αρχική"><Brand data={d} className={s.brand} /></a>
    <div><a href="#services">Υπηρεσίες</a><a href="#contact">Επικοινωνία</a></div>
    <a className={s.navCta} href={phoneHref(d)}>{d.PHONE || 'Κάλεσε τώρα'}</a>
  </nav>
}

function Contact({ d, compact = false }) {
  return <section id="contact" className={`${s.contact} ${compact ? s.contactCompact : ''}`}>
    <span>{d.CITY || d.AREAS || 'Επικοινωνία'}</span>
    <h2>{d.CTA_TITLE || 'Πες μας τι χρειάζεσαι.'}</h2>
    <a href={phoneHref(d)}>{d.PHONE || 'Στοιχεία επικοινωνίας'} <b>↗</b></a>
  </section>
}

export function AreaFirst({ data: d }) {
  const c = capabilityData(d)
  return <main id="top" className={`${s.root} ${s.area}`}>
    <div className={s.areaTop}>Άμεση εξυπηρέτηση στην περιοχή σου</div>
    <BrandNav d={d} />
    <header className={s.areaHero}>
      {heroImage(d) && <img src={heroImage(d)} alt="" />}
      <div className={s.areaShade} />
      <div className={s.areaCopy}><span>{d.KICKER || d.TRADE}</span><h1>{d.TAGLINE}</h1><p>{d.INTRO}</p><a href="#availability">Έλεγξε διαθεσιμότητα</a></div>
    </header>
    <section id="availability" className={s.availability}><div><b>Χρειάζεσαι βοήθεια;</b><span>Έλεγξε περιοχή και υπηρεσία σε λίγα δευτερόλεπτα.</span></div><ServiceAreaChecker config={c.serviceArea} services={c.services} /></section>
    <section id="services" className={s.areaServices}><header><span>Υπηρεσίες</span><h2>Έτοιμοι όταν μας χρειαστείς.</h2></header><div>{c.services.slice(0,6).map((x,i)=><article key={x.id}><b>{String(i+1).padStart(2,'0')}</b><h3>{x.name}</h3><p>{x.shortDescription}</p><a href={phoneHref(d)}>Ζήτησε εκτίμηση ↗</a></article>)}</div></section>
    <section className={s.areaProof}><strong>Καθαρή ενημέρωση</strong><strong>Συνέπεια στο ραντεβού</strong><strong>Εξυπηρέτηση στην περιοχή σου</strong></section>
    <Contact d={d}/><FindUs data={d}/>
  </main>
}

export function PriceFirst({ data: d }) {
  const c = capabilityData(d)
  return <main id="top" className={`${s.root} ${s.price}`}>
    <BrandNav d={d} />
    <header className={s.priceHero} style={heroImage(d) ? {backgroundImage:`linear-gradient(90deg,rgba(35,25,19,.72),rgba(35,25,19,.2)),url(${heroImage(d)})`} : undefined}>
      <div><span>{d.KICKER || d.TRADE} · {d.CITY}</span><h1>{d.NAME}</h1><p>{d.TAGLINE}</p><a href="#services">Δες υπηρεσίες & τιμές</a></div>
    </header>
    <section className={s.priceIntro}><span>Τι προσφέρουμε</span><h2>Διάλεξε αυτό που σου ταιριάζει.</h2><p>{d.INTRO}</p></section>
    <div id="services" className={s.priceBoard}><PriceBoard services={c.services} booking={c.booking}/></div>
    <section className={s.priceGallery}>{[0,1,2].map((i)=>galleryImage(d,i)&&<img key={i} src={galleryImage(d,i)} alt={d.gallery?.[i]?.title || ''}/>)}</section>
    <Contact d={d}/><FindUs data={d}/>
  </main>
}

export function ChapterSnap({ data:d }) {
  const services=capabilityData(d).services
  const chapters=[
    {n:'01',title:d.TAGLINE,copy:d.INTRO,image:heroImage(d)},
    ...services.slice(0,3).map((x,i)=>({n:`0${i+2}`,title:x.name,copy:x.shortDescription,image:galleryImage(d,i)})),
    {n:'05',title:d.CTA_TITLE,copy:d.CITY || d.AREAS,image:galleryImage(d,3)},
  ]
  return <main id="top" className={`${s.root} ${s.chapters}`}>
    <BrandNav d={d} mode="floating" />
    <aside className={s.chapterDots}>{chapters.map(x=><a key={x.n} href={`#chapter-${x.n}`}>{x.n}</a>)}</aside>
    {chapters.map((x,i)=><section id={`chapter-${x.n}`} className={s.chapter} key={x.n}>
      <div className={s.chapterColor}><span>{x.n} / {i===0 ? d.TRADE : 'Κεφάλαιο'}</span>{i===0 ? <h1>{x.title}</h1> : <h2>{x.title}</h2>}<p>{x.copy}</p><a href={i===chapters.length-1?phoneHref(d):`#chapter-${chapters[Math.min(i+1,chapters.length-1)].n}`}>{i===chapters.length-1 ? (d.PHONE || 'Επικοινωνία') : 'Επόμενο'} ↘</a></div>
      <div className={s.chapterVisual}>{x.image ? <img src={x.image} alt=""/> : <b>{x.n}</b>}</div>
    </section>)}
  </main>
}

export function DirectoryIndex({ data:d }) {
  const services=capabilityData(d).services
  const rows=[...services.map((x,i)=>({n:String(i+1).padStart(2,'0'),title:x.name,body:x.shortDescription,meta:x.category})),{n:String(services.length+1).padStart(2,'0'),title:'Σχετικά',body:d.INTRO,meta:d.CITY},{n:String(services.length+2).padStart(2,'0'),title:'Επικοινωνία',body:d.CTA_TITLE,meta:d.PHONE}]
  return <main id="top" className={`${s.root} ${s.directory}`}>
    <header className={s.indexHeader}><Brand data={d}/><nav><a href="#services">Κατάλογος</a><a href="#contact">Επικοινωνία</a></nav><span>{d.CITY} · {d.YEAR}</span></header>
    <section className={s.indexTitle}><span>Ευρετήριο υπηρεσιών</span><h1>{d.NAME}</h1><p>{d.TAGLINE}</p></section>
    <section id="services" className={s.indexList}>{rows.map(x=><details key={x.n}><summary><span>{x.n}</span><strong>{x.title}</strong><small>{x.meta}</small><i>+</i></summary><p>{x.body}</p></details>)}</section>
    <footer id="contact" className={s.indexFooter}><span>{d.ADDRESS || d.CITY}</span><a href={phoneHref(d)}>{d.PHONE || 'Επικοινωνία'}</a><span>{d.HOURS}</span></footer>
  </main>
}

export function HorizontalStory({ data: d }) {
  const services=capabilityData(d).services
  const scenes=[{k:'00',title:d.NAME,copy:d.TAGLINE,image:heroImage(d)},...services.slice(0,4).map((x,i)=>({k:`0${i+1}`,title:x.name,copy:x.shortDescription,image:galleryImage(d,i)})),{k:'05',title:d.CTA_TITLE,copy:d.PHONE,image:galleryImage(d,4)}]
  return <main id="top" className={`${s.root} ${s.horizontal}`}>
    <BrandNav d={d} mode="dark" />
    <div className={s.filmstrip} tabIndex="0" aria-label="Οριζόντια παρουσίαση">
      {scenes.map((x,i)=><section className={s.filmScene} key={x.k}>
        <div className={s.filmMeta}><span>{x.k}</span><span>{i===0?d.TRADE:'Υπηρεσία'}</span></div>
        <div className={s.filmImage}>{x.image ? <img src={x.image} alt=""/> : <span>{x.k}</span>}</div>
        {i===0 ? <h1>{x.title}</h1> : <h2>{x.title}</h2>}<p>{x.copy}</p>{i===scenes.length-1&&<a href={phoneHref(d)}>Κάλεσε τώρα ↗</a>}
      </section>)}
    </div>
    <div className={s.filmHint}>Σύρε οριζόντια <span>→</span></div>
  </main>
}

export function VerticalSnap({ data:d }) {
  const services=capabilityData(d).services
  const slides=[{title:d.TAGLINE,copy:d.INTRO,image:heroImage(d)},...services.slice(0,4).map((x,i)=>({title:x.name,copy:x.shortDescription,image:galleryImage(d,i)}))]
  return <main id="top" className={`${s.root} ${s.snap}`}>
    <header className={s.snapFrame}><Brand data={d}/><span>{d.TRADE} · {d.CITY}</span><a href={phoneHref(d)}>{d.PHONE || 'Επικοινωνία'}</a></header>
    <nav className={s.snapNav}>{slides.map((x,i)=><a key={x.title} href={`#snap-${i}`}>{String(i+1).padStart(2,'0')} <span>{x.title}</span></a>)}</nav>
    <div className={s.snapSlides}>{slides.map((x,i)=><section id={`snap-${i}`} key={x.title} style={x.image?{backgroundImage:`linear-gradient(90deg,rgba(9,12,18,.35),rgba(9,12,18,.05)),url(${x.image})`}:undefined}><div><span>0{i+1}</span>{i===0 ? <h1>{x.title}</h1> : <h2>{x.title}</h2>}<p>{x.copy}</p>{i===0&&<a href="#snap-1">Ανακάλυψε ↓</a>}</div></section>)}</div>
    <span className={s.snapHint}>Scroll / Drag ↓</span>
  </main>
}
