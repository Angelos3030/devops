import './globals.css'
// Τα fonts σερβίρονται από εμάς (scripts/selfhost_fonts.py). Ο browser του
// επισκέπτη δεν μιλάει ποτέ με την Google: καμία IP προς τα έξω, κανένα
// banner συγκατάθεσης — και δύο λιγότερες συνδέσεις πριν φανεί το κείμενο.
import './fonts.css'

export const metadata = {
  title: 'Vitrina — Sites',
  description: 'Sites για ελληνικές τοπικές επιχειρήσεις.',
}

export default function RootLayout({ children }) {
  return (
    <html lang="el">
      <body>{children}</body>
    </html>
  )
}
