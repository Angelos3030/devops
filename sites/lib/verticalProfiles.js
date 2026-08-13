const DESIGN_SYSTEM_IDS = Object.freeze([
  'editorial', 'split', 'bento', 'longform', 'poster', 'sidebar', 'grid',
  'magazine', 'warmth', 'ember', 'marble', 'runway', 'forge', 'aegean',
  'bloom', 'volt', 'motor', 'terra', 'dispatch', 'canvas',
  'cinematic', 'type-gallery', 'quiet', 'kinetic', 'infinite', 'living',
  'beauty-atelier',
  'clinic-triage',
  // Έλειπε από εδώ — γι' αυτό ΔΕΝ μπορούσε καν να μπει σε profile: το
  // tests/verticalProfiles.mjs κόβει κάθε id εκτός αυτής της λίστας.
  'callout',
  // Μονοπρόσωπος επαγγελματίας: ο άνθρωπος ΕΙΝΑΙ η μάρκα.
  'signature',
  'bakery-editorial', 'counter-menu', 'morning-journal', 'neighborhood-market', 'microbakery-lab', 'scandinavian-coffee', 'heritage-bakery',
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
    aliases: ['salon', 'hair salon', 'κομμωτήριο', 'κομμωτής', 'hair studio', 'barber', 'barbershop', 'κουρείο', 'νύχια', 'νυχάδικο', 'nixia', 'nyxia', 'nuxia', 'nail studio', 'nail salon', 'μανικιούρ', 'πεντικιούρ', 'μακιγιάζ'],
    conversionGoal: { primary: 'book-appointment', secondary: 'phone-call' },
    requiredSections: ['hero', 'services', 'pricing-or-consultation', 'work', 'hours', 'contact', 'find-us'],
    motionIntensity: 'expressive', schemaType: 'HairSalon',
    media: {
      minimumPreferredImages: 4,
      requiredSubjects: Object.freeze(['salon-space', 'style-detail']),
      avoid: Object.freeze(['unlicensed-before-after', 'misleading-client-results']),
      fallbackStrategy: 'editorial-color-and-typography-with-service-lookbook',
    },
    compatibleDesignSystemIds: ['beauty-atelier', 'runway', 'type-gallery', 'living', 'cinematic', 'infinite', 'kinetic', 'quiet', 'bloom', 'canvas', 'magazine', 'poster'],
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
    compatibleDesignSystemIds: ['clinic-triage', 'marble', 'quiet', 'cinematic', 'living', 'grid', 'infinite', 'canvas', 'type-gallery', 'editorial', 'bento', 'split'],
  }),
  physician: profile({
    id: 'physician', label: 'Ιατρείο',
    aliases: ['physician', 'doctor', 'medical office', 'γιατρός', 'ιατρός', 'ιατρείο', 'ιατρικό κέντρο', 'παθολόγος', 'καρδιολόγος', 'παιδίατρος', 'δερματολόγος', 'γυναικολόγος', 'ορθοπεδικός', 'οφθαλμίατρος', 'ωρλ', 'ψυχολόγος', 'διατροφολόγος', 'κτηνίατρος'],
    conversionGoal: { primary: 'book-appointment', secondary: 'phone-call' },
    requiredSections: ['hero', 'services', 'doctor-profile', 'credentials', 'visit-information', 'hours', 'contact', 'find-us'],
    motionIntensity: 'restrained', schemaType: 'Physician',
    media: {
      minimumPreferredImages: 2,
      requiredSubjects: Object.freeze(['doctor-portrait', 'medical-office']),
      avoid: Object.freeze(['graphic-procedures', 'guaranteed-outcomes', 'patient-identifying-images']),
      fallbackStrategy: 'credential-led-editorial-with-clinical-abstracts',
    },
    compatibleDesignSystemIds: ['clinic-triage', 'signature', 'marble', 'quiet', 'editorial', 'split', 'cinematic', 'grid', 'living', 'bento', 'canvas', 'sidebar'],
  }),
  pharmacy: profile({
    id: 'pharmacy', label: 'Φαρμακείο',
    aliases: ['pharmacy', 'drugstore', 'φαρμακείο', 'φαρμακοποιός', 'παραφαρμακείο', 'δερμοκαλλυντικά'],
    conversionGoal: { primary: 'phone-or-visit', secondary: 'directions' },
    requiredSections: ['hero', 'services', 'product-categories', 'on-duty-information', 'hours', 'contact', 'find-us'],
    motionIntensity: 'restrained', schemaType: 'Pharmacy',
    media: {
      minimumPreferredImages: 2,
      requiredSubjects: Object.freeze(['pharmacy-space-or-team', 'product-category-detail']),
      avoid: Object.freeze(['prescription-claims', 'unverified-health-claims', 'patient-identifying-images']),
      fallbackStrategy: 'health-service-and-category-led-layout',
    },
    compatibleDesignSystemIds: ['quiet', 'marble', 'grid', 'editorial', 'bento', 'split', 'living', 'clinic-triage', 'sidebar', 'canvas', 'infinite', 'type-gallery'],
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
    compatibleDesignSystemIds: ['beauty-atelier', 'bloom', 'quiet', 'clinic-triage', 'marble', 'runway', 'living', 'cinematic', 'type-gallery', 'bento', 'infinite', 'canvas'],
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
    compatibleDesignSystemIds: ['living', 'quiet', 'signature', 'aegean', 'bloom', 'clinic-triage', 'cinematic', 'infinite', 'canvas', 'marble', 'type-gallery', 'terra'],
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
    compatibleDesignSystemIds: ['bakery-editorial', 'counter-menu', 'morning-journal', 'neighborhood-market', 'microbakery-lab', 'scandinavian-coffee', 'heritage-bakery', 'bloom', 'type-gallery', 'living', 'cinematic', 'quiet'],
  }),
  retail: profile({
    id: 'retail', label: 'Κατάστημα λιανικής',
    aliases: ['retail', 'store', 'κατάστημα', 'boutique', 'μπουτίκ', 'ανθοπωλείο', 'κατάστημα ρούχων', 'υποδήματα', 'παπούτσια', 'κοσμήματα', 'οπτικά', 'βιβλιοπωλείο', 'είδη δώρων'],
    conversionGoal: { primary: 'product-enquiry', secondary: 'visit-location' },
    requiredSections: ['hero', 'products', 'new-arrivals', 'store-information', 'hours', 'contact', 'find-us'],
    motionIntensity: 'expressive', schemaType: 'Store',
    media: {
      minimumPreferredImages: 4,
      requiredSubjects: Object.freeze(['products', 'store-space']),
      avoid: Object.freeze(['unavailable-products', 'misleading-brand-affiliations', 'unlicensed-campaign-images']),
      fallbackStrategy: 'editorial-product-cards-and-brand-led-layout',
    },
    compatibleDesignSystemIds: ['bento', 'grid', 'type-gallery', 'quiet', 'living', 'infinite', 'canvas', 'cinematic', 'kinetic', 'magazine', 'editorial', 'split'],
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
    // Το `longform` (στενή στήλη, drop-cap, magazine ανάγνωση) ταιριάζει σε
    // επάγγελμα που πρέπει να ΕΞΗΓΗΣΕΙ: νομικά κείμενα, διαδικασίες, όροι.
    compatibleDesignSystemIds: ['marble', 'signature', 'quiet', 'cinematic', 'longform', 'grid', 'infinite', 'canvas', 'type-gallery', 'living', 'kinetic', 'editorial'],
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
    // Το `callout` φτιάχτηκε ΓΙΑ τεχνίτες (κάρτα προσφοράς στο hero, τηλέφωνο
    // έκτακτης, αριθμημένες υπηρεσίες) και ήταν ήδη πρώτο στο backend — αλλά
    // έλειπε από εδώ, οπότε ο πελάτης δεν το έβλεπε ΠΟΤΕ στον chooser.
    // Το `dispatch` ΔΕΝ επιστρέφει εδώ: αποκλείστηκε συνειδητά όταν το `callout`
    // το αντικατέστησε, και το tests/verticalProfiles.mjs το φυλάει ρητά.
    compatibleDesignSystemIds: ['callout', 'forge', 'grid', 'sidebar', 'poster', 'bento', 'kinetic', 'type-gallery', 'infinite', 'cinematic', 'quiet', 'living'],
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
    // Ο παραγωγός έχει ιστορία να πει (γενιές, τόπος, μέθοδος) — το `longform`
    // είναι το μόνο μας αρχέτυπο φτιαγμένο για συνεχή ανάγνωση.
    compatibleDesignSystemIds: ['terra', 'living', 'quiet', 'cinematic', 'longform', 'canvas', 'infinite', 'type-gallery', 'kinetic', 'grid', 'editorial', 'magazine'],
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

// Περιγραφές onboarding περιέχουν επωνυμία, πόλη και ελεύθερο κείμενο. Exact
// lookup δεν αρκεί: «Φαρμακείο Μαρία στον Γέρακα» πρέπει να αναγνωρίζεται. Η
// μεγαλύτερη φράση κερδίζει ώστε «οδοντιατρική κλινική» να προηγείται του
// γενικότερου «κλινική» όταν προστεθούν νέες κατηγορίες.
const SORTED_ALIASES = Object.freeze(
  [...VERTICAL_ALIASES.entries()].sort((a, b) => b[0].length - a[0].length),
)

export function getVerticalProfile(vertical) {
  const normalized = normalize(vertical)
  const exact = VERTICAL_ALIASES.get(normalized)
  const matched = exact || SORTED_ALIASES.find(([alias]) =>
    normalized === alias || normalized.includes(alias),
  )?.[1]
  const key = matched
  return VERTICAL_PROFILES[key] || VERTICAL_PROFILES.generic
}

export function isDesignCompatible(vertical, designSystemId) {
  return getVerticalProfile(vertical).compatibleDesignSystemIds.includes(designSystemId)
}

export { DESIGN_SYSTEM_IDS }
