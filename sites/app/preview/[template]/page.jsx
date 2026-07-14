import { TEMPLATES } from '../../../lib/templates'
import { demoBusinesses, demoData } from '../../../lib/demoData'

// Full-screen render of one template with a chosen demo business (for showcase/ads).
export default function PreviewTemplate({ params, searchParams }) {
  const Tpl = TEMPLATES[params.template] || TEMPLATES.editorial
  const data = demoBusinesses[searchParams?.biz] || demoData
  return <Tpl data={data} />
}
