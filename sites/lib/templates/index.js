import Editorial from './Editorial'
import Split from './Split'
import Showcase from './Showcase'
import Bento from './Bento'
import Longform from './Longform'
import Corporate from './Corporate'
import Poster from './Poster'
import Sidebar from './Sidebar'
import GridT from './Grid'
import Coast from './Coast'
import Magazine from './Magazine'
import Warmth from './Warmth'
import Ember from './Ember'
import Marble from './Marble'
import Runway from './Runway'
import Forge from './Forge'
import Aegean from './Aegean'
import Bloom from './Bloom'
import Pulse from './Pulse'
import Volt from './Volt'
import Motor from './Motor'
import Terra from './Terra'
import Dispatch from './Dispatch'
import Canvas from './Canvas'
import Cinematic from './Cinematic'
import TypeGallery from './TypeGallery'
import Quiet from './Quiet'
import Kinetic from './Kinetic'
import Infinite from './Infinite'
import Living from './Living'
import BeautyAtelier from './BeautyAtelier'
import ClinicTriage from './ClinicTriage'
import Callout from './Callout'
import { BakeryEditorial, CounterMenu, MorningJournal, NeighborhoodMarket, MicrobakeryLab, ScandinavianCoffeeHouse, HeritageBakery } from './CafeCollection'

