import s from './Infinite.module.css'
import Brand from './Brand'
import FindUs from './FindUs'

export default function Infinite({ data: d }) {
  const tel = `tel:+${d.PHONE_INTL}`
  const gallery = d.gallery || []
  const services = d.services || []
  const journey = gallery.length ? gallery : services

  return (
    <div className={s.root}>
      <nav className={s.nav} aria-label="Κύρια πλοήγηση"><a href="#top" className={s.brand}><Brand data={d} /></a><span>{d.CITY}</span><a href={tel} className={s.call}>{d.PHONE}</a></nav>
      <header id="top" className={s.hero}>
        <div className={s.heroTop}><span className={s.kicker}>{d.KICKER}</span><span className={s.counter}>01 — 04</span></div>
        <h1>{d.TAGLINE}</h1>
        <div className={s.heroBottom}><p>{d.NAME} · {d.TRADE}</p><a href="#journey">Εξερεύνησε <span aria-hidden="true">↓</span></a></div>
        {d.HERO_IMAGE && <figure className={s.heroImage}><img src={d.HERO_IMAGE} alt={`${d.NAME} — ${d.TRADE}`} /></figure>}
      </header>

      <main>
        <section id="journey" className={s.journey} aria-label="Επιλεγμένα έργα">
          <header><span>Επιλεγμένη διαδρομή</span><h2>Έργα χωρίς τέλος.</h2><p>Σύρε οριζόντια για να εξερευνήσεις.</p></header>
          <div className={s.rail} tabIndex="0">
            {journey.map((item, i) => gallery.length ? <figure className={s.frame} key={i}><img src={item.image} alt={item.title} loading="lazy" /><figcaption><span>{String(i + 1).padStart(2, '0')}</span><div><b>{item.title}</b><small>{item.sub || d.CITY}</small></div></figcaption></figure> : <article className={s.textFrame} key={i}><span>{String(i + 1).padStart(2, '0')}</span><h3>{item.title}</h3><p>{item.desc}</p></article>)}
            <a href={tel} className={s.endFrame}><span>Ας ξεκινήσουμε</span><b>{d.PHONE}</b><i aria-hidden="true">→</i></a>
          </div>
        </section>

        <section id="services" className={s.services}><header><span>Υπηρεσίες</span><h2>Ό,τι χρειάζεται ο χώρος σου.</h2></header><ol>{services.map((item,i)=><li key={i}><span>{item.num || String(i+1).padStart(2,'0')}</span><h3>{item.title}</h3><p>{item.desc}</p></li>)}</ol></section>
        <section id="story" className={s.story}><div className={s.storyLead}><span>Η ιστορία</span><blockquote>{d.STORY_TITLE}</blockquote></div><div className={s.storyBody}>{d.story?.map((item,i)=><p key={i}>{item.p}</p>)}<b>— {d.NAME}</b></div></section>
        <section id="contact" className={s.contact}><p>{d.AREAS} · {d.HOURS}</p><h2>{d.CTA_TITLE}</h2><a href={tel}>Κάλεσε {d.PHONE}<span aria-hidden="true">↗</span></a></section>
      </main>
      <FindUs data={d} dark />
      <footer className={s.footer}><span>© {d.YEAR} {d.NAME}</span><span>{d.CITY}</span><span>Site από Vitrina</span></footer>
    </div>
  )
}
