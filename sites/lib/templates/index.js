import { AreaFirst, HorizontalStory, PriceFirst, ChapterSnap, DirectoryIndex, VerticalSnap } from './CafeCollection'
import KlassyTable from './KlassyTable'
import BarberSidebar from './BarberSidebar'
import VillaAgency from './VillaAgency'
import GymsoFitness from './GymsoFitness'
import MedicCare from './MedicCare'
import FrostBakery from './FrostBakery'
import EleganceSalon from './EleganceSalon'
import GreckoTable from './GreckoTable'
import NovenaCare from './NovenaCare'
import BigspringAdvisory from './BigspringAdvisory'
import ConstraBuild from './ConstraBuild'
import PropertyAtlas from './PropertyAtlas'
import EducenterCampus from './EducenterCampus'
import VexCounter from './VexCounter'
import AirspaceOffice from './AirspaceOffice'
import FreightLane from './FreightLane'
import BlueOnepage from './BlueOnepage'
import BillysBarber from './BillysBarber'
import ThomsonStylist from './ThomsonStylist'
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
import Signature from './Signature'
import { BakeryEditorial, CounterMenu, MorningJournal, NeighborhoodMarket, MicrobakeryLab, ScandinavianCoffeeHouse, HeritageBakery } from './CafeCollection'

