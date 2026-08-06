import { getSiteData } from '../../../lib/api'
import { pickTemplate } from '../../../lib/templates'
import { buildMetadata, buildJsonLd } from '../../../lib/seo'
import CallBar from '../../../lib/templates/CallBar'
import { withMediaFallback } from '../../../lib/mediaFallback'
import MediaDisclosure from '../../../lib/templates/MediaDisclosure'

export const dynamic = 'force-dynamic' // multi-tenant: render per request (ISR via fetch revalidate)

export async function generateMetadata({ params, searchParams }) {
  try {
    const { data } = await getSiteData(params.client, searchParams?.layout)
    const domain = String(params.client).includes('.') ? params.client : undefined
    return buildMetadata(withMediaFallback(data), { domain })
  } catch {
    return { title: 'Vitrina' }
  }
}

export default async function SitePage({ params, searchParams }) {
  let payload
  try {
    // ?v= → cache-bust από το /choose μετά από upload φωτο (live traffic μένει cached)
    payload = await getSiteData(params.client, searchParams?.layout, Boolean(searchParams?.v))
  } catch (e) {
    return (
      <div style={{ minHeight: '60vh', display: 'grid', placeItems: 'center', fontFamily: 'Inter, sans-serif', color: '#555' }}>
        <p>Το site δεν είναι διαθέσιμο αυτή τη στιγμή.</p>
      </div>
    )
  }
  const Template = pickTemplate(payload.layout)
  const siteData = withMediaFallback(payload.data)
  const domain = String(params.client).includes('.') ? params.client : undefined
  const jsonLd = buildJsonLd(siteData, { domain })
  return (
    <>
      {/* Local-SEO structured data (Google rich results + local ranking) */}
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />
      <Template data={siteData} />
      <MediaDisclosure data={siteData} />
      <CallBar data={siteData} />
    </>
  )
}
