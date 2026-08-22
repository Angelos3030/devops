import { demoBusinesses } from '../../../../lib/demoData'
import { withMediaFallback } from '../../../../lib/mediaFallback'
import MasterCinematic from '../../../../lib/templates/MasterCinematic'
import MasterEditorial from '../../../../lib/templates/MasterEditorial'
import MasterSpatial from '../../../../lib/templates/MasterSpatial'

const THEMES = {
  cinematic: MasterCinematic,
  editorial: MasterEditorial,
  spatial: MasterSpatial,
}

export default function MasterThemeProof({ params, searchParams }) {
  const Theme = THEMES[params.theme] || MasterCinematic
  // Το route έδινε ΠΑΝΤΑ δεδομένα rooms, οπότε τα τρία Master themes δεν είχαν
  // ελεγχθεί ποτέ με το vertical τους (CLAUDE.md §7β). Δέχεται πλέον ?biz=.
  const base = demoBusinesses[searchParams?.biz] || demoBusinesses.rooms
  const input = searchParams?.photos === 'none'
    ? { ...base, HERO_IMAGE: '', STORY_IMAGE: '', gallery: [], MEDIA_POLICY: 'real-only' }
    : base
  const data = withMediaFallback(input)
  return <Theme data={data} />
}
