import s from './CafeCollection.module.css'
import Brand from './Brand'

const tel = (d) => `tel:+${d.PHONE_INTL}`
const services = (d) => (d.services || []).slice(0, 4)
const photos = (d) => (d.gallery || []).filter((item) => item?.image).slice(0, 6)

function Credit({ d, light = false }) {
  return <footer className={`${s.credit} ${light ? s.creditLight : ''}`}><span>{d.NAME} · {d.CITY}</span><span>{d.HOURS}</span><span>Site από Vitrina</span></footer>
}

export function BakeryEditorial({ data: d }) {
  const gallery = photos(d)
  return <main className={`${s.root} ${s.patisserie}`}>
    <nav className={s.patNav}><Brand data={d} /><span>Maison artisanale</span><a href={tel(d)}>Παραγγελίες</a></nav>
    <header className={s.patHero}>
      <div className={s.patTitle}><span>Depuis 2026 · {d.CITY}</span><h1>{d.NAME}</h1><p>{d.TAGLINE}</p></div>
      {d.HERO_IMAGE && <figure><img src={d.HERO_IMAGE} alt={d.NAME} /><figcaption>Η τέχνη της καθημερινής απόλαυσης</figcaption></figure>}
      <div className={s.patSeal}>fait<br />main</div>
    </header>
    <section className={s.patIntro}><span>01 · Η συλλογή</span><h2>Μικρές δημιουργίες,<br /><em>μεγάλη φροντίδα.</em></h2><p>{d.INTRO}</p></section>
    <section className={s.patProducts}>{services(d).map((item, i) => <article key={item.title}>{gallery[i] && <img src={gallery[i].image} alt={item.title} loading="lazy" />}<div><span>0{i + 1}</span><h3>{item.title}</h3><p>{item.desc}</p></div></article>)}</section>
    <section className={s.patQuote}><p>«{d.STORY_TITLE}»</p><a href={tel(d)}>Κάλεσέ μας · {d.PHONE}</a></section>
    <Credit d={d} />
  </main>
}

export function CounterMenu({ data: d }) {
  const gallery = photos(d)
  return <main className={`${s.root} ${s.urban}`}>
    <nav className={s.urbanNav}><Brand data={d} /><div><a href="#menu">MENU</a><a href="#visit">VISIT</a></div><a className={s.urbanOrder} href={tel(d)}>ORDER ↗</a></nav>
    <header className={s.urbanHero}>
      <div className={s.urbanCopy}><span>COFFEE / FOOD / PEOPLE</span><h1>GOOD<br /><i>MOOD</i><br />DAILY.</h1><p>{d.TAGLINE}</p></div>
      {d.HERO_IMAGE && <div className={s.urbanPhoto}><img src={d.HERO_IMAGE} alt={d.NAME} /><span>OPEN<br />{d.HOURS}</span></div>}
      <div className={s.urbanTicker}>ESPRESSO · BRUNCH · SWEET THINGS · TAKE AWAY · {d.CITY} · </div>
    </header>
    <section id="menu" className={s.urbanMenu}><header><span>THE DAILY LINE-UP</span><h2>Pick your<br />favorite.</h2></header><div>{services(d).map((item, i) => <article key={item.title}><b>{String(i + 1).padStart(2, '0')}</b><h3>{item.title}</h3><p>{item.desc}</p><span>↗</span></article>)}</div></section>
    <section className={s.urbanGallery}>{gallery.slice(0, 3).map((item, i) => <figure key={item.title} className={s[`urbanPic${i + 1}`]}><img src={item.image} alt={item.title} loading="lazy" /><figcaption>{item.title}</figcaption></figure>)}</section>
    <section id="visit" className={s.urbanVisit}><h2>SEE YOU<br />AT THE BAR.</h2><div><p>{d.AREAS}</p><p>{d.HOURS}</p><a href={tel(d)}>{d.PHONE}</a></div></section>
    <Credit d={d} light />
  </main>
}

