// Η δημόσια βάση URL της εφαρμογής (dashboard + /gia ad landings).
//
// Το app.getvitrina.gr δεν είναι συνδεδεμένο αυτή τη στιγμή (το Railway Hobby
// επιτρέπει 2 custom domains/service και τα κρατάει ο πρώτος πελάτης), οπότε
// default = το Railway URL ώστε canonical/sitemap να ΜΗ δείχνουν σε 404.
// Μόλις συνδεθεί το app.getvitrina.gr, θέσε NEXT_PUBLIC_APP_BASE και τελείωσε.
export const APP_BASE = (
  process.env.NEXT_PUBLIC_APP_BASE || 'https://sites-production-da56.up.railway.app'
).replace(/\/$/, '')
