import { useEffect, useState } from "react";
import {
  ArrowDown,
  ArrowRight,
  Check,
  List,
  MapPin,
  Phone,
  X,
} from "@phosphor-icons/react";

const projects = [
  {
    image: "/assets/modern-kitchen.jpg",
    number: "01",
    category: "Κουζίνα",
    title: "Λειτουργικός σχεδιασμός, καθαρή αισθητική",
    copy: "Κουζίνα κατασκευασμένη στα μέτρα του χώρου, με ποιοτικά υλικά και προσεγμένες λεπτομέρειες.",
  },
  {
    image: "/assets/walnut-sideboard.jpg",
    number: "02",
    category: "Έπιπλο",
    title: "Ξύλο με χαρακτήρα",
    copy: "Ιδιαίτερα έπιπλα και συνθέσεις που σχεδιάζονται για τον άνθρωπο και τον χώρο τους.",
  },
  {
    image: "/assets/wardrobe-built-in.jpg",
    number: "03",
    category: "Ντουλάπα",
    title: "Κάθε εκατοστό αξιοποιείται",
    copy: "Εντοιχισμένες ντουλάπες, πρακτική οργάνωση και εφαρμογή που δείχνει μέρος του χώρου.",
  },
];

const services = [
  ["01", "Κουζίνες στα μέτρα σου", "Σχεδιασμός, κατασκευή, εντοιχισμός και ανακαίνιση ντουλαπιών κουζίνας."],
  ["02", "Ντουλάπες & αποθήκευση", "Εντοιχισμένες ντουλάπες, εσωτερική διαρρύθμιση και επισκευές."],
  ["03", "Έπιπλα & συνθέσεις", "Τραπέζια, βιβλιοθήκες, κρεβάτια, ράφια και ειδικές ξύλινες κατασκευές."],
  ["04", "Επισκευές & λουστράρισμα", "Ξυλουργικά μερεμέτια, πόρτες, παράθυρα και ανανέωση επίπλων."],
];

