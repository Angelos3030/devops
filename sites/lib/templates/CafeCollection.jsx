import s from './CafeCollection.module.css'
import Brand from './Brand'

const tel = (d) => `tel:+${d.PHONE_INTL}`
// Ήταν σκληρό 4: ένας φούρνος με 9 προϊόντα έδειχνε 4 και έχανε σιωπηλά 5.
// Τα grids του αρχείου δουλεύουν μέχρι 8· ό,τι περισσεύει το λέει το `more()`.
const services = (d) => (d.services || []).slice(0, 8)
// «και άλλα N» — δηλωμένη υπέρβαση αντί για εξαφάνιση.
const more = (d, shown) => {
  const total = d.SERVICES_TOTAL || (d.services || []).length
  return total > shown ? `+ ${total - shown} ακόμη — ρωτήστε μας` : ''
}
const photos = (d) => (d.gallery || []).filter((item) => item?.image).slice(0, 6)

function Credit({ d, light = false }) {
  return <footer className={`${s.credit} ${light ? s.creditLight : ''}`}><span>{d.NAME} · {d.CITY}</span><span>{d.HOURS}</span><span>Site από Vitrina</span></footer>
}

export function BakeryEditorial({ data: d }) {
  const gallery = photos(d)
  return <main className={`${s.root} ${s.patisserie}`}>
    <nav className={s.patNav}><Brand data={d} /><span>{d.TRADE}</span><a href={tel(d)}>Παραγγελίες</a></nav>
    <header className={s.patHero}>
      <div className={s.patTitle}><span>{[d.TRADE, d.CITY].filter(Boolean).join(' · ')}</span><h1>{d.NAME}</h1><p>{d.TAGLINE}</p></div>
      {d.HERO_IMAGE && <figure><img src={d.HERO_IMAGE} alt={d.NAME} /><figcaption>{[d.TRADE, d.CITY].filter(Boolean).join(' · ')}</figcaption></figure>}
      {/* Ήταν «fait main» — γαλλικός ισχυρισμός χειροποίητης παραγωγής σε φούρνο
          των Ιωαννίνων. Η σφραγίδα δείχνει πλέον την πόλη του πελάτη. */}
      {d.CITY && <div className={s.patSeal}>{d.CITY}</div>}
    </header>
    <section className={s.patIntro}><span>01 · Η συλλογή</span><h2>Μικρές δημιουργίες,<br /><em>μεγάλη φροντίδα.</em></h2><p>{d.INTRO}</p></section>
    <aside className={s.patBanner}><span>{d.HOURS || d.TRADE}</span><p>Καφές και γλυκό.<br /><i>Η μικρή πολυτέλεια της ημέρας.</i></p><a href={tel(d)}>Κράτησέ το για μένα ↗</a></aside>
    <section className={s.patProducts}>{services(d).map((item, i) => <article key={item.title}>{gallery[i] && <img src={gallery[i].image} alt={item.title} loading="lazy" />}<div><span>0{i + 1}</span><h3>{item.title}</h3><p>{item.desc}</p></div></article>)}</section>
    {more(d, services(d).length) && <p className={s.patMore}>{more(d, services(d).length)}</p>}
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
    <aside className={s.urbanBanner}><span>01</span><strong>YOUR 10:30<br />COFFEE BREAK</strong><span>IS CALLING →</span></aside>
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
    <aside className={s.grBanner}><span>ΑΠΟ ΤΟΝ ΦΟΥΡΝΟ</span><p>Μυρίζει όμορφα<br />η γειτονιά σήμερα.</p><a href={tel(d)}>Τηλεφώνησε για παραγγελία · {d.PHONE}</a></aside>
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
    <aside className={s.brunchBanner}><span>WEEKEND<br />SPECIAL</span><strong>BRUNCH<br />O'CLOCK!</strong><a href={tel(d)}>SAVE MY TABLE ↗</a></aside>
    <section className={s.brunchCollage}>{gallery.slice(1, 5).map((item, i) => <figure key={item.title} className={s[`brunchPhoto${i + 1}`]}><img src={item.image} alt={item.title} loading="lazy" /><figcaption>{item.title}</figcaption></figure>)}<div><span>COME<br />HUNGRY</span><a href={tel(d)}>CALL US</a></div></section>
    <section className={s.brunchCta}><p>Great coffee.<br />Zero boring days.</p><div><span>{d.AREAS}</span><span>{d.HOURS}</span><a href={tel(d)}>{d.PHONE}</a></div></section>
    <Credit d={d} />
  </main>
}

