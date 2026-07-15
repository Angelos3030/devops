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

export function buildJsonLd(data) {
  const areas = (data.AREAS || '').split('·').map((a) => a.trim()).filter(Boolean)
  return {
    '@context': 'https://schema.org',
    '@type': schemaType(data),
    name: data.NAME,
    description: data.TAGLINE,
    telephone: data.PHONE_INTL ? `+${data.PHONE_INTL}` : undefined,
    image: data.HERO_IMAGE || undefined,
    address: { '@type': 'PostalAddress', addressLocality: data.CITY, addressCountry: 'GR' },
    areaServed: areas.length ? areas : (data.CITY ? [data.CITY] : undefined),
    openingHours: data.HOURS || undefined,
    priceRange: '€€',
  }
}

export function buildMetadata(data) {
  const title = `${data.NAME} — ${data.TRADE} | ${data.CITY}`
  const description = `${data.TAGLINE} Τηλ. ${data.PHONE}.`
  const keywords = [data.TRADE, `${data.TRADE} ${data.CITY}`, data.NAME, data.CITY]
    .filter(Boolean)
  return {
    title,
    description,
    keywords,
    openGraph: {
      title,
      description,
      type: 'website',
      locale: 'el_GR',
      images: data.HERO_IMAGE ? [{ url: data.HERO_IMAGE }] : undefined,
    },
  }
}