export function MorningJournal({ data: d }) {
  const gallery = photos(d)
  return <main className={`${s.root} ${s.greekBakery}`}>
    <div className={s.grNotice}>Ζεστό ψωμί από το πρωί · Καθημερινά κοντά σας</div>
    <nav className={s.grNav}><Brand data={d} /><div><a href="#fournos">Ο φούρνος μας</a><a href="#contact">Επικοινωνία</a></div></nav>
    <header className={s.grHero}>
      <div><span>Ο ΦΟΥΡΝΟΣ ΤΗΣ ΓΕΙΤΟΝΙΑΣ</span><h1>Καλημέρα,<br /><em>{d.CITY}.</em></h1><p>{d.TAGLINE}</p><a href={tel(d)}>Κράτησε την παραγγελία σου</a></div>
      {d.HERO_IMAGE && <figure><img src={d.HERO_IMAGE} alt={d.NAME} /><span>φρέσκο<br />σήμερα</span></figure>}
    </header>
    <section id="fournos" className={s.grPromise}><p>{d.INTRO}</p><strong>Κάθε μέρα.<br />Όπως παλιά.</strong></section>
    <section className={s.grGoods}>{services(d).map((item, i) => <article key={item.title}><span>{item.num || `0${i + 1}`}</span><h2>{item.title}</h2><p>{item.desc}</p></article>)}</section>
    <section className={s.grStory}>{gallery[1] && <img src={gallery[1].image} alt={gallery[1].title} loading="lazy" />}<div><span>Η δική μας ιστορία</span><h2>{d.STORY_TITLE}</h2>{d.story?.map((item, i) => <p key={i}>{item.p}</p>)}</div></section>
    <section id="contact" className={s.grContact}><span>ΠΕΡΑΣΕ ΝΑ ΠΕΙΣ ΜΙΑ ΚΑΛΗΜΕΡΑ</span><h2>{d.AREAS}</h2><a href={tel(d)}>{d.PHONE}</a></section>
    <Credit d={d} />
  </main>
}

export function NeighborhoodMarket({ data: d }) {
  const gallery = photos(d)
  return <main className={`${s.root} ${s.brunch}`}>
    <nav className={s.brunchNav}><Brand data={d} /><span className={s.brunchPill}>OPEN {d.HOURS}</span><a href={tel(d)}>BOOK A TABLE ↗</a></nav>
    <header className={s.brunchHero}>
      <div className={s.brunchSun}>☀</div>
      <div className={s.brunchWords}><span>BRUNCH CLUB · {d.CITY}</span><h1>EAT.<br /><i>PLAY.</i><br />REPEAT.</h1><p>{d.TAGLINE}</p></div>
      {gallery[0] && <figure><img src={gallery[0].image} alt={gallery[0].title} /><figcaption>YES, PLEASE!</figcaption></figure>}
      <div className={s.brunchSticker}>GOOD<br />VIBES<br />ONLY</div>
    </header>
    <section className={s.brunchCards}>{services(d).map((item, i) => <article key={item.title} className={s[`brunchCard${i + 1}`]}><span>0{i + 1}</span><h2>{item.title}</h2><p>{item.desc}</p></article>)}</section>
    <section className={s.brunchCollage}>{gallery.slice(1, 5).map((item, i) => <figure key={item.title} className={s[`brunchPhoto${i + 1}`]}><img src={item.image} alt={item.title} loading="lazy" /><figcaption>{item.title}</figcaption></figure>)}<div><span>COME<br />HUNGRY</span><a href={tel(d)}>CALL US</a></div></section>
    <section className={s.brunchCta}><p>Great coffee.<br />Zero boring days.</p><div><span>{d.AREAS}</span><span>{d.HOURS}</span><a href={tel(d)}>{d.PHONE}</a></div></section>
    <Credit d={d} />
  </main>
}
