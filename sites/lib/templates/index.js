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

// Structurally-distinct React archetypes.
export const TEMPLATES = { editorial: Editorial, split: Split, showcase: Showcase, bento: Bento, longform: Longform, corporate: Corporate, poster: Poster, sidebar: Sidebar, grid: GridT, coast: Coast }
export const TEMPLATE_KEYS = ['editorial', 'split', 'showcase', 'bento', 'longform', 'corporate', 'poster', 'sidebar', 'grid', 'coast']
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
}

// Map backend layout names → React archetype (until backend adopts react keys).
const MAP = {
  studio: 'editorial', trust: 'editorial', commerce: 'editorial', warmth: 'editorial',
  atelier: 'split', noir: 'split',
  fresh: 'showcase', bold: 'showcase', coast: 'showcase',
  professional: 'corporate', trade: 'corporate',
  editorial: 'editorial', split: 'split', showcase: 'showcase', bento: 'bento', longform: 'longform', corporate: 'corporate',
  poster: 'poster', sidebar: 'sidebar', grid: 'grid', coast: 'coast',
}
export function pickTemplate(layout) {
  return TEMPLATES[MAP[layout] || layout] || Editorial
}