// Structurally-distinct React archetypes.
export const TEMPLATES = { editorial: Editorial, split: Split, showcase: Showcase, bento: Bento, longform: Longform, corporate: Corporate, poster: Poster, sidebar: Sidebar, grid: GridT, coast: Coast, magazine: Magazine, warmth: Warmth, ember: Ember, marble: Marble, runway: Runway, forge: Forge, aegean: Aegean, bloom: Bloom, pulse: Pulse, volt: Volt, motor: Motor, terra: Terra, dispatch: Dispatch, canvas: Canvas, cinematic: Cinematic, 'type-gallery': TypeGallery, quiet: Quiet, kinetic: Kinetic, infinite: Infinite, living: Living, 'beauty-atelier': BeautyAtelier, 'clinic-triage': ClinicTriage, callout: Callout, 'bakery-editorial': BakeryEditorial, 'counter-menu': CounterMenu, 'morning-journal': MorningJournal, 'neighborhood-market': NeighborhoodMarket, 'microbakery-lab': MicrobakeryLab, 'scandinavian-coffee': ScandinavianCoffeeHouse, 'heritage-bakery': HeritageBakery }
// The public collection stays intentionally curated. Legacy templates remain
// renderable for existing clients but are not offered to new customers.
export const TEMPLATE_KEYS = ['editorial', 'split', 'bento', 'longform', 'poster', 'sidebar', 'grid', 'magazine', 'warmth', 'ember', 'marble', 'runway', 'forge', 'aegean', 'bloom', 'volt', 'motor', 'terra', 'dispatch', 'canvas', 'cinematic', 'type-gallery', 'quiet', 'kinetic', 'infinite', 'living', 'beauty-atelier', 'clinic-triage', 'callout', 'bakery-editorial', 'counter-menu', 'morning-journal', 'neighborhood-market', 'microbakery-lab', 'scandinavian-coffee', 'heritage-bakery']
export const LEGACY_TEMPLATE_KEYS = ['showcase', 'corporate', 'coast', 'pulse']
export const TEMPLATE_META = {
  editorial: { label: 'Editorial', desc: 'Κλασικό stacked, μεγάλη τυπογραφία.' },
  split: { label: 'Split', desc: 'Σταθερό πλαϊνό panel + περιεχόμενο που κυλάει.' },
  showcase: { label: 'Showcase', desc: 'Full-screen, με έμφαση στις φωτογραφίες.' },
  bento: { label: 'Bento', desc: 'Πλέγμα από tiles διαφορετικού μεγέθους.' },
  longform: { label: 'Longform', desc: 'Στενή στήλη, magazine reading, drop-cap.' },
  corporate: { label: 'Corporate', desc: 'Καθαρό business με stats & feature cards.' },
  poster: { label: 'Poster', desc: 'Oversized τυπογραφία, brutalist, high-contrast.' },
  sidebar: { label: 'Sidebar', desc: 'Sticky rail επικοινωνίας — conversion.' },
  grid: { label: 'Swiss Studio', desc: 'Αυστηρό ελβετικό σύστημα, καθαρές γραμμές και σύγχρονη sans-serif τυπογραφία.' },
  coast: { label: 'Coast', desc: 'Μεσογειακό, φωτεινό, zigzag rows — τουρισμός.' },
  magazine: { label: 'Magazine', desc: 'Εφημερίδα/multi-column, masthead, στήλες.' },
  warmth: { label: 'Warmth', desc: 'Ζεστό hospitality, menu-style — ταβέρνες/φούρνοι.' },
  ember: {
    label: 'Ember', desc: 'Νυχτερινή ψησταριά — καπνιστό, λάμψη κάρβουνου, κατάλογος. Premium food/night.',
    /* ΣΚΟΥΡΟ theme. Οι πέντε κοινές παλέτες έχουν όλες ανοιχτή επιφάνεια, και
       η ταυτότητα εδώ στηρίζεται σε δευτερεύοντα χρώματα που διαβάζονται ΜΟΝΟ σε
       σκούρο φόντο (μετρήθηκε: --brass 7,89:1 στο δικό του, 2,12:1 σε warm). Με ανοιχτή παλέτα το theme δεν
       «αλλάζει χρώμα», σπάει. Γίνεται true όταν αποκτήσουμε σκούρες παλέτες. */
    customizable: { palette: false, fontPair: true },
  },
  marble: { label: 'Marble', desc: 'Minimal-luxe — πορσελάνη, χρυσές hairlines, ευρετήριο τομέων. Δικηγόροι/ιατροί.' },
  runway: { label: 'Gallery Noir', desc: 'Ασπρόμαυρη gallery με μία έντονη υπογραφή και έργα σε πρώτο πλάνο.' },
  forge: {
    label: 'Workshop', desc: 'Βιομηχανικό εργαστήριο — ατσάλι, safety yellow και δυνατή αξιοπιστία.',
    /* Ανοιχτή επιφάνεια — ο spine guard επαληθεύει την αντίθεση σε κάθε παλέτα. */
    customizable: { palette: true, fontPair: true },
  },
  aegean: { label: 'Aegean', desc: 'Κυκλαδίτικο — full-bleed θάλασσα, καρτ-ποστάλ gallery. Τουρισμός/δωμάτια.' },
  bloom: { label: 'Bloom', desc: 'Πρωινό φως — καμάρες βιτρίνας, βοτανικό πράσινο. Καφέ/φούρνοι.' },
  pulse: { label: 'Pulse', desc: 'Κλινική ηρεμία — λευκό/teal, γραμμή παλμού. Ιατρεία/κλινικές.' },
  volt: {
    label: 'Volt', desc: 'Ενέργεια — ανθρακί + electric lime, διαγώνιες τομές. Γυμναστήρια.',
    /* ΣΚΟΥΡΟ theme. Οι πέντε κοινές παλέτες έχουν όλες ανοιχτή επιφάνεια, και
       η ταυτότητα εδώ στηρίζεται σε δευτερεύοντα χρώματα που διαβάζονται ΜΟΝΟ σε
       σκούρο φόντο (μετρήθηκε: ο τίτλος του hero έγινε δυσανάγνωστος πάνω στη φωτογραφία). Με ανοιχτή παλέτα το theme δεν
       «αλλάζει χρώμα», σπάει. Γίνεται true όταν αποκτήσουμε σκούρες παλέτες. */
    customizable: { palette: false, fontPair: true },
  },
  motor: {
    label: 'Motor', desc: 'Γκαράζ — gunmetal, signal red, δελτίο εργασιών. Συνεργεία.',
    /* ΣΚΟΥΡΟ theme. Οι πέντε κοινές παλέτες έχουν όλες ανοιχτή επιφάνεια, και
       η ταυτότητα εδώ στηρίζεται σε δευτερεύοντα χρώματα που διαβάζονται ΜΟΝΟ σε
       σκούρο φόντο (μετρήθηκε: --steel 8,35:1 στο δικό του, 1,81:1 σε warm). Με ανοιχτή παλέτα το theme δεν
       «αλλάζει χρώμα», σπάει. Γίνεται true όταν αποκτήσουμε σκούρες παλέτες. */
    customizable: { palette: false, fontPair: true },
  },
  canvas: { label: 'Portfolio Canvas', desc: 'Κατάλογος έργων με ήρεμη πολυτέλεια και μεγάλες φωτογραφίες.' },
  dispatch: { label: 'One Screen', desc: 'Μία οθόνη, μηδέν σκρολ — κινηματογραφικό φόντο και τηλέφωνο-ήρωας.' },
  terra: {
    label: 'Terra', desc: 'Γη & kraft — ετικέτες προϊόντων, ελιά. Παραγωγοί/αγροτικά.',
    /* Ανοιχτή επιφάνεια — ο spine guard επαληθεύει την αντίθεση σε κάθε παλέτα. */
    customizable: { palette: true, fontPair: true },
  },
  cinematic: { label: 'Cinematic Residence', desc: 'Κινηματογραφική αφήγηση χώρου με μεγάλα έργα και ήρεμες μεταβάσεις.' },
  'type-gallery': { label: 'Type Gallery', desc: 'Εκφραστική τυπογραφία, poster ρυθμός και τολμηρή παρουσίαση έργων.' },
  quiet: { label: 'Quiet Precision', desc: 'Ήρεμη ακρίβεια, λεπτομέρεια και αυστηρή minimal σύνθεση.' },
  kinetic: { label: 'Kinetic Workshop', desc: 'Motion-first layout με clipped reveals, marquee και δυναμική τυπογραφία.' },
  infinite: { label: 'Infinite Showroom', desc: 'Οριζόντια περιήγηση έργων, sticky αφήγηση και αίσθηση showroom.' },
  living: { label: 'Living Material', desc: 'Οργανικές φόρμες, υλικά και tactile παρουσίαση με απαλή κίνηση.' },
  'beauty-atelier': { label: 'Beauty Atelier', desc: 'Premium editorial εμπειρία για νύχια, κομμωτήριο και αισθητική, με υπηρεσίες, έργα και booking-first ροή.' },
  callout: {
    label: 'Τεχνίτης', desc: 'Επείγουσα κλήση — κάρτα προσφοράς πάνω στο hero, μεγάλο τηλέφωνο, αριθμημένες υπηρεσίες.',
    category: 'trade', style: 'urgent-utility',
    /* Το palette ήταν `false` επειδή το theme όντως έσπαγε: το amber δούλευε ως
       φόντο κουμπιού και ήταν αδιάβαστο ως κείμενο. Μετά τη μετάβαση στο spine
       οι δύο δουλειές είναι δύο ρόλοι και το `tests/spine_guard.mjs` επαληθεύει
       την αντίθεση σε κάθε παλέτα — οπότε είναι πλέον αληθινά `true`.
       Το fontPair μένει `false`: η συμπυκνωμένη γραφή ΕΙΝΑΙ η ταυτότητα. */
    customizable: { palette: true, fontPair: false },
    variants: {},
    sections: ['nav', 'hero+quote', 'segments', 'services', 'why', 'work', 'band', 'findus', 'footer'],
    requiredAssets: { minServices: 3, minGallery: 0 },
    imageRatios: { hero: '16/9', work: '4/3' },
    tokens: { display: 'Fira Sans Condensed', body: 'Open Sans', accent: '#ffb020', navy: '#0e1a2b' },
  },
  'clinic-triage': {
    label: 'Ιατρείο', desc: 'Ήρεμο ιατρικό — τρεις κάρτες «τι θέλεις να κάνεις», εναλλασσόμενα panels και σκούρα ζώνη τηλεφώνου.',
    category: 'health', style: 'clinical-triage',
    customizable: { palette: true, fontPair: true },
    variants: { hero: ['image-left', 'image-right'] },
    sections: ['nav', 'hero', 'triage', 'services', 'why', 'gallery', 'ribbon', 'findus', 'footer'],
    requiredAssets: { minServices: 3, minGallery: 3 },
    imageRatios: { hero: '16/9', panel: '3/2', gallery: '16/9' },
    tokens: { display: 'Noto Sans Display', body: 'Open Sans', accent: '#0078bf', container: '1300px', radius: '10px' },
  },
  'bakery-editorial': { label: 'Bakery Editorial', desc: 'Μεγάλη φωτογραφία, refined τυπογραφία και premium αφήγηση προϊόντος.' },
  'counter-menu': { label: 'Counter Menu', desc: 'Conversion-first πάγκος με menu board, ωράριο και άμεση επικοινωνία.' },
  'morning-journal': { label: 'Morning Journal', desc: 'Editorial εφημερίδα γειτονιάς με ιστορία, προϊόν και καθαρή πληροφορία.' },
  'neighborhood-market': { label: 'Neighborhood Market', desc: 'Χρώμα, modular tiles και ζωντανή local ταυτότητα για σύγχρονο καφέ ή φούρνο.' },
  'microbakery-lab': { label: 'Microbakery Lab', desc: 'Πειραματικό monochrome grid, process-first αφήγηση και έντονη τυπογραφία.' },
  'scandinavian-coffee': { label: 'Scandinavian Coffee House', desc: 'Φως, αρχιτεκτονική φωτογραφία και ήρεμη specialty coffee εμπειρία.' },
  'heritage-bakery': { label: 'Heritage Bakery', desc: 'Οικογενειακή ιστορία, πλούσια προϊόντα και σύγχρονη ελληνική παράδοση.' },
}

