// Local-SEO helpers: schema.org type + JSON-LD + metadata for each client site.

const norm = (s) => (s || '').toLowerCase()

export function schemaType(data) {
  const t = norm(`${data.TRADE} ${data.KICKER}`)
  if (/(εστιατ|ταβερν|restaurant|μεζε|φαγητ)/.test(t)) return 'Restaurant'
  if (/(καφε|cafe|coffee|μπαρ|bar)/.test(t)) return 'CafeOrCoffeeShop'
  if (/(οδοντ|dentist)/.test(t)) return 'Dentist'
  if (/(ιατρ|γιατρ|doctor|κλινικ|physio|φυσικοθερ)/.test(t)) return 'MedicalBusiness'
  if (/(κομμωτ|hair|salon|κουρε)/.test(t)) return 'HairSalon'
  if (/(beauty|αισθητικ|νυχ|spa|μακιγι)/.test(t)) return 'BeautySalon'
  if (/(δικηγ|lawyer|legal|νομικ)/.test(t)) return 'LegalService'
  if (/(λογιστ|accountant|φοροτεχ)/.test(t)) return 'AccountingService'
  if (/(ξυλουργ|μαραγκ|wood|επιπλ|κουζιν|μαστορ|τεχνικ|υδραυλ|ηλεκτρολ|construct)/.test(t)) return 'HomeAndConstructionBusiness'
  return 'LocalBusiness'
}

// Ελληνικές ώρες («Δευτ.–Σάβ. 08:00–19:00», «Καθημερινά 12:00–00:00») →
// openingHoursSpecification, που είναι ό,τι διαβάζει η Google (το σκέτο κείμενο όχι).
const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
const DAY_EL = [
  [/^(δευτ|δε)/i, 0], [/^(τρι|τρ)/i, 1], [/^(τετ|τε)/i, 2], [/^(πεμ|πε)/i, 3],
  [/^(παρ|πα)/i, 4], [/^(σαβ|σα)/i, 5], [/^(κυρ|κυ)/i, 6],
]
// Χωρίς αυτό, «Σάβ.» δεν ταίριαζε με «σαβ» και το ωράριο έβγαινε κενό.
const noTones = (t) => t.normalize('NFD').replace(/[̀-ͯ]/g, '')
const dayIndex = (token) => {
  const t = noTones(token.trim().replace(/\./g, ''))
  for (const [re, i] of DAY_EL) if (re.test(t)) return i
  return -1
}

export function openingHoursSpec(hours) {
  if (!hours) return undefined
  const text = String(hours)
  // «24/7», «όλο το 24ωρο» → ανοιχτά συνεχώς
  if (/24\s*\/\s*7|24ωρ/i.test(noTones(text))) {
    return [{ '@type': 'OpeningHoursSpecification', dayOfWeek: DAYS, opens: '00:00', closes: '23:59' }]
  }
  const time = text.match(/(\d{1,2}[:.]\d{2})\s*[–\-—]\s*(\d{1,2}[:.]\d{2})/)
  if (!time) return undefined
  const opens = time[1].replace('.', ':')
  const closes = time[2].replace('.', ':')

  let days = null
  if (/καθημεριν|καθε μερα|7 ημ/i.test(noTones(text))) {
    days = DAYS
  } else {
    const range = text.match(/([Α-Ωα-ωίϊΐόάέύϋΰήώ]{2,5}\.?)\s*[–\-—]\s*([Α-Ωα-ωίϊΐόάέύϋΰήώ]{2,5}\.?)/)
    if (range) {
      const a = dayIndex(range[1]), b = dayIndex(range[2])
      if (a >= 0 && b >= 0) {
        days = []
        for (let i = a; ; i = (i + 1) % 7) { days.push(DAYS[i]); if (i === b) break }
      }
    }
  }
  if (!days?.length) return undefined
  return [{ '@type': 'OpeningHoursSpecification', dayOfWeek: days, opens, closes }]
}

export function buildJsonLd(data, opts = {}) {
  const { domain } = opts
  const url = domain ? `https://${domain}` : undefined
  const areas = (data.AREAS || '').split('·').map((a) => a.trim()).filter(Boolean)
  const lat = parseFloat(data.GEO_LAT), lng = parseFloat(data.GEO_LNG)
  const hasGeo = Number.isFinite(lat) && Number.isFinite(lng)
  return {
    '@context': 'https://schema.org',
    '@type': schemaType(data),
    '@id': url ? `${url}#business` : undefined,
    url,
    name: data.NAME,
    description: data.TAGLINE,
    telephone: data.PHONE_INTL ? `+${data.PHONE_INTL}` : undefined,
    image: data.HERO_IMAGE || undefined,
    address: {
      '@type': 'PostalAddress',
      streetAddress: data.ADDRESS || undefined,
      addressLocality: data.CITY,
      addressCountry: 'GR',
    },
    geo: hasGeo ? { '@type': 'GeoCoordinates', latitude: lat, longitude: lng } : undefined,
    hasMap: hasGeo ? `https://www.google.com/maps/search/?api=1&query=${lat},${lng}` : undefined,
    sameAs: data.GBP_URL ? [data.GBP_URL] : undefined,
    areaServed: areas.length ? areas : (data.CITY ? [data.CITY] : undefined),
    openingHoursSpecification: openingHoursSpec(data.HOURS),
    openingHours: data.HOURS || undefined,   // ανθρώπινο fallback
    priceRange: '€€',
  }
}

export function buildMetadata(data, opts = {}) {
  const { domain } = opts
  const url = domain ? `https://${domain}` : undefined
  const title = `${data.NAME} — ${data.TRADE} | ${data.CITY}`
  const description = `${data.TAGLINE} Τηλ. ${data.PHONE}.`
  const keywords = [data.TRADE, `${data.TRADE} ${data.CITY}`, data.NAME, data.CITY]
    .filter(Boolean)
  const images = data.HERO_IMAGE ? [{ url: data.HERO_IMAGE }] : undefined
  const meta = {
    title,
    description,
    keywords,
    robots: { index: true, follow: true },
    openGraph: {
      title,
      description,
      type: 'website',
      locale: 'el_GR',
      url,
      siteName: data.NAME,
      images,
    },
    twitter: {
      card: data.HERO_IMAGE ? 'summary_large_image' : 'summary',
      title,
      description,
      images: data.HERO_IMAGE ? [data.HERO_IMAGE] : undefined,
    },
  }
  if (url) {
    // canonical στο δικό του domain → κόβει duplicate content apex/www
    meta.metadataBase = new URL(url)
    meta.alternates = { canonical: url }
  }
  return meta
}
