import { TEMPLATES } from '../../../lib/templates'
import { demoBusinesses, demoData } from '../../../lib/demoData'
import CallBar from '../../../lib/templates/CallBar'

// Full-screen render of one template with a chosen demo business (for showcase/ads).
export default function PreviewTemplate({ params, searchParams }) {
  const Tpl = TEMPLATES[params.template] || TEMPLATES.editorial
  const data = demoBusinesses[searchParams?.biz] || demoData
  // Ίδια μπάρα κλήσης με τα ζωντανά site, ώστε το preview να δείχνει την αλήθεια.
  return (
    <>
      <Tpl data={data} />
      <CallBar data={data} />
    </>
  )
}
