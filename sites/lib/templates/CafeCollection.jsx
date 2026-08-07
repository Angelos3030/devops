import s from './CafeCollection.module.css'
import Brand from './Brand'
import FindUs from './FindUs'

const tel = (d) => `tel:+${d.PHONE_INTL}`
const items = (d, max = 4) => (d.services || []).slice(0, max)
const photos = (d, max = 6) => (d.gallery || []).filter((item) => item?.image).slice(0, max)

function Footer({ d }) {
  return <footer className={s.footer}>© {d.YEAR} {d.NAME} · {d.CITY} · Site από Vitrina</footer>
}

export function BakeryEditorial({ data: d }) {
  const gallery = photos(d)
  return (
    <main className={`${s.root} ${s.editorial}`}>
      <nav className={s.nav}><Brand data={d} className={s.brand} /><div><a href="#menu">Μενού</a><a href="#story">Η ιστορία</a><a href={tel(d)}>{d.PHONE}</a></div></nav>
      <header className={s.editorialHero}>
        {d.HERO_IMAGE && <img src={d.HERO_IMAGE} alt={`${d.NAME} — ${d.TRADE}`} />}
        <div className={s.heroShade} />
        <div className={s.editorialCopy}><span>{d.KICKER}</span><h1>{d.NAME}</h1><p>{d.TAGLINE}</p><a href="#menu">Ανακάλυψε το μενού</a></div>
        <aside><b>Σήμερα</b><span>{d.HOURS}</span><span>{d.CITY}</span></aside>
      </header>
      <section id="menu" className={s.editorialMenu}>
        <header><span>Από τον φούρνο και τον πάγκο</span><h2>{d.SERVICES_TITLE || 'Ό,τι φτιάχνουμε σήμερα'}</h2></header>
        <div>{items(d).map((item, i) => <article key={i}><span>{item.num}</span><h3>{item.title}</h3><p>{item.desc}</p></article>)}</div>
      </section>
      <section className={s.filmstrip}>{gallery.map((item, i) => <figure key={i}><img src={item.image} alt={item.title} loading="lazy" /><figcaption>{item.title}<span>{item.sub}</span></figcaption></figure>)}</section>
      <section id="story" className={s.editorialStory}><div><span>Η ιστορία μας</span><h2>{d.STORY_TITLE}</h2>{d.story?.map((p, i) => <p key={i}>{p.p}</p>)}</div>{d.STORY_IMAGE && <img src={d.STORY_IMAGE} alt={d.NAME} loading="lazy" />}</section>
      <section className={s.bigCta}><p>Καφές, φρέσκο ψωμί και μια θέση για σένα.</p><a href={tel(d)}>Κάλεσέ μας · {d.PHONE}</a></section>
      <FindUs data={d} /><Footer d={d} />
    </main>
  )
}

export function CounterMenu({ data: d }) {
  const gallery = photos(d, 4)
  return (
    <main className={`${s.root} ${s.counter}`}>
      <nav className={s.counterNav}><Brand data={d} className={s.brand} /><span>{d.CITY}</span><a href={tel(d)}>Κάλεσε τώρα</a></nav>
      <header className={s.counterHero}>
        <div className={s.counterIntro}><span>{d.KICKER}</span><h1>{d.TAGLINE}</h1><p>{d.INTRO}</p><div><a href={tel(d)}>Παραγγελία / κράτηση</a><a href="#counter-menu">Δες τι έχουμε ↓</a></div></div>
        <div className={s.counterMosaic}>{gallery.slice(0, 3).map((item, i) => <img key={i} src={item.image} alt={item.title} />)}</div>
      </header>
      <section id="counter-menu" className={s.menuBoard}>
        <header><span>Menu board</span><h2>Απόλαυσέ το όπως σου αρέσει.</h2><p>{d.HOURS}</p></header>
        <div>{items(d).map((item, i) => <article key={i}><b>{String(i + 1).padStart(2, '0')}</b><div><h3>{item.title}</h3><p>{item.desc}</p></div><span>→</span></article>)}</div>
      </section>
      <section className={s.counterProof}><p>Φρέσκο κάθε μέρα</p><p>Στο {d.CITY}</p><p>{d.PHONE}</p></section>
      <section className={s.counterStory}>{d.STORY_IMAGE && <img src={d.STORY_IMAGE} alt={d.NAME} loading="lazy" />}<div><span>Πίσω από τον πάγκο</span><h2>{d.STORY_TITLE}</h2>{d.story?.map((p, i) => <p key={i}>{p.p}</p>)}</div></section>
      <FindUs data={d} /><Footer d={d} />
    </main>
  )
}

