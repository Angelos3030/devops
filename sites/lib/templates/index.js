import Editorial from './Editorial'
import Split from './Split'
import Showcase from './Showcase'
import Bento from './Bento'
import Longform from './Longform'

// Structurally-distinct React archetypes.
export const TEMPLATES = { editorial: Editorial, split: Split, showcase: Showcase, bento: Bento, longform: Longform }
export const TEMPLATE_KEYS = ['editorial', 'split', 'showcase', 'bento', 'longform']
export const TEMPLATE_META = {
  editorial: { label: 'Editorial', desc: 'Κλασικό stacked, μεγάλη τυπογραφία.' },
  split: { label: 'Split', desc: 'Σταθερό πλαϊνό panel + περιεχόμενο που κυλάει.' },
  showcase: { label: 'Showcase', desc: 'Full-screen, με έμφαση στις φωτογραφίες.' },
  bento: { label: 'Bento', desc: 'Πλέγμα από tiles διαφορετικού μεγέθους.' },
  longform: { label: 'Longform', desc: 'Στενή στήλη, magazine reading, drop-cap.' },
}

// Map backend layout names → React archetype (until backend adopts react keys).
const MAP = {
  studio: 'editorial', trust: 'editorial', commerce: 'editorial', warmth: 'editorial',
  atelier: 'split', noir: 'split',
  fresh: 'showcase', bold: 'showcase', coast: 'showcase',
  editorial: 'editorial', split: 'split', showcase: 'showcase', bento: 'bento', longform: 'longform',
}
export function pickTemplate(layout) {
  return TEMPLATES[MAP[layout] || layout] || Editorial
}
