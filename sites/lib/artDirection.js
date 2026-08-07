// Gives each visual route a different edit of the same client material.
// The customer's assets stay truthful; only prominence and sequence change.
const DIRECTIONS = {
  canvas: { hero: 0, story: 4, rotate: 0 },
  runway: { hero: 2, story: 0, rotate: 2 },
  grid: { hero: 1, story: 3, rotate: 1 },
  forge: { hero: 3, story: 1, rotate: 3 },
  dispatch: { hero: 4, story: 2, rotate: 4 },
  cinematic: { hero: 1, story: 4, rotate: 1 },
  'type-gallery': { hero: 2, story: 1, rotate: 3 },
  quiet: { hero: 0, story: 3, rotate: 4 },
  kinetic: { hero: 3, story: 2, rotate: 2 },
  infinite: { hero: 4, story: 0, rotate: 1 },
  living: { hero: 2, story: 4, rotate: 4 },
  'bakery-editorial': { hero: 0, story: 4, rotate: 0 },
  'counter-menu': { hero: 2, story: 0, rotate: 2 },
  'morning-journal': { hero: 1, story: 3, rotate: 1 },
  'neighborhood-market': { hero: 3, story: 2, rotate: 3 },
  'microbakery-lab': { hero: 0, story: 1, rotate: 4 },
}

const at = (items, index) => items.length ? items[index % items.length] : null

export function artDirect(data = {}, template = '') {
  const direction = DIRECTIONS[template]
  const gallery = Array.isArray(data.gallery) ? data.gallery.filter((item) => item?.image) : []
  if (!direction || gallery.length < 2) return data

  const ordered = gallery.map((_, index) => at(gallery, index + direction.rotate))
  const hero = at(gallery, direction.hero)
  const story = at(gallery, direction.story)

  return {
    ...data,
    HERO_IMAGE: hero?.image || data.HERO_IMAGE,
    STORY_IMAGE: story?.image || data.STORY_IMAGE,
    gallery: ordered,
    ART_DIRECTION: template,
  }
}
