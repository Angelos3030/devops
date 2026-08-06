const DESIGN_SYSTEM_IDS = Object.freeze([
  'editorial', 'split', 'bento', 'longform', 'poster', 'sidebar', 'grid',
  'magazine', 'warmth', 'ember', 'marble', 'runway', 'forge', 'aegean',
  'bloom', 'volt', 'motor', 'terra', 'dispatch', 'canvas',
  'cinematic', 'type-gallery', 'quiet', 'kinetic', 'infinite', 'living',
])

const REQUIRED_BASE_SECTIONS = Object.freeze(['hero', 'services', 'contact', 'find-us'])

const profile = ({
  id,
  label,
  aliases,
  conversionGoal,
  requiredSections = REQUIRED_BASE_SECTIONS,
  motionIntensity,
  schemaType,
  media,
  compatibleDesignSystemIds,
}) => Object.freeze({
  id,
  label,
  aliases: Object.freeze(aliases),
  conversionGoal: Object.freeze(conversionGoal),
  requiredSections: Object.freeze([...requiredSections]),
  motionIntensity,
  schemaType,
  media: Object.freeze({
    supportsNoPhoto: true,
    minimumPreferredImages: 0,
    maximumGalleryImages: 8,
    requiredSubjects: Object.freeze([]),
    avoid: Object.freeze([]),
    fallbackStrategy: 'typography-and-service-led',
    ...media,
  }),
  compatibleDesignSystemIds: Object.freeze(compatibleDesignSystemIds),
})

