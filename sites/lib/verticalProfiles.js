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
    aliases: ['carpenter', 'woodworker', 'ξυλουργός', 'ξυλουργείο', 'ξυλουργικό εργαστήριο', 'κουζίνες', 'ντουλάπες', 'επιπλοποιός', 'έπιπλα', 'μαραγκός', 'κουφώματα', 'ανακαινίσεις'],
    conversionGoal: { primary: 'request-quote', secondary: 'phone-call' },
    requiredSections: ['hero', 'services', 'work', 'process', 'service-areas', 'contact', 'find-us'],
    motionIntensity: 'moderate', schemaType: 'HomeAndConstructionBusiness',
    media: {
      minimumPreferredImages: 4,
      requiredSubjects: Object.freeze(['finished-work', 'material-detail']),
      avoid: Object.freeze(['unattributed-project-claims', 'unsafe-workshop-scenes']),
      fallbackStrategy: 'material-textures-and-typographic-project-cards',
    },
    compatibleDesignSystemIds: ['canvas', 'runway', 'grid', 'cinematic', 'type-gallery', 'quiet', 'kinetic', 'infinite', 'living', 'forge', 'editorial', 'magazine'],
  }),
  taverna: profile({
    id: 'taverna', label: 'Ταβέρνα / Εστιατόριο',
    aliases: ['taverna', 'restaurant', 'ταβέρνα', 'εστιατόριο', 'μεζεδοπωλείο', 'ψητοπωλείο', 'σουβλατζίδικο', 'πιτσαρία', 'μαγειρείο', 'catering', 'ζαχαροπλαστείο', 'μπαρ'],
    conversionGoal: { primary: 'reservation-call', secondary: 'directions' },
    requiredSections: ['hero', 'menu-highlights', 'services', 'atmosphere', 'hours', 'contact', 'find-us'],
    motionIntensity: 'moderate', schemaType: 'Restaurant',
    media: {
      minimumPreferredImages: 5,
      requiredSubjects: Object.freeze(['signature-dishes', 'dining-space']),
      avoid: Object.freeze(['generic-food-unrelated-to-menu', 'misleading-dish-claims']),
      fallbackStrategy: 'menu-led-layout-with-ingredient-illustrations',
    },
    compatibleDesignSystemIds: ['warmth', 'ember', 'magazine', 'cinematic', 'type-gallery', 'living', 'infinite', 'quiet', 'kinetic', 'poster', 'bloom', 'aegean'],
  }),
  salon: profile({
    id: 'salon', label: 'Κομμωτήριο',
    aliases: ['salon', 'hair salon', 'κομμωτήριο', 'κομμωτής', 'hair studio', 'barber', 'barbershop', 'κουρείο', 'νύχια', 'nail studio', 'μανικιούρ', 'μακιγιάζ'],
    conversionGoal: { primary: 'book-appointment', secondary: 'phone-call' },
    requiredSections: ['hero', 'services', 'pricing-or-consultation', 'work', 'hours', 'contact', 'find-us'],
    motionIntensity: 'expressive', schemaType: 'HairSalon',
    media: {
      minimumPreferredImages: 4,
      requiredSubjects: Object.freeze(['salon-space', 'style-detail']),
      avoid: Object.freeze(['unlicensed-before-after', 'misleading-client-results']),
      fallbackStrategy: 'editorial-color-and-typography-with-service-lookbook',
    },
    compatibleDesignSystemIds: ['runway', 'type-gallery', 'living', 'cinematic', 'infinite', 'kinetic', 'quiet', 'bloom', 'canvas', 'magazine', 'poster', 'bento'],
  }),
  dentist: profile({
    id: 'dentist', label: 'Οδοντιατρείο',
    aliases: ['dentist', 'dental clinic', 'οδοντίατρος', 'οδοντιατρείο', 'οδοντιατρική κλινική', 'ορθοδοντικός', 'παιδοδοντίατρος', 'περιοδοντολόγος'],
    conversionGoal: { primary: 'book-appointment', secondary: 'phone-call' },
    requiredSections: ['hero', 'services', 'doctor-profile', 'trust-signals', 'hours', 'contact', 'find-us'],
    motionIntensity: 'restrained', schemaType: 'Dentist',
    media: {
      minimumPreferredImages: 2,
      requiredSubjects: Object.freeze(['doctor-or-team', 'clinic-space']),
      avoid: Object.freeze(['graphic-procedures', 'guaranteed-medical-outcomes', 'unconsented-patient-images']),
      fallbackStrategy: 'clinical-abstracts-and-credential-led-layout',
    },
    compatibleDesignSystemIds: ['marble', 'quiet', 'cinematic', 'living', 'grid', 'infinite', 'canvas', 'type-gallery', 'kinetic', 'editorial', 'bento', 'split'],
  }),
  physician: profile({
    id: 'physician', label: 'Ιατρείο',
    aliases: ['physician', 'doctor', 'medical office', 'γιατρός', 'ιατρός', 'ιατρείο', 'ιατρικό κέντρο', 'παθολόγος', 'καρδιολόγος', 'παιδίατρος', 'δερματολόγος', 'γυναικολόγος', 'ορθοπεδικός', 'οφθαλμίατρος', 'ωρλ', 'ψυχολόγος', 'διατροφολόγος', 'κτηνίατρος', 'φαρμακείο'],
    conversionGoal: { primary: 'book-appointment', secondary: 'phone-call' },
    requiredSections: ['hero', 'services', 'doctor-profile', 'credentials', 'visit-information', 'hours', 'contact', 'find-us'],
    motionIntensity: 'restrained', schemaType: 'Physician',
    media: {
      minimumPreferredImages: 2,
      requiredSubjects: Object.freeze(['doctor-portrait', 'medical-office']),
      avoid: Object.freeze(['graphic-procedures', 'guaranteed-outcomes', 'patient-identifying-images']),
      fallbackStrategy: 'credential-led-editorial-with-clinical-abstracts',
    },
    compatibleDesignSystemIds: ['marble', 'quiet', 'editorial', 'split', 'cinematic', 'grid', 'living', 'bento', 'canvas', 'sidebar', 'infinite', 'type-gallery'],
  }),
  aesthetics: profile({
    id: 'aesthetics', label: 'Κέντρο αισθητικής',
    aliases: ['aesthetics', 'beauty clinic', 'κέντρο αισθητικής', 'αισθητικός', 'ινστιτούτο αισθητικής', 'laser αποτρίχωση', 'spa προσώπου', 'αισθητική προσώπου', 'κέντρο ομορφιάς'],
    conversionGoal: { primary: 'book-treatment', secondary: 'phone-call' },
    requiredSections: ['hero', 'treatments', 'expertise', 'experience', 'pricing-or-consultation', 'contact', 'find-us'],
    motionIntensity: 'moderate', schemaType: 'BeautySalon',
    media: {
      minimumPreferredImages: 3,
      requiredSubjects: Object.freeze(['treatment-space', 'treatment-detail']),
      avoid: Object.freeze(['unconsented-before-after', 'medical-result-guarantees', 'over-retouched-results']),
      fallbackStrategy: 'soft-editorial-treatment-led-layout',
    },
    compatibleDesignSystemIds: ['bloom', 'quiet', 'marble', 'runway', 'living', 'cinematic', 'type-gallery', 'bento', 'infinite', 'canvas', 'magazine', 'poster'],
  }),
  massage: profile({
    id: 'massage', label: 'Massage / Wellness',
    aliases: ['massage', 'wellness', 'spa', 'μασάζ', 'κέντρο μασάζ', 'ευεξία', 'φυσικοθεραπευτής', 'φυσικοθεραπεία', 'ρεφλεξολογία', 'pilates studio', 'yoga studio'],
    conversionGoal: { primary: 'book-session', secondary: 'phone-call' },
    requiredSections: ['hero', 'treatments', 'benefits', 'therapist-or-method', 'session-information', 'contact', 'find-us'],
    motionIntensity: 'restrained', schemaType: 'HealthAndBeautyBusiness',
    media: {
      minimumPreferredImages: 3,
      requiredSubjects: Object.freeze(['treatment-room', 'wellness-detail']),
      avoid: Object.freeze(['sexualized-imagery', 'medical-cure-claims', 'unconsented-client-images']),
      fallbackStrategy: 'calm-materials-and-wellness-typography',
    },
    compatibleDesignSystemIds: ['living', 'quiet', 'aegean', 'bloom', 'warmth', 'cinematic', 'infinite', 'canvas', 'marble', 'type-gallery', 'terra', 'magazine'],
  }),
  cafe: profile({
    id: 'cafe', label: 'Καφέ',
    aliases: ['cafe', 'coffee shop', 'καφέ', 'καφετέρια', 'specialty coffee', 'φούρνος', 'αρτοποιείο', 'bakery', 'παγωτατζίδικο', 'brunch'],
    conversionGoal: { primary: 'visit-location', secondary: 'phone-call' },
    requiredSections: ['hero', 'menu-highlights', 'services', 'atmosphere', 'hours', 'contact', 'find-us'],
    motionIntensity: 'expressive', schemaType: 'CafeOrCoffeeShop',
    media: {
      minimumPreferredImages: 4,
      requiredSubjects: Object.freeze(['signature-drink', 'venue-atmosphere']),
      avoid: Object.freeze(['unavailable-menu-items', 'misleading-location-views']),
      fallbackStrategy: 'brand-patterns-and-menu-led-bento',
    },
    compatibleDesignSystemIds: ['bloom', 'type-gallery', 'living', 'infinite', 'cinematic', 'kinetic', 'quiet', 'warmth', 'magazine', 'poster', 'ember', 'bento'],
  }),
  lawyer: profile({
    id: 'lawyer', label: 'Δικηγορικό γραφείο',
    aliases: ['lawyer', 'attorney', 'legal office', 'δικηγόρος', 'δικηγορικό γραφείο', 'νομικές υπηρεσίες', 'λογιστής', 'λογιστικό γραφείο', 'συμβολαιογράφος', 'ασφαλιστής', 'σύμβουλος επιχειρήσεων', 'μεσίτης', 'μεσιτικό γραφείο', 'μηχανικός', 'αρχιτέκτονας'],
    conversionGoal: { primary: 'request-consultation', secondary: 'phone-call' },
    requiredSections: ['hero', 'practice-areas', 'credentials', 'process', 'contact', 'find-us'],
    motionIntensity: 'restrained', schemaType: 'LegalService',
    media: {
      minimumPreferredImages: 1,
      requiredSubjects: Object.freeze(['professional-portrait-or-office']),
      avoid: Object.freeze(['courtroom-result-claims', 'guaranteed-legal-outcomes', 'client-identifying-material']),
      fallbackStrategy: 'typography-credentials-and-practice-area-led',
    },
    compatibleDesignSystemIds: ['marble', 'quiet', 'cinematic', 'grid', 'infinite', 'canvas', 'type-gallery', 'living', 'kinetic', 'editorial', 'sidebar', 'bento'],
  }),
  plumber: profile({
    id: 'plumber', label: 'Υδραυλικός',
    aliases: ['plumber', 'plumbing', 'υδραυλικός', 'υδραυλικές εργασίες', 'αποφράξεις', 'ηλεκτρολόγος', 'ψυκτικός', 'κλειδαράς', 'ελαιοχρωματιστής', 'μπογιατζής', 'τεχνίτης', 'μάστορας', 'καθαρισμός', 'συνεργείο καθαρισμού', 'απεντομώσεις', 'μετακομίσεις'],
    conversionGoal: { primary: 'emergency-call', secondary: 'request-quote' },
    requiredSections: ['hero', 'emergency-callout', 'services', 'trust-signals', 'service-areas', 'contact'],
    motionIntensity: 'moderate', schemaType: 'Plumber',
    media: {
      minimumPreferredImages: 1,
      requiredSubjects: Object.freeze(['technician-or-tools']),
      avoid: Object.freeze(['unsafe-repair-scenes', 'unattributed-project-claims']),
      fallbackStrategy: 'service-icons-and-high-contrast-call-led',
    },
    compatibleDesignSystemIds: ['dispatch', 'kinetic', 'grid', 'type-gallery', 'infinite', 'cinematic', 'quiet', 'living', 'canvas', 'forge', 'poster', 'bento'],
  }),
  rooms: profile({
    id: 'rooms', label: 'Ενοικιαζόμενα δωμάτια',
    aliases: ['rooms', 'lodging', 'hotel', 'ενοικιαζόμενα δωμάτια', 'κατάλυμα', 'ξενοδοχείο', 'airbnb', 'βίλα', 'ξενώνας', 'τουριστικό γραφείο'],
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
    compatibleDesignSystemIds: ['aegean', 'cinematic', 'infinite', 'living', 'quiet', 'canvas', 'type-gallery', 'kinetic', 'grid', 'marble', 'magazine', 'bloom'],
  }),
  gym: profile({
    id: 'gym', label: 'Γυμναστήριο',
    aliases: ['gym', 'fitness', 'γυμναστήριο', 'fitness studio', 'personal training', 'personal trainer', 'crossfit', 'σχολή χορού', 'πολεμικές τέχνες'],
    conversionGoal: { primary: 'trial-enquiry', secondary: 'phone-call' },
    requiredSections: ['hero', 'programs', 'facilities', 'trainers-or-method', 'hours', 'contact', 'find-us'],
    motionIntensity: 'expressive', schemaType: 'ExerciseGym',
    media: {
      minimumPreferredImages: 4,
      requiredSubjects: Object.freeze(['training-space', 'equipment-or-session']),
      avoid: Object.freeze(['unverified-transformation-claims', 'unsafe-exercise-form']),
      fallbackStrategy: 'kinetic-type-and-program-led-layout',
    },
    compatibleDesignSystemIds: ['volt', 'kinetic', 'type-gallery', 'infinite', 'runway', 'grid', 'cinematic', 'living', 'quiet', 'poster', 'bento', 'motor'],
  }),
  garage: profile({
    id: 'garage', label: 'Συνεργείο αυτοκινήτων',
    aliases: ['garage', 'auto repair', 'mechanic', 'συνεργείο', 'συνεργείο αυτοκινήτων', 'μηχανικός αυτοκινήτων', 'βουλκανιζατέρ', 'φανοποιείο', 'ηλεκτρολόγος αυτοκινήτων', 'πλυντήριο αυτοκινήτων', 'ανταλλακτικά αυτοκινήτων'],
    conversionGoal: { primary: 'service-call', secondary: 'directions' },
    requiredSections: ['hero', 'services', 'trust-signals', 'brands-or-vehicle-types', 'hours', 'contact', 'find-us'],
    motionIntensity: 'moderate', schemaType: 'AutoRepair',
    media: {
      minimumPreferredImages: 3,
      requiredSubjects: Object.freeze(['workshop', 'technician-or-diagnostic-equipment']),
      avoid: Object.freeze(['visible-license-plates', 'unsafe-lift-scenes', 'unattributed-repairs']),
      fallbackStrategy: 'diagnostic-ui-and-service-led-layout',
    },
    compatibleDesignSystemIds: ['motor', 'kinetic', 'grid', 'infinite', 'type-gallery', 'cinematic', 'quiet', 'living', 'canvas', 'volt', 'forge', 'poster'],
  }),
  farm: profile({
    id: 'farm', label: 'Παραγωγός / Αγροτικά προϊόντα',
    aliases: ['farm', 'producer', 'olive oil', 'παραγωγός', 'αγροτικά προϊόντα', 'ελαιόλαδο', 'ελαιοπαραγωγός', 'οινοποιείο', 'μελισσοκόμος', 'τυροκομείο', 'κτηνοτρόφος', 'βιολογικά προϊόντα', 'παντοπωλείο'],
    conversionGoal: { primary: 'product-enquiry', secondary: 'phone-call' },
    requiredSections: ['hero', 'products', 'origin-and-method', 'quality-signals', 'contact', 'find-us'],
    motionIntensity: 'restrained', schemaType: 'LocalBusiness',
    media: {
      minimumPreferredImages: 4,
      requiredSubjects: Object.freeze(['product', 'origin-or-production']),
      avoid: Object.freeze(['unsupported-certifications', 'misleading-origin-claims', 'generic-imported-product-stock']),
      fallbackStrategy: 'packaging-labels-and-origin-story-led',
    },
    compatibleDesignSystemIds: ['terra', 'living', 'quiet', 'cinematic', 'canvas', 'infinite', 'type-gallery', 'kinetic', 'grid', 'editorial', 'magazine', 'warmth'],
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
    compatibleDesignSystemIds: ['canvas', 'cinematic', 'type-gallery', 'quiet', 'kinetic', 'infinite', 'living', 'grid', 'runway', 'editorial', 'bento', 'magazine'],
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
