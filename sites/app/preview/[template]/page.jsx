import { TEMPLATES, themeControls } from '../../../lib/templates'
import { demoBusinesses, demoData } from '../../../lib/demoData'
import CallBar from '../../../lib/templates/CallBar'
import { withMediaFallback } from '../../../lib/mediaFallback'
import MediaDisclosure from '../../../lib/templates/MediaDisclosure'
import { artDirect } from '../../../lib/artDirection'
import theme from '../../site/[client]/theme.module.css'

// Full-screen render of one template with a chosen demo business (for showcase/ads).
export default function PreviewTemplate({ params, searchParams }) {
  const Tpl = TEMPLATES[params.template] || TEMPLATES.editorial
  const selected = demoBusinesses[searchParams?.biz] || demoData
  // ?logo=<url> — έλεγχος του brand slot και στις τρεις καταστάσεις
  // (ανεβασμένο / παραγόμενο / χωρίς). Ίδιο μοτίβο με το ?photos=none.
  let input = searchParams?.photos === 'none'
    ? { ...selected, HERO_IMAGE: '', STORY_IMAGE: '', gallery: [], MEDIA_POLICY: 'real-only' }
    : selected
  if (searchParams?.logo) input = { ...input, LOGO: searchParams.logo }
  const controls = themeControls(params.template)
  const data = artDirect(withMediaFallback(input), params.template)
  // Ίδιο scope με το ζωντανό site: χωρίς αυτό το preview δεν μπορούσε να δείξει
  // παλέτα, άρα ούτε να επαληθευτεί ότι ένα theme ακολουθεί το συμβόλαιο.
  return (
    <>
      <div className={theme.scope}
        data-palette={controls.palette ? (searchParams?.palette || 'original') : undefined}
        data-font={controls.fontPair ? (searchParams?.font || 'editorial') : undefined}>
        <Tpl data={data} />
      </div>
      <MediaDisclosure data={data} />
      <CallBar data={data} />
    </>
  )
}