export const VERTICAL_PROFILES = Object.freeze({
  carpenter: profile({
    id: 'carpenter', label: 'Ξυλουργός',
    aliases: ['carpenter', 'woodworker', 'ξυλουργός', 'ξυλουργείο', 'ξυλουργικό εργαστήριο', 'κουζίνες', 'ντουλάπες'],
    conversionGoal: { primary: 'request-quote', secondary: 'phone-call' },
    requiredSections: ['hero', 'services', 'work', 'process', 'service-areas', 'contact', 'find-us'],
    motionIntensity: 'moderate', schemaType: 'HomeAndConstructionBusiness',
    media: {
      minimumPreferredImages: 4,
      requiredSubjects: Object.freeze(['finished-work', 'material-detail']),
      avoid: Object.freeze(['unattributed-project-claims', 'unsafe-workshop-scenes']),
      fallbackStrategy: 'material-textures-and-typographic-project-cards',
    },
    compatibleDesignSystemIds: ['canvas', 'runway', 'grid', 'cinematic', 'type-gallery', 'quiet', 'kinetic', 'infinite', 'living'],
  }),
  taverna: profile({
    id: 'taverna', label: 'Ταβέρνα / Εστιατόριο',
    aliases: ['taverna', 'restaurant', 'ταβέρνα', 'εστιατόριο', 'μεζεδοπωλείο', 'ψητοπωλείο'],
    conversionGoal: { primary: 'reservation-call', secondary: 'directions' },
    requiredSections: ['hero', 'menu-highlights', 'services', 'atmosphere', 'hours', 'contact', 'find-us'],
    motionIntensity: 'moderate', schemaType: 'Restaurant',
    media: {
      minimumPreferredImages: 5,
      requiredSubjects: Object.freeze(['signature-dishes', 'dining-space']),
      avoid: Object.freeze(['generic-food-unrelated-to-menu', 'misleading-dish-claims']),
      fallbackStrategy: 'menu-led-layout-with-ingredient-illustrations',
    },
    compatibleDesignSystemIds: ['warmth', 'ember', 'magazine', 'cinematic', 'type-gallery', 'living', 'infinite', 'quiet', 'kinetic'],
  }),
  salon: profile({
    id: 'salon', label: 'Κομμωτήριο',
    aliases: ['salon', 'hair salon', 'κομμωτήριο', 'κομμωτής', 'hair studio'],
    conversionGoal: { primary: 'book-appointment', secondary: 'phone-call' },
    requiredSections: ['hero', 'services', 'pricing-or-consultation', 'work', 'hours', 'contact', 'find-us'],
    motionIntensity: 'expressive', schemaType: 'HairSalon',
    media: {
      minimumPreferredImages: 4,
      requiredSubjects: Object.freeze(['salon-space', 'style-detail']),
      avoid: Object.freeze(['unlicensed-before-after', 'misleading-client-results']),
      fallbackStrategy: 'editorial-color-and-typography-with-service-lookbook',
    },
    compatibleDesignSystemIds: ['runway', 'type-gallery', 'living', 'cinematic', 'infinite', 'kinetic', 'quiet', 'bloom', 'canvas'],
  }),
  dentist: profile({
    id: 'dentist', label: 'Οδοντιατρείο',
    aliases: ['dentist', 'dental clinic', 'οδοντίατρος', 'οδοντιατρείο', 'οδοντιατρική κλινική'],
    conversionGoal: { primary: 'book-appointment', secondary: 'phone-call' },
    requiredSections: ['hero', 'services', 'doctor-profile', 'trust-signals', 'hours', 'contact', 'find-us'],
    motionIntensity: 'restrained', schemaType: 'Dentist',
    media: {
      minimumPreferredImages: 2,
      requiredSubjects: Object.freeze(['doctor-or-team', 'clinic-space']),
      avoid: Object.freeze(['graphic-procedures', 'guaranteed-medical-outcomes', 'unconsented-patient-images']),
      fallbackStrategy: 'clinical-abstracts-and-credential-led-layout',
    },
    compatibleDesignSystemIds: ['marble', 'quiet', 'cinematic', 'living', 'grid', 'infinite', 'canvas', 'type-gallery', 'kinetic'],
  }),
  cafe: profile({
    id: 'cafe', label: 'Καφέ',
    aliases: ['cafe', 'coffee shop', 'καφέ', 'καφετέρια', 'specialty coffee'],
    conversionGoal: { primary: 'visit-location', secondary: 'phone-call' },
    requiredSections: ['hero', 'menu-highlights', 'services', 'atmosphere', 'hours', 'contact', 'find-us'],
    motionIntensity: 'expressive', schemaType: 'CafeOrCoffeeShop',
    media: {
      minimumPreferredImages: 4,
      requiredSubjects: Object.freeze(['signature-drink', 'venue-atmosphere']),
      avoid: Object.freeze(['unavailable-menu-items', 'misleading-location-views']),
      fallbackStrategy: 'brand-patterns-and-menu-led-bento',
    },
    compatibleDesignSystemIds: ['bloom', 'type-gallery', 'living', 'infinite', 'cinematic', 'kinetic', 'quiet', 'warmth', 'magazine'],
  }),
  lawyer: profile({
    id: 'lawyer', label: 'Δικηγορικό γραφείο',
    aliases: ['lawyer', 'attorney', 'legal office', 'δικηγόρος', 'δικηγορικό γραφείο', 'νομικές υπηρεσίες'],
    conversionGoal: { primary: 'request-consultation', secondary: 'phone-call' },
    requiredSections: ['hero', 'practice-areas', 'credentials', 'process', 'contact', 'find-us'],
    motionIntensity: 'restrained', schemaType: 'LegalService',
    media: {
      minimumPreferredImages: 1,
      requiredSubjects: Object.freeze(['professional-portrait-or-office']),
      avoid: Object.freeze(['courtroom-result-claims', 'guaranteed-legal-outcomes', 'client-identifying-material']),
      fallbackStrategy: 'typography-credentials-and-practice-area-led',
    },
    compatibleDesignSystemIds: ['marble', 'quiet', 'cinematic', 'grid', 'infinite', 'canvas', 'type-gallery', 'living', 'kinetic'],
  }),
  plumber: profile({
    id: 'plumber', label: 'Υδραυλικός',
    aliases: ['plumber', 'plumbing', 'υδραυλικός', 'υδραυλικές εργασίες', 'αποφράξεις'],
    conversionGoal: { primary: 'emergency-call', secondary: 'request-quote' },
    requiredSections: ['hero', 'emergency-callout', 'services', 'trust-signals', 'service-areas', 'contact'],
    motionIntensity: 'moderate', schemaType: 'Plumber',
    media: {
      minimumPreferredImages: 1,
      requiredSubjects: Object.freeze(['technician-or-tools']),
      avoid: Object.freeze(['unsafe-repair-scenes', 'unattributed-project-claims']),
      fallbackStrategy: 'service-icons-and-high-contrast-call-led',
    },
    compatibleDesignSystemIds: ['dispatch', 'kinetic', 'grid', 'type-gallery', 'infinite', 'cinematic', 'quiet', 'living', 'canvas'],
  }),
  rooms: profile({
    id: 'rooms', label: 'Ενοικιαζόμενα δωμάτια',
    aliases: ['rooms', 'lodging', 'hotel', 'ενοικιαζόμενα δωμάτια', 'κατάλυμα', 'ξενοδοχείο'],
    conversionGoal: { primary: 'booking-enquiry', secondary: 'phone-call' },
    requiredSections: ['hero', 'rooms', 'amenities', 'gallery', 'location', 'contact', 'find-us'],
    motionIntensity: 'moderate', schemaType: 'LodgingBusiness',
    media: {
      supportsNoPhoto: false,
      minimumPreferredImages: 8,
      requiredSubjects: Object.freeze(['room-interior', 'bathroom', 'exterior-or-view', 'amenities']),
      avoid: Object.freeze(['misleading-room-category', 'unavailable-amenities', 'unrelated-destination-stock']),
      fallbackStrategy: 'request-property-photos-before-publication',
    },
    compatibleDesignSystemIds: ['aegean', 'cinematic', 'infinite', 'living', 'quiet', 'canvas', 'type-gallery', 'kinetic', 'grid'],
  }),
  gym: profile({
    id: 'gym', label: 'Γυμναστήριο',
    aliases: ['gym', 'fitness', 'γυμναστήριο', 'fitness studio', 'personal training'],
    conversionGoal: { primary: 'trial-enquiry', secondary: 'phone-call' },
    requiredSections: ['hero', 'programs', 'facilities', 'trainers-or-method', 'hours', 'contact', 'find-us'],
    motionIntensity: 'expressive', schemaType: 'ExerciseGym',
    media: {
      minimumPreferredImages: 4,
      requiredSubjects: Object.freeze(['training-space', 'equipment-or-session']),
      avoid: Object.freeze(['unverified-transformation-claims', 'unsafe-exercise-form']),
      fallbackStrategy: 'kinetic-type-and-program-led-layout',
    },
    compatibleDesignSystemIds: ['volt', 'kinetic', 'type-gallery', 'infinite', 'runway', 'grid', 'cinematic', 'living', 'quiet'],
  }),
  garage: profile({
    id: 'garage', label: 'Συνεργείο αυτοκινήτων',
    aliases: ['garage', 'auto repair', 'mechanic', 'συνεργείο', 'συνεργείο αυτοκινήτων', 'μηχανικός αυτοκινήτων'],
    conversionGoal: { primary: 'service-call', secondary: 'directions' },
    requiredSections: ['hero', 'services', 'trust-signals', 'brands-or-vehicle-types', 'hours', 'contact', 'find-us'],
    motionIntensity: 'moderate', schemaType: 'AutoRepair',
    media: {
      minimumPreferredImages: 3,
      requiredSubjects: Object.freeze(['workshop', 'technician-or-diagnostic-equipment']),
      avoid: Object.freeze(['visible-license-plates', 'unsafe-lift-scenes', 'unattributed-repairs']),
      fallbackStrategy: 'diagnostic-ui-and-service-led-layout',
    },
    compatibleDesignSystemIds: ['motor', 'kinetic', 'grid', 'infinite', 'type-gallery', 'cinematic', 'quiet', 'living', 'canvas'],
  }),
  farm: profile({
    id: 'farm', label: 'Παραγωγός / Αγροτικά προϊόντα',
    aliases: ['farm', 'producer', 'olive oil', 'παραγωγός', 'αγροτικά προϊόντα', 'ελαιόλαδο', 'ελαιοπαραγωγός'],
    conversionGoal: { primary: 'product-enquiry', secondary: 'phone-call' },
    requiredSections: ['hero', 'products', 'origin-and-method', 'quality-signals', 'contact', 'find-us'],
    motionIntensity: 'restrained', schemaType: 'LocalBusiness',
    media: {
      minimumPreferredImages: 4,
      requiredSubjects: Object.freeze(['product', 'origin-or-production']),
      avoid: Object.freeze(['unsupported-certifications', 'misleading-origin-claims', 'generic-imported-product-stock']),
      fallbackStrategy: 'packaging-labels-and-origin-story-led',
    },
    compatibleDesignSystemIds: ['terra', 'living', 'quiet', 'cinematic', 'canvas', 'infinite', 'type-gallery', 'kinetic', 'grid'],
  }),
  generic: profile({
    id: 'generic', label: 'Τοπική επιχείρηση',
    aliases: ['generic', 'other', 'άλλο', 'λοιπά', 'local business'],
    conversionGoal: { primary: 'contact-enquiry', secondary: 'phone-call' },
    requiredSections: ['hero', 'services', 'trust-signals', 'contact', 'find-us'],
    motionIntensity: 'restrained', schemaType: 'LocalBusiness',
    media: {
      minimumPreferredImages: 0,
      fallbackStrategy: 'typography-service-and-trust-led',
    },
    compatibleDesignSystemIds: ['canvas', 'cinematic', 'type-gallery', 'quiet', 'kinetic', 'infinite', 'living', 'grid', 'runway'],
  }),
})

const normalize = (value) => String(value || '')
  .normalize('NFD')
  .replace(/[\u0300-\u036f]/g, '')
  .trim()
  .toLocaleLowerCase('el-GR')
  .replace(/[_-]+/g, ' ')
  .replace(/\s+/g, ' ')

const VERTICAL_ALIASES = new Map(
  Object.values(VERTICAL_PROFILES).flatMap((item) =>
    [item.id, ...item.aliases].map((alias) => [normalize(alias), item.id])),
)

export function getVerticalProfile(vertical) {
  const key = VERTICAL_ALIASES.get(normalize(vertical))
  return VERTICAL_PROFILES[key] || VERTICAL_PROFILES.generic
}

export function isDesignCompatible(vertical, designSystemId) {
  return getVerticalProfile(vertical).compatibleDesignSystemIds.includes(designSystemId)
}

export { DESIGN_SYSTEM_IDS }
