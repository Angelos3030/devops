import assert from 'node:assert/strict'
import { capabilityData, normaliseInventory, normaliseServices, priceLabel } from '../lib/capabilities/contracts.js'
import { checkServiceArea, createBookingAction, inventoryAvailability } from '../lib/capabilities/providers.js'

const services = normaliseServices({ services: [{ title: 'Έλεγχος', desc: 'Διάγνωση', priceType: 'from', priceFrom: 35, duration: '45 λεπτά' }] })
assert.equal(services[0].name, 'Έλεγχος')
assert.equal(priceLabel(services[0]), 'από 35€')
assert.equal(priceLabel({ priceType: 'quote' }), 'Κατόπιν εκτίμησης')
assert.equal(priceLabel({ priceType: 'free' }), 'Δωρεάν')

const area = { postcodes: ['15'], limitedPostcodes: ['19'], nextAvailable: 'Αύριο', specialCoverageMessage: 'Κάλεσέ μας' }
assert.equal(checkServiceArea(area, { postcode: '153 44' }).status, 'available')
assert.equal(checkServiceArea(area, { postcode: '190 01' }).status, 'limited')
assert.equal(checkServiceArea(area, { postcode: '210 00' }).status, 'outside')

const inventory = normaliseInventory({ inventoryOptions: [{ id: 'a', label: 'Δρυς', inventoryStatus: 'unavailable' }] })
assert.equal(inventoryAvailability(inventory[0]).selectable, false)
assert.equal(createBookingAction({}, services[0]).kind, 'enquiry')
assert.equal(capabilityData({ services: [{ title: 'Α' }] }).services.length, 1)

console.log('capabilitySystems: contracts + demo providers passed')
