import { AreaFirst, HorizontalStory, PriceFirst, ChapterSnap, DirectoryIndex, VerticalSnap } from './CapabilitySystems'
import MosoShowroom from './MosoShowroom'
import CleanService from './CleanService'
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
export const TEMPLATES = { 'moso-interior': MosoShowroom, 'clean-work': CleanService, 'klassy-cafe': KlassyTable, 'barber-shop': BarberSidebar, 'villa-agency': VillaAgency, 'gymso-fitness': GymsoFitness, 'medic-care': MedicCare, 'frost-bakery': FrostBakery, 'area-first': AreaFirst, 'horizontal-story': HorizontalStory, 'price-first': PriceFirst, 'chapter-snap': ChapterSnap, 'directory-index': DirectoryIndex, 'vertical-snap': VerticalSnap, 'elegance-salon': EleganceSalon, 'grecko-table': GreckoTable, 'novena-care': NovenaCare, 'bigspring-advisory': BigspringAdvisory, 'constra-build': ConstraBuild, 'property-atlas': PropertyAtlas, 'educenter-campus': EducenterCampus, 'vex-counter': VexCounter, 'airspace-office': AirspaceOffice, 'freight-lane': FreightLane, 'blue-onepage': BlueOnepage, 'billys-barber': BillysBarber, 'thomson-stylist': ThomsonStylist, editorial: Editorial, split: Split, showcase: Showcase, bento: Bento, longform: Longform, corporate: Corporate, poster: Poster, sidebar: Sidebar, grid: GridT, coast: Coast, magazine: Magazine, warmth: Warmth, ember: Ember, marble: Marble, runway: Runway, forge: Forge, aegean: Aegean, bloom: Bloom, pulse: Pulse, volt: Volt, motor: Motor, terra: Terra, dispatch: Dispatch, canvas: Canvas, cinematic: Cinematic, 'type-gallery': TypeGallery, quiet: Quiet, kinetic: Kinetic, infinite: Infinite, living: Living, 'beauty-atelier': BeautyAtelier, 'clinic-triage': ClinicTriage, callout: Callout, signature: Signature, 'bakery-editorial': BakeryEditorial, 'counter-menu': CounterMenu, 'morning-journal': MorningJournal, 'neighborhood-market': NeighborhoodMarket, 'microbakery-lab': MicrobakeryLab, 'scandinavian-coffee': ScandinavianCoffeeHouse, 'heritage-bakery': HeritageBakery }
// The public collection stays intentionally curated. Legacy templates remain
// renderable for existing clients but are not offered to new customers.
export const TEMPLATE_KEYS = ['moso-interior', 'clean-work', 'klassy-cafe', 'barber-shop', 'villa-agency', 'gymso-fitness', 'medic-care', 'frost-bakery', 'area-first', 'horizontal-story', 'price-first', 'chapter-snap', 'directory-index', 'vertical-snap', 'elegance-salon', 'grecko-table', 'novena-care', 'bigspring-advisory', 'constra-build', 'property-atlas', 'educenter-campus', 'vex-counter', 'airspace-office', 'freight-lane', 'blue-onepage', 'billys-barber', 'thomson-stylist', 'editorial', 'split', 'bento', 'longform', 'poster', 'sidebar', 'grid', 'magazine', 'warmth', 'ember', 'marble', 'runway', 'forge', 'aegean', 'bloom', 'volt', 'motor', 'terra', 'dispatch', 'canvas', 'cinematic', 'type-gallery', 'quiet', 'kinetic', 'infinite', 'living', 'beauty-atelier', 'clinic-triage', 'callout', 'signature', 'bakery-editorial', 'counter-menu', 'morning-journal', 'neighborhood-market', 'microbakery-lab', 'scandinavian-coffee', 'heritage-bakery']
export const LAUNCH_TEMPLATE_KEYS = [ 'elegance-salon', 'grecko-table', 'novena-care', 'bigspring-advisory', 'constra-build', 'property-atlas', 'beauty-atelier', 'clinic-triage', 'callout', 'signature', 'cinematic', 'bakery-editorial' ];
export const LEGACY_TEMPLATE_KEYS = ['showcase', 'corporate', 'coast', 'pulse']
export const TEMPLATE_META = {
  /* Ονόματα και περιγραφές ΠΡΟΣ ΤΟΝ ΠΕΛΑΤΗ. Καμία αναφορά σε
     εσωτερικό id, port ή πηγή template. Παράγεται από
     research/theme-library/catalog.py — μην το γράφεις με το χέρι. */
  aegean: { label: 'Αιγαίο', desc: 'Κυκλαδίτικο φως, μεγάλη θαλασσινή φωτογραφία και ήρεμη τυπογραφία.', category: 'Τουρισμός & διαμονή', primary: 'rooms', verticals: ["massage", "rooms"], generic: false, customizable: { palette: true, fontPair: true } },
  'airspace-office': { label: 'Γραφείο', desc: 'Εταιρικό και καθαρό, με ομάδα, υπηρεσίες και επικοινωνία.', category: 'Επαγγελματικές υπηρεσίες', primary: 'professional', verticals: ["professional"], generic: false, customizable: { palette: false, fontPair: false } },
  'area-first': { label: 'Περιοχές Πρώτα', desc: 'Οι περιοχές εξυπηρέτησης μπροστά — για τοπικό τεχνίτη.', category: 'Τεχνικά επαγγέλματα', primary: 'logistics', verticals: ["logistics", "trade"], generic: false, customizable: { palette: false, fontPair: false } },
  'bakery-editorial': { label: 'Φούρνος Editorial', desc: 'Αφήγηση σαν περιοδικό, με το ψωμί και τη διαδικασία πρωταγωνιστές.', category: 'Εστίαση', primary: 'bakery', verticals: ["bakery", "food"], generic: false, customizable: { palette: true, fontPair: true } },
  'barber-shop': { label: 'Κουρείο', desc: 'Σκούρο, αντρικό, με τιμοκατάλογο και ωράριο σε πλαϊνή στήλη.', category: 'Ομορφιά', primary: 'beauty', verticals: ["aesthetics", "beauty", "massage"], generic: false, customizable: { palette: false, fontPair: false } },
  'beauty-atelier': { label: 'Ατελιέ Ομορφιάς', desc: 'Ήρεμη πολυτέλεια, lookbook και ραντεβού χωρίς τριβή.', category: 'Ομορφιά', primary: 'aesthetics', verticals: ["aesthetics", "beauty"], generic: false, customizable: { palette: true, fontPair: true } },
  bento: { label: 'Bento', desc: 'Βασικό αρχέτυπο πλακιδίων. Εσωτερική υποδομή συμβατότητας.', category: 'Εσωτερικά', primary: 'retail', verticals: ["aesthetics", "gym", "pet", "pharmacy", "realestate", "retail"], generic: false, internal: true, customizable: { palette: true, fontPair: true } },
  'bigspring-advisory': { label: 'Συμβουλευτική', desc: 'Σοβαρό και δομημένο, με υπηρεσίες και αίτημα ραντεβού.', category: 'Επαγγελματικές υπηρεσίες', primary: 'professional', verticals: ["dentist", "doctor", "education", "logistics", "professional", "realestate"], generic: false, customizable: { palette: false, fontPair: false } },
  'billys-barber': { label: 'Κουρείο Vintage', desc: 'Ρετρό ύφος με έντονη τυπογραφία και άμεσο τηλέφωνο.', category: 'Ομορφιά', primary: 'beauty', verticals: ["aesthetics", "beauty", "massage"], generic: false, customizable: { palette: false, fontPair: false } },
  bloom: { label: 'Άνθιση', desc: 'Καθαρό λευκό με στρογγυλή φωτογραφία-ήρωα και ζεστό πράσινο κουμπί.', category: 'Υγεία', primary: 'aesthetics', verticals: ["aesthetics", "bakery", "cafe", "food", "massage", "pet"], generic: false, customizable: { palette: true, fontPair: true } },
  'blue-onepage': { label: 'Μονοσέλιδο', desc: 'Όλα σε μία σελίδα, με ενότητες που κυλούν ομαλά.', category: 'Επαγγελματικές υπηρεσίες', primary: 'professional', verticals: ["professional"], generic: false, customizable: { palette: false, fontPair: false } },
  callout: { label: 'Επείγουσα Κλήση', desc: 'Το τηλέφωνο βλάβης σε πρώτο πλάνο. Για 24/7 εξυπηρέτηση.', category: 'Τεχνικά επαγγέλματα', primary: 'trade', verticals: ["trade"], generic: false, customizable: { palette: true, fontPair: true } },
  canvas: { label: 'Καμβάς', desc: 'Ήσυχο editorial με μεγάλη εικόνα και serif αφήγηση.', category: 'Ευέλικτο', primary: 'farm', verticals: ["aesthetics", "dentist", "doctor", "education", "farm", "garage", "logistics", "massage", "pet", "pharmacy", "professional", "realestate", "retail", "rooms", "wood"], generic: true, customizable: { palette: true, fontPair: true } },
  'chapter-snap': { label: 'Κεφάλαια', desc: 'Κάθε ενότητα γεμίζει την οθόνη — σαν κεφάλαια βιβλίου.', category: 'Τουρισμός & διαμονή', primary: 'education', verticals: ["beauty", "education", "rooms"], generic: false, customizable: { palette: false, fontPair: false } },
  cinematic: { label: 'Κινηματογραφικό', desc: 'Σκούρο, γεμάτο φωτογραφία, με μεγάλη χειρόγραφη τυπογραφία.', category: 'Ευέλικτο', primary: 'food', verticals: ["aesthetics", "beauty", "cafe", "dentist", "doctor", "education", "farm", "food", "garage", "gym", "logistics", "massage", "pet", "professional", "realestate", "retail", "rooms", "trade", "wood"], generic: true, customizable: { palette: true, fontPair: true } },
  'clean-work': { label: 'Καθαρή Δουλειά', desc: 'Λιτό και αξιόπιστο, με υπηρεσίες, περιοχές και άμεση κλήση.', category: 'Τεχνικά επαγγέλματα', primary: 'logistics', verticals: ["logistics"], generic: false, customizable: { palette: false, fontPair: false } },
  'clinic-triage': { label: 'Ιατρείο Διαλογής', desc: 'Οδηγεί τον ασθενή στη σωστή υπηρεσία και μετά στο ραντεβού.', category: 'Υγεία', primary: 'dentist', verticals: ["aesthetics", "dentist", "doctor", "massage", "pharmacy"], generic: false, customizable: { palette: true, fontPair: true } },
  coast: { label: 'Ακτή', desc: 'Ανοιχτό και θαλασσινό, με ευρύχωρο hero και γαλάζιο τόνο.', category: 'Τουρισμός & διαμονή', primary: 'rooms', verticals: ["rooms"], generic: false, customizable: { palette: true, fontPair: true } },
  'constra-build': { label: 'Κατασκευές', desc: 'Έργα, στάδια και προσφορά — για κατασκευαστικό ή τεχνικό γραφείο.', category: 'Τεχνικά επαγγέλματα', primary: 'trade', verticals: ["logistics", "trade", "wood"], generic: false, customizable: { palette: false, fontPair: false } },
  corporate: { label: 'Corporate', desc: 'Βασικό αρχέτυπο εταιρικό. Εσωτερική υποδομή συμβατότητας.', category: 'Εσωτερικά', internal: true, customizable: { palette: true, fontPair: true } },
  'counter-menu': { label: 'Πάγκος', desc: 'Ο κατάλογος ως κύριο περιεχόμενο, γρήγορη ανάγνωση, χωρίς περιττά.', category: 'Εστίαση', primary: 'cafe', verticals: ["cafe"], generic: false, customizable: { palette: false, fontPair: true } },
  'directory-index': { label: 'Ευρετήριο Υπηρεσιών', desc: 'Για πολλές υπηρεσίες: ταξινομημένος κατάλογος με γρήγορη εύρεση.', category: 'Υγεία', primary: 'education', verticals: ["dentist", "education", "professional", "realestate"], generic: false, customizable: { palette: false, fontPair: false } },
  dispatch: { label: 'Βάρδια', desc: 'Σκούρο τεχνικό, με τηλέφωνο και λίστα υπηρεσιών σε κάρτα.', category: 'Τεχνικά επαγγέλματα', primary: 'trade', verticals: ["garage", "trade", "wood"], generic: false, customizable: { palette: true, fontPair: true } },
  editorial: { label: 'Editorial', desc: 'Βασικό αρχέτυπο αφήγησης. Εσωτερική υποδομή συμβατότητας.', category: 'Εσωτερικά', primary: 'pharmacy', verticals: ["dentist", "doctor", "farm", "pet", "pharmacy", "realestate", "retail", "wood"], generic: true, internal: true, customizable: { palette: true, fontPair: true } },
  'educenter-campus': { label: 'Εκπαιδευτικό Κέντρο', desc: 'Προγράμματα, καθηγητές και εγγραφή σε καθαρή δομή.', category: 'Εκπαίδευση', primary: 'education', verticals: ["education"], generic: false, customizable: { palette: false, fontPair: false } },
  'elegance-salon': { label: 'Κομψό Σαλόνι', desc: 'Editorial εμπειρία με ροή booking-first και ήρεμη πολυτέλεια.', category: 'Ομορφιά', primary: 'beauty', verticals: ["beauty"], generic: false, customizable: { palette: false, fontPair: false } },
  ember: { label: 'Χόβολη', desc: 'Πολύ σκούρο με πορτοκαλί λάμψη. Δραματικό για βραδινή εστίαση.', category: 'Εστίαση', primary: 'food', verticals: ["food"], generic: false, customizable: { palette: true, fontPair: true } },
  forge: { label: 'Σφυρήλατο', desc: 'Βιομηχανικό, με κίτρινη ταινία και τούβλο.', category: 'Τεχνικά επαγγέλματα', primary: 'wood', verticals: ["garage", "trade", "wood"], generic: false, customizable: { palette: true, fontPair: true } },
  'freight-lane': { label: 'Μεταφορές', desc: 'Δρομολόγια, κάλυψη και χρόνοι, με καθαρό αίτημα προσφοράς.', category: 'Μεταφορές & Logistics', primary: 'logistics', verticals: ["logistics"], generic: false, customizable: { palette: false, fontPair: false } },
  'frost-bakery': { label: 'Ζαχαροπλαστείο', desc: 'Παστέλ και γλυκιά διάθεση, με βιτρίνα προϊόντων και παραγγελία.', category: 'Εστίαση', primary: 'bakery', verticals: ["bakery", "cafe", "food"], generic: false, customizable: { palette: false, fontPair: false } },
  'grecko-table': { label: 'Μεσογειακό Τραπέζι', desc: 'Φιλοξενία με δυνατή εισαγωγή, ρυθμό καταλόγου και την κράτηση στο επίκεντρο.', category: 'Εστίαση', primary: 'food', verticals: ["food"], generic: false, customizable: { palette: false, fontPair: false } },
  grid: { label: 'Grid', desc: 'Βασικό αρχέτυπο πλέγματος. Εσωτερική υποδομή συμβατότητας.', category: 'Εσωτερικά', primary: 'retail', verticals: ["dentist", "doctor", "education", "farm", "garage", "gym", "logistics", "pet", "pharmacy", "professional", "realestate", "retail", "rooms", "trade", "wood"], generic: true, internal: true, customizable: { palette: true, fontPair: true } },
  'gymso-fitness': { label: 'Γυμναστήριο', desc: 'Πρόγραμμα, συνδρομές και εγγραφή, με έντονη φωτογραφία.', category: 'Γυμναστήριο & ευεξία', primary: 'gym', verticals: ["gym"], generic: false, customizable: { palette: false, fontPair: false } },
  'heritage-bakery': { label: 'Παραδοσιακός Φούρνος', desc: 'Οικογενειακή ιστορία, πλούσια προϊόντα, σύγχρονη ελληνική παράδοση.', category: 'Εστίαση', primary: 'bakery', verticals: ["bakery"], generic: false, customizable: { palette: false, fontPair: true } },
  'horizontal-story': { label: 'Οριζόντια Αφήγηση', desc: 'Το έργο ξετυλίγεται σε οριζόντια ροή, βήμα βήμα.', category: 'Τεχνικά επαγγέλματα', primary: 'wood', verticals: ["wood"], generic: false, customizable: { palette: false, fontPair: false } },
  infinite: { label: 'Συνεχές', desc: 'Αδιάκοπη ροή φωτογραφιών, χωρίς ορατές τομές ενοτήτων.', category: 'Ευέλικτο', primary: 'garage', verticals: ["aesthetics", "beauty", "education", "farm", "food", "garage", "gym", "logistics", "massage", "pet", "pharmacy", "professional", "retail", "rooms", "trade", "wood"], generic: true, customizable: { palette: true, fontPair: true } },
  kinetic: { label: 'Κινητικό', desc: 'Έντονο lime και μεγάλα γράμματα. Νεανικό και θορυβώδες.', category: 'Ευέλικτο', primary: 'garage', verticals: ["beauty", "farm", "food", "garage", "gym", "retail", "rooms", "trade", "wood"], generic: true, customizable: { palette: true, fontPair: true } },
  'klassy-cafe': { label: 'Κλασικό Καφενείο', desc: 'Ζεστό και παραδοσιακό, με τον κατάλογο και τις ώρες σε πρώτο πλάνο.', category: 'Εστίαση', primary: 'cafe', verticals: ["bakery", "cafe", "food"], generic: false, customizable: { palette: false, fontPair: false } },
  living: { label: 'Καθημερινό', desc: 'Ζεστό και οικείο, με τη φωτογραφία του προϊόντος μπροστά.', category: 'Ευέλικτο', primary: 'massage', verticals: ["aesthetics", "beauty", "cafe", "dentist", "doctor", "education", "farm", "food", "garage", "gym", "logistics", "massage", "pet", "pharmacy", "professional", "realestate", "retail", "rooms", "trade", "wood"], generic: true, customizable: { palette: true, fontPair: true } },
  longform: { label: 'Longform', desc: 'Βασικό αρχέτυπο μακράς ροής. Εσωτερική υποδομή συμβατότητας.', category: 'Εσωτερικά', internal: true, customizable: { palette: true, fontPair: true } },
  magazine: { label: 'Magazine', desc: 'Βασικό αρχέτυπο περιοδικού. Εσωτερική υποδομή συμβατότητας.', category: 'Εσωτερικά', primary: 'food', verticals: ["aesthetics", "farm", "food", "massage", "pet", "retail"], generic: false, internal: true, customizable: { palette: true, fontPair: true } },
  marble: { label: 'Μάρμαρο', desc: 'Λευκό και λιτό, με μία εικόνα και πολύ αέρα γύρω της.', category: 'Ευέλικτο', primary: 'pharmacy', verticals: ["aesthetics", "dentist", "doctor", "education", "massage", "pharmacy", "professional", "realestate", "rooms"], generic: true, customizable: { palette: true, fontPair: true } },
  'medic-care': { label: 'Ιατρική Φροντίδα', desc: 'Ήρεμο και προσιτό, με υπηρεσίες και στοιχεία επικοινωνίας μπροστά.', category: 'Υγεία', primary: 'doctor', verticals: ["dentist", "doctor"], generic: false, customizable: { palette: false, fontPair: false } },
  'microbakery-lab': { label: 'Εργαστήριο', desc: 'Μονόχρωμο αυστηρό grid και αφήγηση με έμφαση στη διαδικασία.', category: 'Εστίαση', primary: 'bakery', verticals: ["bakery"], generic: false, customizable: { palette: true, fontPair: true } },
  'morning-journal': { label: 'Πρωινή Εφημερίδα', desc: 'Editorial γειτονιάς με ιστορία, προϊόν και καθαρή πληροφορία.', category: 'Εστίαση', primary: 'bakery', verticals: ["bakery"], generic: false, customizable: { palette: false, fontPair: true } },
  'moso-interior': { label: 'Εσωτερικοί Χώροι', desc: 'Για ξυλουργείο ή διακόσμηση: έργα σε μεγάλη κλίμακα.', category: 'Τεχνικά επαγγέλματα', primary: 'wood', verticals: ["trade", "wood"], generic: false, customizable: { palette: false, fontPair: false } },
  motor: { label: 'Μοτέρ', desc: 'Σκούρο γκαράζ με κόκκινο τόνο και δελτίο εργασιών.', category: 'Τεχνικά επαγγέλματα', primary: 'garage', verticals: ["garage", "gym"], generic: false, customizable: { palette: true, fontPair: true } },
  'neighborhood-market': { label: 'Αγορά Γειτονιάς', desc: 'Χρώμα και modular πλακίδια για ζωντανή τοπική ταυτότητα.', category: 'Εστίαση', primary: 'cafe', verticals: ["bakery", "cafe"], generic: false, customizable: { palette: false, fontPair: true } },
  'novena-care': { label: 'Φροντίδα', desc: 'Καθαρή ιατρική εμπειρία με υπηρεσίες, εμπιστοσύνη και ραντεβού.', category: 'Υγεία', primary: 'dentist', verticals: ["dentist", "doctor"], generic: false, customizable: { palette: false, fontPair: false } },
  poster: { label: 'Poster', desc: 'Βασικό αρχέτυπο αφίσας. Εσωτερική υποδομή συμβατότητας.', category: 'Εσωτερικά', primary: 'gym', verticals: ["food", "garage", "gym"], generic: false, internal: true, customizable: { palette: true, fontPair: true } },
  'price-first': { label: 'Τιμοκατάλογος', desc: 'Οι τιμές πρώτες — για επάγγελμα που πουλά με σαφή τιμή.', category: 'Ομορφιά', primary: 'beauty', verticals: ["beauty"], generic: false, customizable: { palette: false, fontPair: false } },
  'property-atlas': { label: 'Άτλας Ακινήτων', desc: 'Χάρτης, κατηγορίες και καρτέλες ακινήτων με στοιχεία.', category: 'Ακίνητα', primary: 'realestate', verticals: ["professional", "realestate"], generic: false, customizable: { palette: false, fontPair: false } },
  pulse: { label: 'Παλμός', desc: 'Καθαρό και αθλητικό, με τον εξοπλισμό σε πρώτο πλάνο.', category: 'Γυμναστήριο & ευεξία', primary: 'gym', verticals: ["gym"], generic: false, customizable: { palette: true, fontPair: true } },
  quiet: { label: 'Ησυχία', desc: 'Σχεδόν μόνο τυπογραφία. Ο μέγιστος δυνατός αέρας.', category: 'Ευέλικτο', primary: 'pharmacy', verticals: ["aesthetics", "beauty", "cafe", "dentist", "doctor", "education", "farm", "food", "garage", "gym", "logistics", "massage", "pet", "pharmacy", "professional", "realestate", "retail", "rooms", "trade", "wood"], generic: true, customizable: { palette: true, fontPair: true } },
  runway: { label: 'Πασαρέλα', desc: 'Ασπρόμαυρη φωτογραφία με χειρόγραφο ροζ accent.', category: 'Ομορφιά', primary: 'gym', verticals: ["aesthetics", "beauty", "gym"], generic: false, customizable: { palette: true, fontPair: true } },
  'scandinavian-coffee': { label: 'Σκανδιναβικός Καφές', desc: 'Φως, αρχιτεκτονική φωτογραφία και ήρεμη εμπειρία specialty.', category: 'Εστίαση', primary: 'cafe', verticals: ["cafe"], generic: false, customizable: { palette: true, fontPair: true } },
  showcase: { label: 'Showcase', desc: 'Βασικό αρχέτυπο βιτρίνας. Εσωτερική υποδομή συμβατότητας.', category: 'Εσωτερικά', internal: true, customizable: { palette: true, fontPair: true } },
  sidebar: { label: 'Sidebar', desc: 'Βασικό αρχέτυπο πλαϊνής στήλης. Εσωτερική υποδομή συμβατότητας.', category: 'Εσωτερικά', primary: 'trade', verticals: ["pharmacy", "trade"], generic: false, internal: true, customizable: { palette: true, fontPair: true } },
  signature: { label: 'Υπογραφή', desc: 'Προσωπικό ύφος, με serif όνομα και μία τονισμένη λέξη.', category: 'Επαγγελματικές υπηρεσίες', primary: 'dentist', verticals: ["beauty", "dentist", "doctor", "massage", "professional", "realestate"], generic: false, customizable: { palette: true, fontPair: true } },
  split: { label: 'Split', desc: 'Βασικό αρχέτυπο δύο στηλών. Εσωτερική υποδομή συμβατότητας.', category: 'Εσωτερικά', primary: 'pharmacy', verticals: ["doctor", "pet", "pharmacy", "retail"], generic: false, internal: true, customizable: { palette: true, fontPair: true } },
  terra: { label: 'Γη', desc: 'Γήινοι τόνοι και χαλαρός ρυθμός. Για ευεξία και φροντίδα.', category: 'Υγεία', primary: 'farm', verticals: ["farm", "massage"], generic: false, customizable: { palette: true, fontPair: true } },
  'thomson-stylist': { label: 'Στούντιο Styling', desc: 'Καθαρό και προσωπικό, με έργα και υπηρεσίες σε ίσα μέρη.', category: 'Ομορφιά', primary: 'beauty', verticals: ["aesthetics", "beauty", "massage"], generic: false, customizable: { palette: false, fontPair: false } },
  'type-gallery': { label: 'Τυπογραφική Γκαλερί', desc: 'Η τυπογραφία κάνει τη δουλειά· η εικόνα υποστηρίζει.', category: 'Ευέλικτο', primary: 'gym', verticals: ["aesthetics", "bakery", "beauty", "cafe", "education", "farm", "food", "garage", "gym", "logistics", "massage", "pet", "pharmacy", "professional", "retail", "rooms", "trade", "wood"], generic: true, customizable: { palette: true, fontPair: true } },
  'vertical-snap': { label: 'Κατακόρυφη Ροή', desc: 'Πλήρεις οθόνες που κουμπώνουν καθώς κυλάς.', category: 'Τουρισμός & διαμονή', primary: 'rooms', verticals: ["rooms"], generic: false, customizable: { palette: false, fontPair: false } },
  'vex-counter': { label: 'Ταχεία Εξυπηρέτηση', desc: 'Για μαγαζί με ουρά: κατάλογος, τιμές και γρήγορη παραγγελία.', category: 'Εστίαση', primary: 'cafe', verticals: ["bakery", "cafe", "food"], generic: false, customizable: { palette: false, fontPair: false } },
  'villa-agency': { label: 'Γραφείο Ακινήτων', desc: 'Κάρτες ακινήτων με τιμή και προδιαγραφές, φίλτρα κατηγορίας.', category: 'Ακίνητα', primary: 'realestate', verticals: ["realestate"], generic: false, customizable: { palette: false, fontPair: false } },
  volt: { label: 'Βολτ', desc: 'Σκούρο και τεχνολογικό, με πράσινο τόνο.', category: 'Τεχνικά επαγγέλματα', primary: 'gym', verticals: ["garage", "gym"], generic: false, customizable: { palette: true, fontPair: true } },
  warmth: { label: 'Ζεστασιά', desc: 'Ζεστή φωτογραφία φαγητού και κρεμ ενότητες.', category: 'Εστίαση', primary: 'food', verticals: ["bakery", "farm", "food", "massage"], generic: false, customizable: { palette: true, fontPair: true } },
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

/**
 * Ό,τι επιτρέπεται να δει ο πελάτης στην «Επιλογή θέματος».
 *
 * Δεν είναι κάθε renderable id: τα αρχέτυπα συμβατότητας
 * (bento, corporate, editorial, grid, longform, magazine, poster, showcase, sidebar, split)
 * είναι στόχοι του MAP για τα legacy layout names — υποδομή, όχι προϊόν.
 */
export const COMMERCIAL_THEMES = ["aegean", "airspace-office", "area-first", "bakery-editorial", "barber-shop", "beauty-atelier", "bigspring-advisory", "billys-barber", "bloom", "blue-onepage", "callout", "canvas", "chapter-snap", "cinematic", "clean-work", "clinic-triage", "coast", "constra-build", "counter-menu", "directory-index", "dispatch", "educenter-campus", "elegance-salon", "ember", "forge", "freight-lane", "frost-bakery", "grecko-table", "gymso-fitness", "heritage-bakery", "horizontal-story", "infinite", "kinetic", "klassy-cafe", "living", "marble", "medic-care", "microbakery-lab", "morning-journal", "moso-interior", "motor", "neighborhood-market", "novena-care", "price-first", "property-atlas", "pulse", "quiet", "runway", "scandinavian-coffee", "signature", "terra", "thomson-stylist", "type-gallery", "vertical-snap", "vex-counter", "villa-agency", "volt", "warmth"]

export const THEME_LIBRARY = COMMERCIAL_THEMES.map((id) => ({
  id,
  label: TEMPLATE_META[id].label,
  desc: TEMPLATE_META[id].desc,
  category: TEMPLATE_META[id].category,
  primary: TEMPLATE_META[id].primary,
  verticals: TEMPLATE_META[id].verticals || [],
  generic: !!TEMPLATE_META[id].generic,
}))

/** Η κατηγορία που ταιριάζει στο επάγγελμα του πελάτη — για προεπιλογή φίλτρου. */
export function categoryForVertical(vertical) {
  const hit = THEME_LIBRARY.find((t) => t.primary === vertical && !t.generic)
  return hit ? hit.category : ''
}

export const THEME_CATEGORIES = [...new Set(THEME_LIBRARY.map((t) => t.category))].sort()

export function themesByCategory(category) {
  return category ? THEME_LIBRARY.filter((t) => t.category === category) : THEME_LIBRARY
}
