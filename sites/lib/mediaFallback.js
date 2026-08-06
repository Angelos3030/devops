const unsplash = (id, width = 1600) =>
  `https://images.unsplash.com/${id}?auto=format&fit=crop&w=${width}&q=84`

const LIBRARY = {
  carpenter: [
    ['photo-1556911220-bff31c812dba', 'Σχεδιασμός κουζίνας'],
    ['photo-1595428774223-ef52624120d2', 'Ξύλινη κατασκευή'],
    ['photo-1616486338812-3dadae4b4ace', 'Λεπτομέρεια επίπλου'],
    ['photo-1493663284031-b7e3aefcae8e', 'Εσωτερικός χώρος'],
  ],
  food: [
    ['photo-1517248135467-4c7edcad34c4', 'Ο χώρος'],
    ['photo-1544025162-d76694265947', 'Πιάτο ημέρας'],
    ['photo-1540189549336-e6e99c3679fe', 'Φρέσκες γεύσεις'],
    ['photo-1555939594-58d7cb561ad1', 'Στο τραπέζι'],
  ],
  beauty: [
    ['photo-1560066984-138dadb4c035', 'Ο χώρος περιποίησης'],
    ['photo-1522337660859-02fbefca4702', 'Styling'],
    ['photo-1595476108010-b4d1f102b1b1', 'Περιποίηση μαλλιών'],
    ['photo-1521590832167-7bcbfaa6381f', 'Προσωπικό στυλ'],
  ],
  health: [
    ['photo-1629909613654-28e377c37b09', 'Σύγχρονος χώρος φροντίδας'],
    ['photo-1588776814546-1ffcf47267a5', 'Χώρος υποδοχής'],
    ['photo-1606811841689-23dfddce3e95', 'Σύγχρονος εξοπλισμός'],
    ['photo-1519494026892-80bbd2d6fd0d', 'Άνετο περιβάλλον'],
  ],
  professional: [
    ['photo-1497366216548-37526070297c', 'Επαγγελματικός χώρος'],
    ['photo-1521737604893-d14cc237f11d', 'Συνεργασία'],
    ['photo-1454165804606-c3d57bc86b40', 'Μελέτη και οργάνωση'],
    ['photo-1450101499163-c8848c66ca85', 'Προσοχή στη λεπτομέρεια'],
  ],
  technician: [
    ['photo-1621905251189-08b45d6a269e', 'Επαγγελματική εργασία'],
    ['photo-1581578731548-c64695cc6952', 'Τεχνική υποστήριξη'],
    ['photo-1621905252507-b35492cc74b4', 'Εγκατάσταση'],
    ['photo-1607472586893-edb57bdc0e39', 'Καθαρή δουλειά'],
  ],
  hospitality: [
    ['photo-1519046904884-53103b34b206', 'Η εμπειρία του χώρου'],
    ['photo-1520250497591-112f2f40a3f4', 'Φιλοξενία'],
    ['photo-1571003123894-1f0594d2b5d9', 'Χαλάρωση'],
    ['photo-1540541338287-41700207dee6', 'Παροχές'],
  ],
}

const RULES = [
  ['carpenter', /ξυλ|κουζιν|ντουλαπ|επιπλ|ανακαιν/i],
  ['food', /ταβερ|εστια|καφ|φουρ|ζαχαρο|bar|cafe/i],
  ['beauty', /κομμ|beauty|αισθητ|νυχι|spa/i],
  ['health', /ιατρ|οδοντ|κλιν|θεραπε|φυσιο/i],
  ['hospitality', /ξενοδο|δωματι|villa|τουρισ|καταλυ/i],
  ['technician', /υδραυλ|ηλεκτρ|τεχν|συνεργ|μηχαν|ψυκτικ/i],
]

function categoryFor(data) {
  const text = [data?.TRADE, data?.type, data?.TAGLINE, ...(data?.services || []).map(x => x?.title)]
    .filter(Boolean).join(' ')
  return RULES.find(([, pattern]) => pattern.test(text))?.[0] || 'professional'
}

export function withMediaFallback(data = {}) {
  const hasHero = Boolean(data.HERO_IMAGE)
  const hasGallery = Array.isArray(data.gallery) && data.gallery.some(item => item?.image)
  if (hasHero && hasGallery) return { ...data, MEDIA_MODE: data.MEDIA_MODE || 'real' }

  const category = categoryFor(data)
  const images = LIBRARY[category]
  const fallbackGallery = images.slice(1).map(([id, title]) => ({
    image: unsplash(id, 1200),
    title,
    sub: 'Ενδεικτική εικόνα',
    illustrative: true,
  }))

  return {
    ...data,
    HERO_IMAGE: data.HERO_IMAGE || unsplash(images[0][0]),
    STORY_IMAGE: data.STORY_IMAGE || unsplash(images[1][0], 1200),
    gallery: hasGallery ? data.gallery : fallbackGallery,
    MEDIA_MODE: hasHero || hasGallery ? 'mixed' : 'no-photo',
    MEDIA_NOTICE: 'Οι συμπληρωματικές εικόνες είναι ενδεικτικές και αντικαθίστανται με υλικό της επιχείρησης.',
  }
}

