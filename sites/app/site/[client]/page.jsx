import { getSiteData } from '../../../lib/api'
import { pickTemplate } from '../../../lib/templates'
import { buildMetadata, buildJsonLd } from '../../../lib/seo'
import CallBar from '../../../lib/templates/CallBar'
import { withMediaFallback } from '../../../lib/mediaFallback'
import MediaDisclosure from '../../../lib/templates/MediaDisclosure'
import { artDirect } from '../../../lib/artDirection'

export const dynamic = 'force-dynamic' // multi-tenant: render per request (ISR via fetch revalidate)

const DRAFT_FIELDS = new Set([
  'name', 'trade', 'city', 'phone', 'hours', 'areas', 'tagline', 'intro',
  'story_title', 'story_paragraphs', 'cta_title', 'services', 'template',
  'address', 'gbp_url',
])

function readDraft(raw) {
  if (!raw || typeof raw !== 'string' || raw.length > 12000) return {}
  try {
    const parsed = JSON.parse(raw)
    return Object.fromEntries(Object.entries(parsed).filter(([key]) => DRAFT_FIELDS.has(key)))
  } catch {
    return {}
  }
}

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
  const draft = readDraft(searchParams?.draft)
  const templateKey = draft.template || payload.layout
  const siteData = artDirect(withMediaFallback({ ...payload.data, ...draft }), templateKey)
  const Template = pickTemplate(templateKey)
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
