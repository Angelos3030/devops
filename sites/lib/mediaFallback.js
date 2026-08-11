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
  // Ο καφές ΔΕΝ είναι ταβέρνα. Πριν από αυτό, «έχω καφέ» έπαιρνε φωτογραφίες
  // με σουβλάκια και ψητά — ο πελάτης το βλέπει και φεύγει.
  cafe: [
    ['photo-1495474472287-4d71bcdd2085', 'Ο καφές μας'],
    ['photo-1442512595331-e89e73853f31', 'Η γωνιά μας'],
    ['photo-1445205170230-053b83016050', 'Φρέσκα γλυκά'],
    ['photo-1470337458703-46ad1756a187', 'Καθημερινή απόλαυση'],
  ],
  beauty: [
    ['photo-1560066984-138dadb4c035', 'Ο χώρος περιποίησης'],
    ['photo-1522337660859-02fbefca4702', 'Styling'],
    ['photo-1595476108010-b4d1f102b1b1', 'Περιποίηση μαλλιών'],
    ['photo-1521590832167-7bcbfaa6381f', 'Προσωπικό στυλ'],
  ],
  nails: [
    ['photo-1604654894610-df63bc536371', 'Περιποίηση νυχιών'],
    ['photo-1610992015732-2449b76344bc', 'Nail art'],
    ['photo-1632345031435-8727f6897d53', 'Μανικιούρ'],
    ['photo-1607779097040-26e80aa78e66', 'Χρώμα και λεπτομέρεια'],
  ],
  health: [
    ['photo-1629909613654-28e377c37b09', 'Σύγχρονος χώρος φροντίδας'],
    ['photo-1588776814546-1ffcf47267a5', 'Χώρος υποδοχής'],
    ['photo-1606811841689-23dfddce3e95', 'Σύγχρονος εξοπλισμός'],
    ['photo-1519494026892-80bbd2d6fd0d', 'Άνετο περιβάλλον'],
  ],
  wellness: [
    ['photo-1544161515-4ab6ce6db874', 'Χώρος ευεξίας'],
    ['photo-1600334089648-b0d9d3028eb2', 'Στιγμή χαλάρωσης'],
    ['photo-1540555700478-4be289fbecef', 'Ήρεμο περιβάλλον'],
    ['photo-1519823551278-64ac92734fb1', 'Φροντίδα σώματος'],
  ],
  retail: [
    ['photo-1441986300917-64674bd600d8', 'Το κατάστημα'],
    ['photo-1528698827591-e19ccd7bc23d', 'Επιλεγμένα προϊόντα'],
    ['photo-1472851294608-062f824d29cc', 'Η συλλογή μας'],
    ['photo-1449247709967-d4461a6a6103', 'Λεπτομέρεια χώρου'],
  ],
  gym: [
    ['photo-1534438327276-14e5300c3a48', 'Ο χώρος προπόνησης'],
    ['photo-1571019613454-1cb2f99b2d8b', 'Προπόνηση'],
    ['photo-1517836357463-d25dfeac3438', 'Εξοπλισμός'],
    ['photo-1581009146145-b5ef050c2e1e', 'Καθοδήγηση'],
  ],
  garage: [
    ['photo-1486006920555-c77dcf18193c', 'Το συνεργείο'],
    ['photo-1619642751034-765dfdf7c58e', 'Διάγνωση οχήματος'],
    ['photo-1625047509248-ec889cbff17f', 'Τεχνικός έλεγχος'],
    ['photo-1504222490345-c075b6008014', 'Εργασία με ακρίβεια'],
  ],
  farm: [
    ['photo-1500382017468-9049fed747ef', 'Ο τόπος παραγωγής'],
    ['photo-1464226184884-fa280b87c399', 'Η παραγωγή μας'],
    ['photo-1471193945509-9ad0617afabf', 'Φρέσκα προϊόντα'],
    ['photo-1498579397066-22750a3cb424', 'Από τη γη'],
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
  // Ελληνικό κατάλυμα, ελληνική εικόνα. Το pool είχε τροπικό resort — φοίνικες
  // και ξύλινα μπανγκαλόου — που για ξενοδοχείο στην Πάρο ή στη Χαλκιδική
  // διαβάζεται αμέσως ως ξένο stock. Ίδια φωτογραφική κατεύθυνση με το demo
  // «Θαλασσιά» στο demoData.js, ώστε πελάτης και showcase να μη διαφωνούν.
  hospitality: [
    ['photo-1601581875309-fafbf2d3ed3a', 'Κυκλαδίτικη φιλοξενία'],
    ['photo-1530841377377-3ff06c0ca713', 'Θέα στο Αιγαίο'],
    ['photo-1504512485720-7d83a16ee930', 'Η γειτονιά'],
    ['photo-1507525428034-b723cf961d3e', 'Δίπλα στη θάλασσα'],
  ],
}

