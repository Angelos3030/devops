import Link from 'next/link'
import { TEMPLATE_META } from '../../../lib/templates'
import { demoBusinesses } from '../../../lib/demoData'
import { APP_BASE } from '../../../lib/appUrl'
import s from './trade.module.css'

// Ad landing pages ανά επάγγελμα: /gia/taverna, /gia/kommotirio, ...
// Ένα ζωντανό demo της κατηγορίας + 3 εναλλακτικά + ένα CTA. Ό,τι πουλάει τα ads.
export const TRADES = {
  xylourgos: {
    label: 'ξυλουργούς & επιπλοποιούς', hero: 'Η ποιότητα της δουλειάς σου πρέπει να φαίνεται.',
    biz: 'carpenter', templates: ['canvas', 'cinematic', 'living', 'forge'],
    points: ['Έργα και λεπτομέρειες σε πρώτο πλάνο', 'Αίτημα προσφοράς με ένα κλικ', 'Περιοχές εξυπηρέτησης και τηλέφωνο μπροστά'],
  },
  taverna: {
    label: 'ταβέρνες & εστιατόρια', hero: 'Το site που ανοίγει την όρεξη.',
    biz: 'taverna', templates: ['ember', 'warmth', 'magazine', 'editorial'],
    points: ['Μενού & φωτογραφίες που πουλάνε', 'Τηλέφωνο για κράτηση σε ένα κλικ', 'Σε βρίσκουν στο Google «ταβέρνα + περιοχή»'],
  },
  kafe: {
    label: 'καφέ & φούρνους', hero: 'Το πρωινό φως του μαγαζιού σου, online.',
    biz: 'cafe', templates: ['bloom', 'warmth', 'bento', 'editorial'],
    points: ['Ο κατάλογός σου, πάντα ενημερωμένος', 'Ώρες & τοποθεσία μπροστά', 'Φωτογραφίες που φέρνουν κόσμο'],
  },
  katastima: {
    label: 'καταστήματα & boutiques', hero: 'Τα προϊόντα σου, σε μια βιτρίνα που ξεχωρίζει.',
    biz: 'retail', templates: ['runway', 'type-gallery', 'bento', 'infinite'],
    points: ['Προϊόντα και νέες αφίξεις σε πρώτο πλάνο', 'Ερώτηση διαθεσιμότητας με ένα κλικ', 'Ωράριο και τοποθεσία χωρίς ψάξιμο'],
  },
  kommotirio: {
    label: 'κομμωτήρια & beauty', hero: 'Η δουλειά σου, σε βιτρίνα μόδας.',
    biz: 'salon', templates: ['beauty-atelier', 'runway', 'bento', 'type-gallery'],
    points: ['Portfolio που δείχνει το ταλέντο σου', 'Ραντεβού με ένα κλικ', 'Instagram-ready εμφάνιση'],
  },
  iatreio: {
    label: 'ιατρεία & κλινικές', hero: 'Εμπιστοσύνη από την πρώτη ματιά.',
    biz: 'physician', templates: ['marble', 'quiet', 'split', 'grid'],
    points: ['Καθαρή παρουσίαση υπηρεσιών', 'Ραντεβού & ωράριο μπροστά', 'Σοβαρή, ήρεμη αισθητική'],
  },
  odontiatros: {
    label: 'οδοντιατρεία', hero: 'Ένα ήρεμο site που χτίζει εμπιστοσύνη.',
    biz: 'dentist', templates: ['marble', 'quiet', 'grid', 'living'],
    points: ['Θεραπείες χωρίς δύσκολη ορολογία', 'Ιατρός, χώρος και εξοπλισμός με τάξη', 'Ραντεβού και ωράριο μπροστά'],
  },
  aisthitiki: {
    label: 'κέντρα αισθητικής', hero: 'Η φροντίδα σου αξίζει μια όμορφη πρώτη εικόνα.',
    biz: 'aesthetics', templates: ['beauty-atelier', 'bloom', 'runway', 'quiet'],
    points: ['Θεραπείες με καθαρή παρουσίαση', 'Ραντεβού σε ένα άγγιγμα', 'Premium αισθητική χωρίς υπερβολές'],
  },
  masaz: {
    label: 'μασάζ & χώρους ευεξίας', hero: 'Η εμπειρία χαλάρωσης ξεκινά πριν το ραντεβού.',
    biz: 'massage', templates: ['living', 'cinematic', 'quiet', 'bloom'],
    points: ['Ατμόσφαιρα που μεταφέρει την εμπειρία', 'Υπηρεσίες και διάρκεια με σαφήνεια', 'Κράτηση με ένα άγγιγμα'],
  },
  dikigoros: {
    label: 'δικηγόρους & λογιστές', hero: 'Κύρος που φαίνεται πριν το πρώτο ραντεβού.',
    biz: 'lawyer', templates: ['marble', 'grid', 'longform', 'editorial'],
    points: ['Τομείς εξειδίκευσης με τάξη', 'Διακριτικό, θεσμικό ύφος', 'Επικοινωνία χωρίς τριβή'],
  },
  texnitis: {
    label: 'τεχνίτες & μάστορες', hero: 'Σε παίρνουν τηλέφωνο, δεν σε ψάχνουν.',
    biz: 'plumber', templates: ['forge', 'sidebar', 'dispatch', 'poster'],
    points: ['Τηλέφωνο σε κάθε οθόνη', 'Οι δουλειές σου σε φωτογραφίες', '«Υδραυλικός + περιοχή» στο Google'],
  },
  domatia: {
    label: 'δωμάτια & καταλύματα', hero: 'Κρατήσεις χωρίς προμήθεια πλατφόρμας.',
    biz: 'rooms', templates: ['aegean', 'bento', 'editorial', 'magazine'],
    points: ['Το κατάλυμά σου σε πρώτο πλάνο', 'Απευθείας κράτηση με τηλέφωνο', 'Ελληνικά & αγγλικά'],
  },
  gymnastirio: {
    label: 'γυμναστήρια & trainers', hero: 'Ενέργεια που φαίνεται από την πρώτη οθόνη.',
    biz: 'gym', templates: ['volt', 'poster', 'bento', 'grid'],
    points: ['Πρόγραμμα & υπηρεσίες καθαρά', 'Δωρεάν δοκιμαστικό με ένα κλικ', 'Φωτογραφίες χώρου που πείθουν'],
  },
  synergeio: {
    label: 'συνεργεία αυτοκινήτων', hero: 'Αξιοπιστία πριν καν σηκώσεις το τηλέφωνο.',
    biz: 'garage', templates: ['motor', 'forge', 'grid', 'dispatch'],
    points: ['Υπηρεσίες σαν δελτίο εργασιών', 'Ραντεβού για service', 'Εγγύηση & τιμές μπροστά'],
  },
  paragogos: {
    label: 'παραγωγούς & κτήματα', hero: 'Το προϊόν σου, με την ιστορία του.',
    biz: 'farm', templates: ['terra', 'longform', 'warmth', 'magazine'],
    points: ['Προϊόντα σαν ετικέτες παρτίδας', 'Παραγγελία απευθείας', 'Η ιστορία της γης σου'],
  },
}

