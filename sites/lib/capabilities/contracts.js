const text = (value, fallback = '') => String(value ?? fallback).trim()
const number = (value) => Number.isFinite(Number(value)) ? Number(value) : null

export function normaliseServices(data = {}) {
  return (data.pricingServices || data.treatments || data.services || []).map((item, index) => ({
    id: text(item.id, `service-${index + 1}`),
    category: text(item.category, 'Υπηρεσίες'),
    name: text(item.name || item.title, `Υπηρεσία ${index + 1}`),
    shortDescription: text(item.shortDescription || item.desc),
    longDescription: text(item.longDescription || item.desc),
    priceType: text(item.priceType, item.price || item.priceFrom ? 'from' : 'quote'),
    price: number(item.price), priceFrom: number(item.priceFrom),
    duration: text(item.duration), featured: Boolean(item.featured),
    bookingEnabled: item.bookingEnabled !== false,
    availabilityStatus: text(item.availabilityStatus || item.availability, 'available'),
    bookingUrl: text(item.bookingUrl), image: text(item.image),
    preparationNotes: text(item.preparationNotes), recoveryNotes: text(item.recoveryNotes),
    practitionerIds: Array.isArray(item.practitionerIds) ? item.practitionerIds : [],
  }))
}

export function normaliseInventory(data = {}) {
  const source = data.inventoryOptions || data.gallery || []
  return source.map((item, index) => ({
    id: text(item.id, `option-${index + 1}`), label: text(item.label || item.title, `Επιλογή ${index + 1}`),
    image: text(item.image), category: text(item.category || item.sub, 'Συλλογή'),
    variant: text(item.variant), price: number(item.price),
    inventoryStatus: text(item.inventoryStatus, index === 1 ? 'low-stock' : 'available'),
    quantityAvailable: number(item.quantityAvailable), selectable: item.selectable !== false,
    leadTime: text(item.leadTime), metadata: item.metadata || {},
  }))
}

export function priceLabel(service) {
  if (service.priceType === 'free') return 'Δωρεάν'
  if (service.priceType === 'quote') return 'Κατόπιν εκτίμησης'
  const amount = service.price ?? service.priceFrom
  if (amount == null) return 'Ρωτήστε μας'
  const prefix = service.priceType === 'from' ? 'από ' : ''
  const suffix = service.priceType === 'hourly' ? '/ώρα' : ''
  return `${prefix}${amount.toLocaleString('el-GR')}€${suffix}`
}

export function capabilityData(data = {}) {
  return {
    services: normaliseServices(data), inventory: normaliseInventory(data),
    serviceArea: {
      postcodes: data.serviceArea?.postcodes || ['10', '11', '12', '15', '17'],
      limitedPostcodes: data.serviceArea?.limitedPostcodes || ['19'],
      nextAvailable: data.serviceArea?.nextAvailable || 'Αύριο, 09:00–12:00',
      specialCoverageMessage: data.serviceArea?.specialCoverageMessage || 'Επικοινώνησε μαζί μας για ειδική κάλυψη.',
    },
    booking: { provider: data.booking?.provider || 'demo', url: data.booking?.url || '' },
  }
}