export function MorningJournal({ data: d }) {
  const gallery = photos(d, 5)
  return (
    <main className={`${s.root} ${s.journal}`}>
      <div className={s.journalTop}><span>{d.CITY} · {d.HOURS}</span><Brand data={d} className={s.journalBrand} /><a href={tel(d)}>{d.PHONE}</a></div>
      <header className={s.journalHero}>
        <div><span>Η καθημερινή έκδοση</span><h1>{d.TAGLINE}</h1><p>{d.INTRO}</p><a href="#journal-menu">Στο σημερινό φύλλο ↓</a></div>
        {d.HERO_IMAGE && <figure><img src={d.HERO_IMAGE} alt={d.NAME} /><figcaption>{d.NAME}, {d.CITY}</figcaption></figure>}
      </header>
      <section id="journal-menu" className={s.journalGrid}>
        <article className={s.leadStory}><span>Πρώτο θέμα</span><h2>{d.STORY_TITLE}</h2>{d.story?.map((p, i) => <p key={i}>{p.p}</p>)}</article>
        <div className={s.journalServices}>{items(d).map((item, i) => <article key={i}><span>{item.num}</span><h3>{item.title}</h3><p>{item.desc}</p></article>)}</div>
        {gallery[0] && <figure><img src={gallery[0].image} alt={gallery[0].title} loading="lazy" /><figcaption>{gallery[0].title}</figcaption></figure>}
      </section>
      <section className={s.journalGallery}>{gallery.slice(1).map((item, i) => <figure key={i}><img src={item.image} alt={item.title} loading="lazy" /><figcaption>{item.title}</figcaption></figure>)}</section>
      <section className={s.journalCta}><span>Έλα από κοντά</span><h2>{d.CTA_TITLE}</h2><a href={tel(d)}>{d.PHONE}</a></section>
      <FindUs data={d} /><Footer d={d} />
    </main>
  )
}

export function NeighborhoodMarket({ data: d }) {
  const gallery = photos(d, 6)
  return (
    <main className={`${s.root} ${s.market}`}>
      <nav className={s.marketNav}><Brand data={d} className={s.brand} /><div><span>{d.HOURS}</span><a href={tel(d)}>📞 {d.PHONE}</a></div></nav>
      <header className={s.marketHero}>
        <div className={s.marketTitle}><span>{d.KICKER}</span><h1>{d.NAME}</h1><p>{d.TAGLINE}</p><a href="#market-grid">Δες τι ετοιμάσαμε</a></div>
        {gallery[0] && <figure><img src={gallery[0].image} alt={gallery[0].title} /><figcaption>φρέσκο · σήμερα</figcaption></figure>}
        <aside><strong>Καλημέρα,<br />{d.CITY}!</strong><span>{d.HOURS}</span></aside>
      </header>
      <section id="market-grid" className={s.marketGrid}>
        {items(d).map((item, i) => <article key={i} className={s[`tile${i + 1}`]}><span>{item.num}</span><h2>{item.title}</h2><p>{item.desc}</p></article>)}
        {gallery.slice(1, 4).map((item, i) => <figure key={i}><img src={item.image} alt={item.title} loading="lazy" /><figcaption>{item.title}</figcaption></figure>)}
      </section>
      <section className={s.marketStory}><div><span>Made in {d.CITY}</span><h2>{d.STORY_TITLE}</h2></div><div>{d.story?.map((p, i) => <p key={i}>{p.p}</p>)}<a href={tel(d)}>Τα λέμε από κοντά →</a></div></section>
      <FindUs data={d} /><Footer d={d} />
    </main>
  )
}