export function generateStaticParams() {
  return Object.keys(TRADES).map((trade) => ({ trade }))
}

export function generateMetadata({ params }) {
  const t = TRADES[params.trade]
  if (!t) return { title: 'Vitrina' }
  const title = `Επαγγελματικό site για ${t.label} — €14,99/μήνα | Vitrina`
  const description = `${t.hero} Έτοιμο site με φιλοξενία, local SEO και απεριόριστες αλλαγές. 30 ημέρες δωρεάν και μετά €14,99/μήνα.`
  return {
    title, description,
    alternates: { canonical: `${APP_BASE}/gia/${params.trade}` },
    openGraph: { title, description, type: 'website', locale: 'el_GR' },
  }
}

export default function TradeLanding({ params }) {
  const t = TRADES[params.trade]
  if (!t) {
    return <div className={s.missing}>Η σελίδα δεν βρέθηκε. <Link href="/">Πίσω στην αρχική</Link></div>
  }
  const demo = demoBusinesses[t.biz]
  const [main, ...rest] = t.templates

  return (
    <div className={s.page}>
      <header className={s.hero}>
        <span className={s.eyebrow}>Vitrina για {t.label}</span>
        <h1>{t.hero}</h1>
        <p className={s.sub}>
          Σου φτιάχνουμε επαγγελματικό site με τα δικά σου στοιχεία και φωτογραφίες.
          Φιλοξενία, SEO και αλλαγές — <strong>€14,99/μήνα</strong>. Προαιρετικό
          .gr domain <strong>24€/έτος</strong>, ξεχωριστά.
        </p>
        <div className={s.actions}>
          <a className={s.cta} href="https://getvitrina.gr/connect.html">Φτιάξε μου το site →</a>
          <a className={s.ghost} href={`/preview/${main}?biz=${t.biz}`} target="_blank" rel="noreferrer">Δες το demo ↗</a>
        </div>
        <ul className={s.points}>
          {t.points.map((p, i) => <li key={i}>{p}</li>)}
        </ul>
      </header>

      <section className={s.showcase}>
        <div className={s.browser}>
          <div className={s.bar}>
            <span className={s.dot} /><span className={s.dot} /><span className={s.dot} />
            <span className={s.url}>🔒 {(demo?.NAME || 'το-μαγαζι-σου').toLowerCase().replace(/\s+/g, '')}.gr</span>
          </div>
          <iframe src={`/preview/${main}?biz=${t.biz}`} title={`Demo ${t.label}`} loading="lazy" />
        </div>
        <p className={s.caption}>
          Ζωντανό demo — <strong>{TEMPLATE_META[main]?.label}</strong>: {TEMPLATE_META[main]?.desc}
        </p>
      </section>

      <section className={s.more}>
        <h2>Και άλλα σχέδια για {t.label}</h2>
        <div className={s.grid}>
          {rest.map((k) => (
            <a key={k} className={s.card} href={`/preview/${k}?biz=${t.biz}`} target="_blank" rel="noreferrer">
              <div className={s.shot}>
                <iframe src={`/preview/${k}?biz=${t.biz}`} title={k} loading="lazy" scrolling="no" />
              </div>
              <div className={s.cardLabel}>
                <strong>{TEMPLATE_META[k]?.label || k}</strong>
                <span>{TEMPLATE_META[k]?.desc}</span>
              </div>
            </a>
          ))}
        </div>
      </section>

      <section className={s.close}>
        <h2>Πες μας το μαγαζί σου — το σχέδιο έρχεται σε λεπτά.</h2>
        <a className={s.cta} href="https://getvitrina.gr/connect.html">Ξεκίνα τώρα — 30 ημέρες δωρεάν</a>
      </section>

      <footer className={s.footer}>© {new Date().getFullYear()} Vitrina · getvitrina.gr</footer>
    </div>
  )
}