const RULES = [
  ['carpenter', /ξυλ|κουζιν|ντουλαπ|επιπλ|ανακαιν/i],
  // ΠΡΟΣΟΧΗ στη σειρά: το «cafe» πρέπει να ελεγχθεί ΠΡΙΝ το «food», αλλιώς
  // το «καφε» πιάνεται από τον κανόνα της ταβέρνας.
  ['cafe', /καφε|καφέ|cafe|coffee|φουρν|αρτοποι|ζαχαροπλ|bakery|creperi|κρεπερ|παγωτ|brunch/i],
  ['food', /ταβερ|εστια|ψησταρ|σουβλα|grill|πιτσαρ|pizza|μεζε|bar|μπαρ/i],
  ['wellness', /μασαζ|massage|wellness|ευεξ|ρεφλεξολογ|pilates|yoga/i],
  ['nails', /νυχι|νυχαδ|μανικιουρ|πεντικιουρ|nail/i],
  ['beauty', /κομμ|κουρει|barber|hair|salon|beauty|αισθητ|spa/i],
  ['health', /ιατρ|οδοντ|κλιν|θεραπε|φυσιο/i],
  ['hospitality', /ξενοδο|δωματι|villa|τουρισ|καταλυ/i],
  ['gym', /γυμναστ|fitness|crossfit|personal train|σχολη χορου|πολεμικ/i],
  ['garage', /συνεργει|μηχανικ.*αυτοκιν|βουλκανιζ|φανοποι|auto repair|garage/i],
  ['farm', /παραγωγ|αγροτικ|ελαιολαδ|οινοποι|μελισσοκ|τυροκομ|κτηνοτροφ|βιολογικ/i],
  ['retail', /καταστημ|boutique|μπουτικ|ανθοπωλ|ρουχ|υποδημ|παπουτσ|κοσμημ|οπτικ|βιβλιοπωλ|ειδη δωρων/i],
  ['technician', /υδραυλ|ηλεκτρ|τεχν|συνεργ|μηχαν|ψυκτικ/i],
]

// Ο πελάτης γράφει «Ταβέρνα», όχι «ταβερνα». Οι κανόνες είναι γραμμένοι χωρίς
// τόνους, οπότε χωρίς αυτό το βήμα ΚΑΝΕΝΑΣ δεν ταίριαζε: «ταβέρνα», «φούρνος»,
// «κομμωτήριο» έπεφταν όλα στο ουδέτερο «professional» με φωτογραφίες γραφείου.
const stripTones = (t) => t.normalize('NFD').replace(/[̀-ͯ]/g, '')

export function mediaCategoryFor(data) {
  // Identity wins over service names. A dentist commonly offers "Αισθητική
  // οδοντιατρική"; matching the full payload used to classify that as a beauty
  // salon and replace dental imagery with hair/nail photos.
  const identity = stripTones([data?.TRADE, data?.type].filter(Boolean).join(' '))
  const identityMatch = RULES.find(([, pattern]) => pattern.test(identity))
  if (identityMatch) return identityMatch[0]

  const context = stripTones(
    [data?.TAGLINE, ...(data?.services || []).map(x => x?.title)]
      .filter(Boolean).join(' '))
  return RULES.find(([, pattern]) => pattern.test(context))?.[0] || 'professional'
}

export function withMediaFallback(data = {}) {
  const hasHero = Boolean(data.HERO_IMAGE)
  const hasGallery = Array.isArray(data.gallery) && data.gallery.some(item => item?.image)
  if (hasHero && hasGallery) return { ...data, MEDIA_MODE: data.MEDIA_MODE || 'real' }

  const category = mediaCategoryFor(data)
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
