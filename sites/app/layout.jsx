import './globals.css'

export const metadata = {
  title: 'Vitrina — Sites',
  description: 'Sites για ελληνικές τοπικές επιχειρήσεις.',
}

export default function RootLayout({ children }) {
  return (
    <html lang="el">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Anton&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,500;0,9..144,600;1,9..144,400&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Nunito+Sans:wght@400;600;700&family=Fira+Sans+Condensed:wght@600;700;800&family=Alegreya:ital,wght@0,500;0,700;1,500&family=Noto+Serif+Display:ital,wght@0,300;0,400;0,500;1,300&family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Manrope:wght@400;600;800&family=Roboto+Slab:wght@500;700&family=Literata:ital,opsz,wght@0,7..72,300;0,7..72,400;1,7..72,300&family=Comfortaa:wght@500;700&family=Fira+Sans:wght@400;600&family=Syne:wght@700;800&family=Open+Sans:wght@400;600&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  )
}
