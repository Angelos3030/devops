// Κανόνες του editor, χωριστά από το UI ώστε να ελέγχονται χωρίς browser και
// χωρίς να γραφτεί τίποτα σε βάση. Οι τιμές ΚΑΘΡΕΦΤΙΖΟΥΝ το backend:
//
//   τύποι/μέγεθος → src/main.py           (upload_asset)
//   max υπηρεσίες → src/meta_oauth.py     (put_content, [:8])
//
// Αν αλλάξει το backend, αλλάζει ΚΑΙ εδώ — αλλιώς ο πελάτης βλέπει «εντάξει»
// και μετά αποτυγχάνει το ανέβασμα, που είναι χειρότερο από το να μην ξεκινήσει.
export const PHOTO_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
export const MAX_PHOTO_MB = 10
export const MAX_SERVICES = 8

/** {ok:true} ή {ok:false, error:'…'} σε απλά ελληνικά — το μήνυμα πάει στην οθόνη. */
export function validatePhoto(file) {
  if (!file) return { ok: false, error: 'Δεν διάλεξες αρχείο.' }
  if (!PHOTO_TYPES.includes(file.type)) {
    return {
      ok: false,
      error: `Δεκτές μόνο εικόνες JPG, PNG, WEBP ή GIF — αυτό είναι ${file.type || 'άγνωστου τύπου'}.`,
    }
  }
  if (file.size > MAX_PHOTO_MB * 1024 * 1024) {
    return {
      ok: false,
      error: `Η φωτογραφία είναι ${(file.size / 1048576).toFixed(1)}MB. Το όριο είναι ${MAX_PHOTO_MB}MB.`,
    }
  }
  return { ok: true }
}

export const canAddService = (services) => (services?.length || 0) < MAX_SERVICES

/** Πόσες γραμμές θα πεταχτούν σιωπηλά από το backend επειδή δεν έχουν όνομα. */
export const countEmptyServices = (services) =>
  (services || []).filter((sv) => !String(sv?.name || '').trim()).length

/** Προσθήκη στο ΤΕΛΟΣ — η σειρά που βλέπει ο πελάτης δεν αλλάζει ποτέ. */
export function addService(services) {
  const next = [...(services || [])]
  if (next.length >= MAX_SERVICES) return next
  next.push({ name: '', description: '' })
  return next
}

/** Επεξεργασία στη θέση: αν ξαναχτίζαμε τον πίνακα, οι γραμμές θα χοροπηδούσαν. */
export function setServiceField(services, index, key, value) {
  const next = [...(services || [])]
  if (!next[index]) return next
  next[index] = { ...next[index], [key]: value }
  return next
}

export const removeService = (services, index) =>
  (services || []).filter((_, i) => i !== index)