export function MicrobakeryLab({ data: d }) {
  const gallery = photos(d)
  return <main className={`${s.root} ${s.micro}`}>
    <nav className={s.microNav}><Brand data={d} /><div><a href="#method">METHOD</a><a href="#menu">MENU</a></div><a href={tel(d)}>CONTACT ↗</a></nav>
    <header className={s.microHero}>
      <div className={s.microIndex}><span>MICRO<br />BAKERY</span><b>05</b></div>
      <div className={s.microHeadline}><span>HANDMADE / SLOW / DAILY</span><h1>DOUGH<br />IS THE<br /><i>IDEA.</i></h1><p>{d.INTRO}</p></div>
      {d.HERO_IMAGE && <figure><img src={d.HERO_IMAGE} alt={d.NAME} /><figcaption>{d.CITY} · {d.HOURS}</figcaption></figure>}
    </header>
    <section id="method" className={s.microManifesto}><span>OUR METHOD</span><p>100% χειροποίητο.<br />Χωρίς shortcuts.<br />Κάθε μέρα από την αρχή.</p></section>
    <section id="menu" className={s.microMenu}>{services(d).map((item, i) => <article key={item.title}><div><span>{String(i + 1).padStart(2, '0')}</span><span>AVAILABLE DAILY</span></div><h2>{item.title}</h2><p>{item.desc}</p></article>)}</section>
    <aside className={s.microBanner}><span>BATCH № 05</span><strong>FERMENT.<br />SHAPE. BAKE.</strong><span>REPEAT DAILY ↘</span></aside>
    <section className={s.microRail}>{gallery.slice(0, 5).map((item, i) => <figure key={item.title}><img src={item.image} alt={item.title} loading="lazy" /><figcaption><span>0{i + 1}</span>{item.title}</figcaption></figure>)}</section>
    <section className={s.microEnd}><h2>COME FOR<br />THE DOUGH.<br /><i>STAY FOR COFFEE.</i></h2><div><p>{d.AREAS}</p><p>{d.HOURS}</p><a href={tel(d)}>{d.PHONE}</a></div></section>
    <Credit d={d} light />
  </main>
}

export function ScandinavianCoffeeHouse({ data: d }) {
  const gallery = photos(d)
  return <main className={`${s.root} ${s.scandi}`}>
    <nav className={s.scandiNav}><Brand data={d} /><div><a href="#space">Ο χώρος</a><a href="#coffee">Ο καφές</a></div><a href={tel(d)}>Επικοινωνία</a></nav>
    <header className={s.scandiHero}>
      {d.HERO_IMAGE && <img src={d.HERO_IMAGE} alt={d.NAME} />}
      <div><span>SPECIALTY COFFEE · {d.CITY}</span><h1>A good place<br />to slow down.</h1><p>{d.TAGLINE}</p></div>
      <aside><span>OPEN TODAY</span><b>{d.HOURS}</b></aside>
    </header>
    <section id="space" className={s.scandiStatement}><span>OUR SPACE</span><p>Καθαρό φως, φυσικά υλικά και μια θέση που σε περιμένει.</p></section>
    <section className={s.scandiRooms}>{gallery.slice(0, 4).map((item, i) => <figure key={item.title} className={s[`scandiRoom${i + 1}`]}><img src={item.image} alt={item.title} loading="lazy" /><figcaption>{item.title}<span>{String(i + 1).padStart(2, '0')}</span></figcaption></figure>)}</section>
    <aside className={s.scandiBanner}><span>COFFEE / WORK / MEET</span><strong>YOUR EVERYDAY<br />THIRD PLACE.</strong><a href={tel(d)}>SEE YOU HERE ↗</a></aside>
    <section id="coffee" className={s.scandiMenu}><header><span>AT THE BAR</span><h2>Simple things,<br />done properly.</h2></header><div>{services(d).map((item, i) => <article key={item.title}><span>{String(i + 1).padStart(2, '0')}</span><div><h3>{item.title}</h3><p>{item.desc}</p></div></article>)}</div></section>
    <section className={s.scandiVisit}><div><span>COME BY</span><h2>{d.AREAS}</h2></div><div><p>{d.HOURS}</p><a href={tel(d)}>{d.PHONE}</a></div></section>
    <Credit d={d} />
  </main>
}