export function App() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [quoteOpen, setQuoteOpen] = useState(false);
  const [sent, setSent] = useState(false);

  useEffect(() => {
    document.body.style.overflow = quoteOpen ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [quoteOpen]);

  const openQuote = () => {
    setSent(false);
    setQuoteOpen(true);
    setMenuOpen(false);
  };

  return (
    <main>
      <section className="hero" id="top">
        <img className="hero-image" src="/assets/rounded-cabinet.jpg" alt="Χειροποίητο στρογγυλεμένο έπιπλο Κουτράκη" />
        <div className="hero-shade" />
        <header className="site-header">
          <a className="brand" href="#top" aria-label="Κουτράκης - αρχική">ΚΟΥΤΡΑΚΗΣ</a>
          <nav className={menuOpen ? "nav open" : "nav"} aria-label="Κύρια πλοήγηση">
            <a href="#top" onClick={() => setMenuOpen(false)}>Αρχική</a>
            <a href="#projects" onClick={() => setMenuOpen(false)}>Έργα</a>
            <a href="#services" onClick={() => setMenuOpen(false)}>Υπηρεσίες</a>
            <a href="#about" onClick={() => setMenuOpen(false)}>Σχετικά</a>
            <a href="#contact" onClick={() => setMenuOpen(false)}>Επικοινωνία</a>
          </nav>
          <button className="header-quote" onClick={openQuote}>Ζήτησε προσφορά</button>
          <button className="menu-button" onClick={() => setMenuOpen(!menuOpen)} aria-label={menuOpen ? "Κλείσιμο μενού" : "Άνοιγμα μενού"}>
            {menuOpen ? <X size={24} /> : <List size={25} />}
          </button>
        </header>

        <div className="hero-copy">
          <p className="eyebrow">Κουζίνες & ξύλινες κατασκευές<br />στα μέτρα σου</p>
          <h1>Κώστας<br />Κουτράκης</h1>
          <div className="location"><span />Γέρακας · Αθήνα</div>
          <button className="primary-button" onClick={openQuote}>Ζήτησε προσφορά <ArrowRight size={22} /></button>
        </div>
        <div className="hero-index"><b>01</b><span /><span /><span /><em>03</em></div>
        <a className="scroll-cue" href="#projects" aria-label="Μετάβαση στα έργα"><ArrowDown size={24} /></a>
      </section>

      <section className="projects-section" id="projects">
        <div className="section-intro">
          <div><i /> <h2>Επιλεγμένα έργα</h2></div>
          <p>Κάθε κατασκευή είναι μοναδική. Σχεδιάζουμε και υλοποιούμε κουζίνες και ξύλινες κατασκευές με έμφαση στη λεπτομέρεια, τη λειτουργικότητα και την ποιότητα.</p>
        </div>
        <div className="project-list">
          {projects.map((project, index) => (
            <article className={`project project-${index + 1}`} key={project.number}>
              <img src={project.image} alt={project.title} />
              <div className="project-copy">
                <small>{project.number} / {project.category}</small>
                <h3>{project.title}</h3>
                <p>{project.copy}</p>
                <button onClick={openQuote}>Συζήτησε το έργο σου <ArrowRight size={18} /></button>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="services-section" id="services">
        <div className="services-heading">
          <p className="section-kicker">Τι κατασκευάζουμε</p>
          <h2>Από την ιδέα,<br />στον χώρο σου.</h2>
        </div>
        <div className="services-list">
          {services.map(([number, title, copy]) => (
            <article key={number}>
              <span>{number}</span>
              <h3>{title}</h3>
              <p>{copy}</p>
              <ArrowRight size={20} />
            </article>
          ))}
        </div>
      </section>

      <section className="about-section" id="about">
        <img src="/assets/kids-bunk-bed.jpg" alt="Ξύλινη κουκέτα κατασκευασμένη στα μέτρα του χώρου" />
        <div className="about-copy">
          <p className="section-kicker">Η δουλειά μας</p>
          <h2>Όχι έτοιμες λύσεις.<br />Η σωστή λύση.</h2>
          <p>Από μια κουζίνα μέχρι ένα ιδιαίτερο έπιπλο, κάθε έργο ξεκινά με σωστή συνεννόηση και μέτρηση του χώρου. Η κατασκευή γίνεται με προσοχή στην εφαρμογή, τη χρήση και το τελικό φινίρισμα.</p>
          <ul>
            <li><Check size={19} /> Αυτοψία και μέτρηση στον χώρο</li>
            <li><Check size={19} /> Κατασκευή προσαρμοσμένη στις ανάγκες σου</li>
            <li><Check size={19} /> Εξυπηρέτηση σε Γέρακα, Αθήνα και γύρω περιοχές</li>
          </ul>
        </div>
      </section>

      <section className="contact-section" id="contact">
        <p className="section-kicker">Έχεις κάτι στο μυαλό σου;</p>
        <h2>Ας το φτιάξουμε.</h2>
        <div className="contact-actions">
          <a href="tel:+306956297670"><Phone size={23} weight="light" /> 6956 297670</a>
          <button onClick={openQuote}>Ζήτησε προσφορά <ArrowRight size={21} /></button>
        </div>
        <div className="contact-meta">
          <span><MapPin size={18} /> Γέρακας 15344 · Εξυπηρέτηση σε όλη την Αθήνα</span>
          <span>koutrakiskouzines.gr</span>
        </div>
      </section>

      <footer><a href="#top">ΚΟΥΤΡΑΚΗΣ</a><span>Ξυλουργικές κατασκευές · Γέρακας, Αθήνα</span><span>© 2026</span></footer>
      <a className="mobile-call" href="tel:+306956297670"><Phone size={21} weight="fill" /> Κάλεσε τώρα</a>

      {quoteOpen && (
        <div className="modal-backdrop" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && setQuoteOpen(false)}>
          <section className="quote-modal" role="dialog" aria-modal="true" aria-labelledby="quote-title">
            <button className="modal-close" onClick={() => setQuoteOpen(false)} aria-label="Κλείσιμο"><X size={23} /></button>
            {sent ? (
              <div className="success-state">
                <span><Check size={32} /></span>
                <h2>Το αίτημα είναι έτοιμο.</h2>
                <p>Στο κανονικό site θα αποστέλλεται απευθείας. Για τώρα, κάλεσε στο <a href="tel:+306956297670">6956 297670</a>.</p>
                <button onClick={() => setQuoteOpen(false)}>Κλείσιμο</button>
              </div>
            ) : (
              <>
                <p className="section-kicker">Νέο έργο</p>
                <h2 id="quote-title">Πες μας τι θέλεις να φτιάξεις.</h2>
                <form onSubmit={(event) => { event.preventDefault(); setSent(true); }}>
                  <label>Όνομα<input required name="name" autoFocus /></label>
                  <label>Τηλέφωνο<input required name="phone" inputMode="tel" /></label>
                  <label>Τι κατασκευή χρειάζεσαι;<textarea required name="project" rows="4" placeholder="π.χ. Νέα κουζίνα στον Γέρακα..." /></label>
                  <button type="submit">Αποστολή αιτήματος <ArrowRight size={20} /></button>
                </form>
              </>
            )}
          </section>
        </div>
      )}
    </main>
  );
}
