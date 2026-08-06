import s from './Living.module.css'
import Brand from './Brand'
import FindUs from './FindUs'

export default function Living({ data: d }) {
  const tel = `tel:+${d.PHONE_INTL}`
  const services = d.services || []
  const gallery = d.gallery || []

  return (
    <div className={s.root}>
      <nav className={s.nav} aria-label="Κύρια πλοήγηση"><a href="#top" className={s.brand}><Brand data={d} /></a><div><a href="#materials">{d.GALLERY_NAV || 'Χώρος'}</a><a href="#services">Υπηρεσίες</a></div><a href={tel} className={s.call}>{d.PRIMARY_CTA || 'Επικοινωνία'}</a></nav>
      <header id="top" className={s.hero}>
        <div className={s.heroCopy}><span className={s.eyebrow}>{d.KICKER}</span><h1>{d.NAME}</h1><p>{d.TAGLINE}</p><a href={tel} className={s.cta}>{d.PRIMARY_CTA || 'Μίλησε μαζί μας'} <span aria-hidden="true">↗</span></a></div>
        {d.HERO_IMAGE ? <figure className={s.heroMedia}><img src={d.HERO_IMAGE} alt={`${d.NAME} — ${d.TRADE}`} /></figure> : <div className={s.materialField} aria-label={`${d.TRADE} — υλικά και τεχνική`}><span /><span /><span /></div>}
        <div className={s.seed} aria-hidden="true" />
      </header>

      <main>
        <section id="materials" className={s.materials}><header><span className={s.eyebrow}>{d.GALLERY_EYEBROW || 'Ο χώρος'}</span><h2>{d.GALLERY_TITLE || 'Μια εμπειρία φτιαγμένη με φροντίδα.'}</h2></header><div className={s.materialGrid}>{gallery.slice(0,3).map((item,i)=><figure key={i}><img src={item.image} alt={item.title} loading="lazy" /><figcaption><span>0{i+1}</span><b>{item.title}</b><small>{item.sub}</small></figcaption></figure>)}{gallery.length===0&&services.slice(0,3).map((item,i)=><article key={i}><span>0{i+1}</span><h3>{item.title}</h3><p>{item.desc}</p></article>)}</div></section>

        <section id="services" className={s.services}><div className={s.serviceIntro}><span className={s.eyebrow}>{d.SERVICES_EYEBROW || 'Οι υπηρεσίες μας'}</span><h2>{d.STORY_TITLE}</h2><p>{d.INTRO || d.TAGLINE}</p></div><div className={s.petals}>{services.map((item,i)=><a href={tel} key={i} className={s.petal}><span>{item.num || String(i+1).padStart(2,'0')}</span><h3>{item.title}</h3><p>{item.desc}</p></a>)}</div></section>

        {gallery.length>3&&<section id="work" className={s.gallery}><header><span className={s.eyebrow}>{d.EXTRA_GALLERY_EYEBROW || 'Η εμπειρία'}</span><h2>{d.EXTRA_GALLERY_TITLE || 'Λεπτομέρειες που σε κάνουν να επιστρέφεις.'}</h2></header><div>{gallery.slice(3).map((item,i)=><figure key={i}><img src={item.image} alt={item.title} loading="lazy" /><figcaption>{item.title}</figcaption></figure>)}</div></section>}

        <section id="story" className={s.story}>{d.STORY_IMAGE&&<figure><img src={d.STORY_IMAGE} alt={`${d.NAME} — η διαδικασία`} loading="lazy" /></figure>}<div><span className={s.eyebrow}>Η φιλοσοφία</span><blockquote>{d.STORY_TITLE}</blockquote>{d.story?.map((item,i)=><p key={i}>{item.p}</p>)}<b>— {d.NAME}, {d.CITY}</b></div></section>
        <section id="contact" className={s.contact}><div className={s.contactRing} aria-hidden="true"/><span>{d.AREAS}</span><h2>{d.CTA_TITLE}</h2><a href={tel}>{d.PHONE}</a><p>{d.HOURS}</p></section>
      </main>
      <FindUs data={d} />
      <footer className={s.footer}><span>© {d.YEAR} {d.NAME}</span><span>{d.TRADE} · {d.CITY}</span><span>Site από Vitrina</span></footer>
    </div>
  )
}
