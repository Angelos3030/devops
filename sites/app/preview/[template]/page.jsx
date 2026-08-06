import { TEMPLATES } from '../../../lib/templates'
import { demoBusinesses, demoData } from '../../../lib/demoData'
import CallBar from '../../../lib/templates/CallBar'
import { withMediaFallback } from '../../../lib/mediaFallback'
import MediaDisclosure from '../../../lib/templates/MediaDisclosure'

// Full-screen render of one template with a chosen demo business (for showcase/ads).
export default function PreviewTemplate({ params, searchParams }) {
  const Tpl = TEMPLATES[params.template] || TEMPLATES.editorial
  const selected = demoBusinesses[searchParams?.biz] || demoData
  const input = searchParams?.photos === 'none'
    ? { ...selected, HERO_IMAGE: '', STORY_IMAGE: '', gallery: [] }
    : selected
  const data = withMediaFallback(input)
  // Ίδια μπάρα κλήσης με τα ζωντανά site, ώστε το preview να δείχνει την αλήθεια.
  return (
    <>
      <Tpl data={data} />
      <MediaDisclosure data={data} />
      <CallBar data={data} />
    </>
  )
}
