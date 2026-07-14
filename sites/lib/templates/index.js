import Editorial from './Editorial'
import Split from './Split'
import Showcase from './Showcase'

// The 3 structurally-distinct React archetypes.
export const TEMPLATES = { editorial: Editorial, split: Split, showcase: Showcase }
export const TEMPLATE_KEYS = ['editorial', 'split', 'showcase']
export const TEMPLATE_META = {
  editorial: { label: 'Editorial', desc: 'Κλασικό stacked, μεγάλη τυπογραφία.' },
  split: { label: 'Split', desc: 'Σταθερό πλαϊνό panel + περιεχόμενο που κυλάει.' },
  showcase: { label: 'Showcase', desc: 'Full-screen, με έμφαση στις φωτογραφίες.' },
}

// Map backend layout names → React archetype (until backend adopts react keys).
const MAP = {
  studio: 'editorial', trust: 'editorial', commerce: 'editorial', warmth: 'editorial',
  atelier: 'split', noir: 'split',
  fresh: 'showcase', bold: 'showcase', coast: 'showcase',
  editorial: 'editorial', split: 'split', showcase: 'showcase',
}
export function pickTemplate(layout) {
  return TEMPLATES[MAP[layout] || layout] || Editorial
}
