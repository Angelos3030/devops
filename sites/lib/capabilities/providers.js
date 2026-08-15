// Deterministic demo adapters. Replace these functions with API-backed providers;
// UI components consume only their returned contract, never transport details.
export function checkServiceArea(config, request) {
  const postcode = String(request.postcode || '').replace(/\s/g, '')
  if (!postcode) return { status: 'idle', message: 'Γράψε τον ταχυδρομικό κώδικα.' }
  if ((config.limitedPostcodes || []).some((p) => postcode.startsWith(p))) {
    return { status: 'limited', message: 'Περιορισμένη διαθεσιμότητα', nextAvailable: config.nextAvailable }
  }
  if ((config.postcodes || []).some((p) => postcode.startsWith(p))) {
    return { status: 'available', message: 'Εξυπηρετούμε την περιοχή σου', nextAvailable: config.nextAvailable }
  }
  return { status: 'outside', message: 'Εκτός της βασικής ζώνης', detail: config.specialCoverageMessage }
}

export function createBookingAction(config, service) {
  if (!service?.bookingEnabled) return { kind: 'disabled', label: 'Μη διαθέσιμο online' }
  if (service.bookingUrl || config.url) return { kind: 'link', label: 'Κλείσε ραντεβού', href: service.bookingUrl || config.url }
  return { kind: 'enquiry', label: `Ενδιαφέρομαι για: ${service.name}`, payload: { serviceId: service.id } }
}

export function inventoryAvailability(option) {
  const labels = { available: 'Διαθέσιμο', 'low-stock': 'Λίγα διαθέσιμα', unavailable: 'Μη διαθέσιμο', 'made-to-order': 'Κατόπιν παραγγελίας', 'on-request': 'Διαθεσιμότητα κατόπιν αιτήματος' }
  return { selectable: option.selectable && option.inventoryStatus !== 'unavailable', label: labels[option.inventoryStatus] || labels.available }
}