// Structurally-distinct React archetypes.
export const TEMPLATES = { 'klassy-cafe': KlassyTable, 'barber-shop': BarberSidebar, 'villa-agency': VillaAgency, 'gymso-fitness': GymsoFitness, 'medic-care': MedicCare, 'frost-bakery': FrostBakery, 'area-first': AreaFirst, 'horizontal-story': HorizontalStory, 'price-first': PriceFirst, 'chapter-snap': ChapterSnap, 'directory-index': DirectoryIndex, 'vertical-snap': VerticalSnap, 'elegance-salon': EleganceSalon, 'grecko-table': GreckoTable, 'novena-care': NovenaCare, 'bigspring-advisory': BigspringAdvisory, 'constra-build': ConstraBuild, 'property-atlas': PropertyAtlas, 'educenter-campus': EducenterCampus, 'vex-counter': VexCounter, 'airspace-office': AirspaceOffice, 'freight-lane': FreightLane, 'blue-onepage': BlueOnepage, 'billys-barber': BillysBarber, 'thomson-stylist': ThomsonStylist, editorial: Editorial, split: Split, showcase: Showcase, bento: Bento, longform: Longform, corporate: Corporate, poster: Poster, sidebar: Sidebar, grid: GridT, coast: Coast, magazine: Magazine, warmth: Warmth, ember: Ember, marble: Marble, runway: Runway, forge: Forge, aegean: Aegean, bloom: Bloom, pulse: Pulse, volt: Volt, motor: Motor, terra: Terra, dispatch: Dispatch, canvas: Canvas, cinematic: Cinematic, 'type-gallery': TypeGallery, quiet: Quiet, kinetic: Kinetic, infinite: Infinite, living: Living, 'beauty-atelier': BeautyAtelier, 'clinic-triage': ClinicTriage, callout: Callout, signature: Signature, 'bakery-editorial': BakeryEditorial, 'counter-menu': CounterMenu, 'morning-journal': MorningJournal, 'neighborhood-market': NeighborhoodMarket, 'microbakery-lab': MicrobakeryLab, 'scandinavian-coffee': ScandinavianCoffeeHouse, 'heritage-bakery': HeritageBakery }
// The public collection stays intentionally curated. Legacy templates remain
// renderable for existing clients but are not offered to new customers.
export const TEMPLATE_KEYS = ['klassy-cafe', 'barber-shop', 'villa-agency', 'gymso-fitness', 'medic-care', 'frost-bakery', 'area-first', 'horizontal-story', 'price-first', 'chapter-snap', 'directory-index', 'vertical-snap', 'elegance-salon', 'grecko-table', 'novena-care', 'bigspring-advisory', 'constra-build', 'property-atlas', 'educenter-campus', 'vex-counter', 'airspace-office', 'freight-lane', 'blue-onepage', 'billys-barber', 'thomson-stylist', 'editorial', 'split', 'bento', 'longform', 'poster', 'sidebar', 'grid', 'magazine', 'warmth', 'ember', 'marble', 'runway', 'forge', 'aegean', 'bloom', 'volt', 'motor', 'terra', 'dispatch', 'canvas', 'cinematic', 'type-gallery', 'quiet', 'kinetic', 'infinite', 'living', 'beauty-atelier', 'clinic-triage', 'callout', 'signature', 'bakery-editorial', 'counter-menu', 'morning-journal', 'neighborhood-market', 'microbakery-lab', 'scandinavian-coffee', 'heritage-bakery']
export const LAUNCH_TEMPLATE_KEYS = [ 'elegance-salon', 'grecko-table', 'novena-care', 'bigspring-advisory', 'constra-build', 'property-atlas', 'beauty-atelier', 'clinic-triage', 'callout', 'signature', 'cinematic', 'bakery-editorial' ];
export const LEGACY_TEMPLATE_KEYS = ['showcase', 'corporate', 'coast', 'pulse']
export const TEMPLATE_META = {
  'klassy-cafe': { label: 'Klassy Table', desc: 'Πιστό port του Klassy Cafe: split hero με χρωματικό πλακίδιο, μενού-carousel με τιμές, εβδομαδιαίες προσφορές.', category: 'food', customizable: { palette: false, fontPair: false } },
  'barber-shop': { label: 'Barber Sidebar', desc: 'Πιστό port του Barber Shop (Templatemo): σταθερή πλαϊνή πλοήγηση, υπηρεσίες-κάρτες με τιμή, τιμοκατάλογος.', category: 'beauty', customizable: { palette: false, fontPair: false } },
  'villa-agency': { label: 'Villa Agency', desc: 'Πιστό port του Villa Agency (Templatemo): κάρτες ακινήτων με τιμή και προδιαγραφές, φίλτρα κατηγορίας.', category: 'property', customizable: { palette: false, fontPair: false } },
  'gymso-fitness': { label: 'Gymso Fitness', desc: 'Πιστό port του Gymso (Tooplate): σκούρο hero, μαθήματα με τιμή και εβδομαδιαίο πρόγραμμα σε πλέγμα.', category: 'fitness', customizable: { palette: false, fontPair: false } },
  'medic-care': { label: 'Medic Care', desc: 'Πιστό port του Medic Care (Templatemo): ήρεμο μπλε/λευκό για μονοπρόσωπο ιατρείο, εναλλασσόμενο timeline, ωράριο και διεύθυνση στο footer.', category: 'medical', customizable: { palette: false, fontPair: false } },
  'frost-bakery': { label: 'Frost Bakery', desc: 'Πιστό port του Frost Bakery (Templatemo): πλαϊνή πλοήγηση με ωράριο, παστέλ παλέτα, display serif, εποχιακά tabs και αριθμημένα βήματα.', category: 'food', customizable: { palette: false, fontPair: false } },
  'area-first': { label: 'Service Radius', desc: 'Premium qualification ροή για περιοχή, υπηρεσία και άμεση διαθεσιμότητα.', category: 'capability', customizable: { palette: false, fontPair: false } },
  'horizontal-story': { label: 'Horizontal Story', desc: 'Χωρική αφήγηση σε οριζόντια scenes με σκόπιμη κάθετη mobile εκδοχή.', category: 'spatial', customizable: { palette: false, fontPair: false } },
  'price-first': { label: 'Price Board', desc: 'Οι υπηρεσίες, η διάρκεια και το κόστος γίνονται το κύριο περιεχόμενο.', category: 'commerce', customizable: { palette: false, fontPair: false } },
  'chapter-snap': { label: 'Chapter Snap', desc: 'Fullscreen κεφάλαια με anchors, προαιρετικό snap και καθαρό mobile fallback.', category: 'narrative', customizable: { palette: false, fontPair: false } },
  'directory-index': { label: 'Directory Index', desc: 'Η αρχική γίνεται διαδραστικό ευρετήριο υπηρεσιών και πληροφοριών.', category: 'information', customizable: { palette: false, fontPair: false } },
  'vertical-snap': { label: 'Fullscreen Story', desc: 'Ένα κινηματογραφικό κεφάλαιο ανά οθόνη με ελεγχόμενη κάθετη αφήγηση.', category: 'narrative', customizable: { palette: false, fontPair: false } },
  'elegance-salon': { label: 'Elegance Salon', desc: 'Editorial salon εμπειρία με booking-first ροή, lookbook και ήρεμη πολυτέλεια.', category: 'beauty', customizable: { palette: false, fontPair: false } },
  'grecko-table': { label: 'Grecko Table', desc: 'Μεσογειακή φιλοξενία με δυνατή εισαγωγή, menu rhythm και κράτηση στο επίκεντρο.', category: 'food', customizable: { palette: false, fontPair: false } },
  'novena-care': { label: 'Novena Care', desc: 'Καθαρή ιατρική εμπειρία με υπηρεσίες, εμπιστοσύνη και άμεσο ραντεβού.', category: 'health', customizable: { palette: false, fontPair: false } },
  'bigspring-advisory': { label: 'Bigspring Advisory', desc: 'Σύγχρονο επαγγελματικό site με καθαρή ιεραρχία και consulting χαρακτήρα.', category: 'professional', customizable: { palette: false, fontPair: false } },
  'constra-build': { label: 'Constra Build', desc: 'Ισχυρή τεχνική παρουσία με έργα, υπηρεσίες και άμεση προσφορά.', category: 'trade', customizable: { palette: false, fontPair: false } },
  'property-atlas': { label: 'Property Atlas', desc: 'Map-led παρουσίαση ακινήτων με listings, περιοχές και καθαρή επικοινωνία.', category: 'property', customizable: { palette: false, fontPair: false } },
  'educenter-campus': { label: 'Educenter Campus', desc: 'Ακαδημαϊκή ηρεμία με προγράμματα, πρακτικές πληροφορίες εγγραφής και τρία βήματα έναρξης.', category: 'education', customizable: { palette: false, fontPair: false } },
  'vex-counter': { label: 'Vex Counter', desc: 'Product-first λιανικό: τεράστια τυπογραφία, πλέγμα προϊόντων και \xabπέρνα από το μαγαζί\xbb.', category: 'retail', customizable: { palette: false, fontPair: false } },
  'airspace-office': { label: 'Airspace Office', desc: 'Επαγγελματικές υπηρεσίες με αέρα, λεπτές γραμμές και υπηρεσίες σε σειρές αντί για κάρτες.', category: 'professional', customizable: { palette: false, fontPair: false } },
  'freight-lane': { label: 'Freight Lane', desc: 'Μεταφορές και logistics: σκούρο, high-vis, με τηλέφωνο που δεν φεύγει από την οθόνη.', category: 'logistics', customizable: { palette: false, fontPair: false } },
  'blue-onepage': { label: 'Blue Onepage', desc: 'Πιστό port του Blue (Themefisher): σκούρο nav, hero slider, μπλε ζώνη, κεντραρισμένες ενότητες και πλέγμα έργων.', category: 'beauty', customizable: { palette: false, fontPair: false } },
  'billys-barber': { label: 'Billy', desc: 'Πιστό port: γκρι σώμα, σερίφ κόκκινες επικεφαλίδες, κατακόρυφος τίτλος στο περιθώριο και δίστηλος κατάλογος υπηρεσιών.', category: 'beauty', customizable: { palette: false, fontPair: false } },
  'thomson-stylist': { label: 'Thomson Stylist', desc: 'Πιστό port: αριστερή δήλωση με τεράστια τυπογραφία, πολύ λευκό, πλέγμα δουλειάς και υπηρεσίες με εικονίδια. Για ανεξάρτητο hair artist.', category: 'beauty', customizable: { palette: false, fontPair: false } },
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
  dispatch: {
    label: 'One Screen', desc: 'Μία οθόνη, μηδέν σκρολ — κινηματογραφικό φόντο και τηλέφωνο-ήρωας.',
    /* ΣΚΟΥΡΟ theme πάνω σε φωτογραφία. Με ανοιχτή παλέτα η κάρτα γίνεται σκούρη
       σε σκούρο: το όνομα και οι υπηρεσίες έγιναν δυσανάγνωστα (φωτογραφήθηκε).
       Ο spine guard ΔΕΝ το πιάνει — μετράει ζεύγη ρόλων, ενώ εδώ το κείμενο
       κάθεται πάνω σε ημιδιαφανές panel και φωτογραφία, όχι πάνω στο surface. */
    customizable: { palette: false, fontPair: true },
  },
  terra: {
    label: 'Terra', desc: 'Γη & kraft — ετικέτες προϊόντων, ελιά. Παραγωγοί/αγροτικά.',
    /* Ανοιχτή επιφάνεια — ο spine guard επαληθεύει την αντίθεση σε κάθε παλέτα. */
    customizable: { palette: true, fontPair: true },
  },
  cinematic: {
    label: 'Cinematic Residence', desc: 'Κινηματογραφική αφήγηση χώρου με μεγάλα έργα και ήρεμες μεταβάσεις.',
    /* ΣΚΟΥΡΟ theme με κείμενο πάνω σε φωτογραφία. Με ανοιχτή παλέτα ο τίτλος του
       hero γίνεται σκούρος πάνω σε φωτεινή εικόνα (φωτογραφήθηκε). Ο spine guard δεν το
       πιάνει: μετράει ζεύγη ρόλων, όχι κείμενο πάνω σε φωτογραφία. */
    customizable: { palette: false, fontPair: true },
  },
  'type-gallery': { label: 'Type Gallery', desc: 'Εκφραστική τυπογραφία, poster ρυθμός και τολμηρή παρουσίαση έργων.' },
  quiet: { label: 'Quiet Precision', desc: 'Ήρεμη ακρίβεια, λεπτομέρεια και αυστηρή minimal σύνθεση.' },
  kinetic: { label: 'Kinetic Workshop', desc: 'Motion-first layout με clipped reveals, marquee και δυναμική τυπογραφία.' },
  infinite: {
    label: 'Infinite Showroom', desc: 'Οριζόντια περιήγηση έργων, sticky αφήγηση και αίσθηση showroom.',
    /* ΣΚΟΥΡΟ theme με κείμενο πάνω σε φωτογραφία. Με ανοιχτή παλέτα ο τίτλος του
       hero γίνεται σκούρος πάνω σε φωτεινή εικόνα (ο τίτλος έγινε σχεδόν αόρατος). Ο spine guard δεν το
       πιάνει: μετράει ζεύγη ρόλων, όχι κείμενο πάνω σε φωτογραφία. */
    customizable: { palette: false, fontPair: true },
  },
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
  signature: {
    label: 'Προσωπικό', desc: 'Ο άνθρωπος είναι η μάρκα — το όνομα ως τίτλος, τυπογραφικό ευρετήριο υπηρεσιών, υπογραφή στο τέλος.',
    category: 'professional', style: 'personal-editorial',
    customizable: { palette: true, fontPair: true },
    /* Δύο τρόποι ίδιας αξίας: με πορτρέτο ή με μονόγραμμα + κάρτα αληθινών
       στοιχείων. Ποτέ stock πρόσωπο — ψεύτικο πρόσωπο σε site προσώπου. */
    variants: { hero: ['portrait', 'monogram'] },
    sections: ['nav', 'hero', 'services', 'approach', 'story', 'strip', 'cta', 'findus', 'footer'],
    requiredAssets: { minServices: 2, minGallery: 0 },
    imageRatios: { portrait: '4/5', strip: '4/3' },
    tokens: { display: 'Fraunces', body: 'Inter', accent: '#2f5d63' },
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
  'bakery-editorial': {
    label: 'Bakery Editorial', desc: 'Μεγάλη φωτογραφία, refined τυπογραφία και premium αφήγηση προϊόντος.',
    /* CafeCollection — επτά ταυτότητες σε ένα αρχείο, κοινό structural .root.
       Ένα accent, μία σκούρα ζώνη. Η ταυτότητα είναι η τυπογραφία (Georgia editorial) και ο ρυθμός. */
    customizable: { palette: true, fontPair: true },
  },
  'counter-menu': {
    label: 'Counter Menu', desc: 'Conversion-first πάγκος με menu board, ωράριο και άμεση επικοινωνία.',
    /* CafeCollection — επτά ταυτότητες σε ένα αρχείο, κοινό structural .root.
       ΔΥΟ ανεξάρτητα accents ως φόντα ενοτήτων (lime menu, κόκκινο visit). Το «electric» δεν εκφράζεται με ένα accent. */
    customizable: { palette: false, fontPair: true },
  },
  'morning-journal': {
    label: 'Morning Journal', desc: 'Editorial εφημερίδα γειτονιάς με ιστορία, προϊόν και καθαρή πληροφορία.',
    /* CafeCollection — επτά ταυτότητες σε ένα αρχείο, κοινό structural .root.
       ΔΟΚΙΜΑΣΤΗΚΕ ΟΠΤΙΚΑ και απορρίφθηκε: η κίτρινη ζώνη είναι υπογραφή, όχι
       εναλλασσόμενο tint. Σε ocean γίνεται σχεδόν λευκή και το terracotta teal —
       μένει γενική ψυχρή σελίδα, χάνεται ο «φούρνος της γειτονιάς». */
    customizable: { palette: false, fontPair: true },
  },
  'neighborhood-market': {
    label: 'Neighborhood Market', desc: 'Χρώμα, modular tiles και ζωντανή local ταυτότητα για σύγχρονο καφέ ή φούρνο.',
    /* CafeCollection — επτά ταυτότητες σε ένα αρχείο, κοινό structural .root.
       ΤΕΣΣΕΡΑ χρώματα ως φόντα ενοτήτων — είναι το δηλωμένο concept, όχι διακόσμηση. */
    customizable: { palette: false, fontPair: true },
  },
  'microbakery-lab': {
    label: 'Microbakery Lab', desc: 'Πειραματικό monochrome grid, process-first αφήγηση και έντονη τυπογραφία.',
    /* CafeCollection — επτά ταυτότητες σε ένα αρχείο, κοινό structural .root.
       Monochrome + ένα safety red. Η ταυτότητα είναι το αυστηρό grid, όχι το χρώμα. */
    customizable: { palette: true, fontPair: true },
  },
  'scandinavian-coffee': {
    label: 'Scandinavian Coffee House', desc: 'Φως, αρχιτεκτονική φωτογραφία και ήρεμη specialty coffee εμπειρία.',
    /* CafeCollection — επτά ταυτότητες σε ένα αρχείο, κοινό structural .root.
       Ένα sage band, ένα σκούρο. Η ταυτότητα είναι το φως και ο χώρος. */
    customizable: { palette: true, fontPair: true },
  },
  'heritage-bakery': {
    label: 'Heritage Bakery', desc: 'Οικογενειακή ιστορία, πλούσια προϊόντα και σύγχρονη ελληνική παράδοση.',
    /* CafeCollection — επτά ταυτότητες σε ένα αρχείο, κοινό structural .root.
       Χρυσή ζώνη + terracotta = δύο signature χρώματα. Με ένα accent καταρρέουν σε ένα. */
    customizable: { palette: false, fontPair: true },
  },
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
