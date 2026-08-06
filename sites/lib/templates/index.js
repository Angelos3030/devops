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

// Structurally-distinct React archetypes.
export const TEMPLATES = { editorial: Editorial, split: Split, showcase: Showcase, bento: Bento, longform: Longform, corporate: Corporate, poster: Poster, sidebar: Sidebar, grid: GridT, coast: Coast, magazine: Magazine, warmth: Warmth, ember: Ember, marble: Marble, runway: Runway, forge: Forge, aegean: Aegean, bloom: Bloom, pulse: Pulse, volt: Volt, motor: Motor, terra: Terra, dispatch: Dispatch, canvas: Canvas }
// The public collection stays intentionally curated. Legacy templates remain
// renderable for existing clients but are not offered to new customers.
export const TEMPLATE_KEYS = ['editorial', 'split', 'bento', 'longform', 'poster', 'sidebar', 'grid', 'magazine', 'warmth', 'ember', 'marble', 'runway', 'forge', 'aegean', 'bloom', 'volt', 'motor', 'terra', 'dispatch', 'canvas']
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
  grid: { label: 'Grid', desc: 'Swiss/structured με hairlines & monospace.' },
  coast: { label: 'Coast', desc: 'Μεσογειακό, φωτεινό, zigzag rows — τουρισμός.' },
  magazine: { label: 'Magazine', desc: 'Εφημερίδα/multi-column, masthead, στήλες.' },
  warmth: { label: 'Warmth', desc: 'Ζεστό hospitality, menu-style — ταβέρνες/φούρνοι.' },
  ember: { label: 'Ember', desc: 'Νυχτερινή ψησταριά — καπνιστό, λάμψη κάρβουνου, κατάλογος. Premium food/night.' },
  marble: { label: 'Marble', desc: 'Minimal-luxe — πορσελάνη, χρυσές hairlines, ευρετήριο τομέων. Δικηγόροι/ιατροί.' },
  runway: { label: 'Runway', desc: 'High-fashion — B&W που «ανάβει», πασαρέλα έργων. Κομμωτήρια/beauty.' },
  forge: { label: 'Forge', desc: 'Βιομηχανικό φως ημέρας — ατσάλι, safety yellow, trust band. Τεχνίτες.' },
  aegean: { label: 'Aegean', desc: 'Κυκλαδίτικο — full-bleed θάλασσα, καρτ-ποστάλ gallery. Τουρισμός/δωμάτια.' },
  bloom: { label: 'Bloom', desc: 'Πρωινό φως — καμάρες βιτρίνας, βοτανικό πράσινο. Καφέ/φούρνοι.' },
  pulse: { label: 'Pulse', desc: 'Κλινική ηρεμία — λευκό/teal, γραμμή παλμού. Ιατρεία/κλινικές.' },
  volt: { label: 'Volt', desc: 'Ενέργεια — ανθρακί + electric lime, διαγώνιες τομές. Γυμναστήρια.' },
  motor: { label: 'Motor', desc: 'Γκαράζ — gunmetal, signal red, δελτίο εργασιών. Συνεργεία.' },
  canvas: { label: 'Canvas', desc: 'Κατάλογος εργαστηρίου — κάθε υπηρεσία είναι έργο με δική της φωτογραφία. Ξυλουργοί/ανακαινίσεις.' },
  dispatch: { label: 'Dispatch', desc: 'Μία οθόνη, μηδέν σκρολ — φωτογραφία σε όλη την οθόνη, τηλέφωνο-ήρωας. Τεχνίτες/έκτακτες κλήσεις.' },
  terra: { label: 'Terra', desc: 'Γη & kraft — ετικέτες προϊόντων, ελιά. Παραγωγοί/αγροτικά.' },
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