// Map backend layout names → React archetype (until backend adopts react keys).
const MAP = {
  studio: 'editorial', trust: 'editorial', commerce: 'editorial', warmth: 'editorial',
  atelier: 'split', noir: 'split',
  fresh: 'showcase', bold: 'showcase', coast: 'showcase',
  professional: 'corporate', trade: 'corporate',
  editorial: 'editorial', split: 'split', showcase: 'showcase', bento: 'bento', longform: 'longform', corporate: 'corporate',
  poster: 'poster', sidebar: 'sidebar', grid: 'grid', coast: 'coast', magazine: 'magazine', warmth: 'warmth',
}
export function pickTemplate(layout) {
  return TEMPLATES[MAP[layout] || layout] || Editorial
}

/**
 * Τι επιτρέπεται να αλλάξει ο πελάτης σε ΑΥΤΟ το theme.
 *
 * Το SKILL.md λέει ότι ο editor οδηγείται από τα metadata, «ποτέ από hardcoded
 * conditions» — αλλά ο renderer έβαζε `data-font` σε κάθε site ανεξαιρέτως, με
 * αποτέλεσμα ένα theme που δηλώνει «η τυπογραφία μου σπάει» να τη χάνει σε κάθε
 * πελάτη. Η δήλωση πρέπει να δεσμεύει.
 *
 * Προεπιλογή `true`: τα themes χωρίς metadata κρατούν τη σημερινή συμπεριφορά.
 */
export function themeControls(key) {
  const c = TEMPLATE_META[key]?.customizable
  return { palette: c?.palette !== false, fontPair: c?.fontPair !== false }
}