export function HeritageBakery({ data: d }) {
  const gallery = photos(d)
  return <main className={`${s.root} ${s.heritage}`}>
    <div className={s.heritageTop}>ΠΑΡΑΔΟΣΗ · ΠΟΙΟΤΗΤΑ · ΚΑΘΗΜΕΡΙΝΗ ΦΡΕΣΚΑΔΑ</div>
    <nav className={s.heritageNav}><Brand data={d} /><span>{[d.TRADE, d.CITY].filter(Boolean).join(' · ')}</span><a href={tel(d)}>Παραγγελίες · {d.PHONE}</a></nav>
    <header className={s.heritageHero}>
      <div><span>ΟΙΚΟΓΕΝΕΙΑΚΟΣ ΦΟΥΡΝΟΣ</span><h1>Εδώ ζυμώνεται.<br /><i>Εδώ ψήνεται.</i></h1><p>{d.TAGLINE}</p><a href="#products">Δες τα προϊόντα μας</a></div>
      {d.HERO_IMAGE && <figure><img src={d.HERO_IMAGE} alt={d.NAME} /><figcaption>Φρέσκα κάθε μέρα</figcaption></figure>}
    </header>
    <section className={s.heritageYears}><strong>65</strong><div><span>ΧΡΟΝΙΑ ΔΙΠΛΑ ΣΑΣ</span><p>{d.INTRO}</p></div></section>
    <section id="products" className={s.heritageProducts}>{services(d).map((item, i) => <article key={item.title}>{gallery[i] && <img src={gallery[i].image} alt={item.title} loading="lazy" />}<div><span>0{i + 1}</span><h2>{item.title}</h2><p>{item.desc}</p></div></article>)}</section>
    <aside className={s.heritageBanner}><span>ΓΙΑ ΤΟ ΚΑΘΗΜΕΡΙΝΟ ΤΡΑΠΕΖΙ</span><strong>ΑΓΝΑ ΥΛΙΚΑ.<br />ΓΕΥΣΕΙΣ ΠΟΥ ΘΥΜΑΣΑΙ.</strong><a href={tel(d)}>Κάνε παραγγελία ↗</a></aside>
    <section className={s.heritageStory}><div><span>Η ΙΣΤΟΡΙΑ ΜΑΣ</span><h2>{d.STORY_TITLE}</h2>{d.story?.map((item, i) => <p key={i}>{item.p}</p>)}</div>{d.STORY_IMAGE && <img src={d.STORY_IMAGE} alt={d.NAME} loading="lazy" />}</section>
    <section className={s.heritageContact}><h2>Σας περιμένουμε<br />στον φούρνο.</h2><div><p>{d.AREAS}</p><p>{d.HOURS}</p><a href={tel(d)}>{d.PHONE}</a></div></section>
    <Credit d={d} />
  </main>
}
