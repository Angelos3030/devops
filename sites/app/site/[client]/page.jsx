import { getSiteData } from '../../../lib/api'
import { pickTemplate } from '../../../lib/templates'

export const dynamic = 'force-dynamic' // multi-tenant: render per request (ISR via fetch revalidate)

export async function generateMetadata({ params, searchParams }) {
  try {
    const { data } = await getSiteData(params.client, searchParams?.layout)
    const title = `${data.NAME} — ${data.TRADE} | ${data.CITY}`
    return { title, description: `${data.TAGLINE} Τηλ. ${data.PHONE}.` }
  } catch {
    return { title: 'Vitrina' }
  }
}

export default async function SitePage({ params, searchParams }) {
  let payload
  try {
    payload = await getSiteData(params.client, searchParams?.layout)
  } catch (e) {
    return (
      <div style={{ minHeight: '60vh', display: 'grid', placeItems: 'center', fontFamily: 'Inter, sans-serif', color: '#555' }}>
        <p>Το site δεν είναι διαθέσιμο αυτή τη στιγμή.</p>
      </div>
    )
  }
  const Template = pickTemplate(payload.layout)
  return <Template data={payload.data} />
}
