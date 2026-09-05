// ΠΑΡΑΓΟΜΕΝΟ — scripts/build_dark_mode.py. Μην το γράψεις στο χέρι.
//
// Το mode ΔΕΝ βγαίνει από όνομα theme. Βγαίνει από τη φωτεινότητα της
// επιφάνειας που δηλώνει το ίδιο το CSS του theme. Το tests/themeMode.mjs
// την ξαναϋπολογίζει και κόβει αν ο χάρτης αποκλίνει.
export const THEME_MODE = {
  'aegean': 'light',   // 0.9810
  'airspace-office': 'light',   // 1.0000
  'area-first': 'light',   // 0.9259
  'bakery-editorial': 'light',   // 0.8674
  'barber-shop': 'light',   // 1.0000
  'beauty-atelier': 'light',   // 0.8820
  'bigspring-advisory': 'light',   // 1.0000
  'billys-barber': 'light',   // 0.6584
  'bloom': 'light',   // 0.9659
  'blue-onepage': 'light',   // 1.0000
  'callout': 'light',   // 1.0000
  'canvas': 'light',   // 0.9560
  'chapter-snap': 'light',   // 0.7923
  'cinematic': 'dark',   // 0.0084
  'clean-work': 'light',   // 1.0000
  'clinic-triage': 'light',   // 1.0000
  'coast': 'light',   // 0.9722
  'constra-build': 'light',   // 0.9035
  'counter-menu': 'dark',   // 0.0030
  'directory-index': 'light',   // 1.0000
  'dispatch': 'dark',   // 0.0040
  'educenter-campus': 'light',   // 0.9560
  'elegance-salon': 'light',   // 0.9573
  'ember': 'dark',   // 0.0055
  'forge': 'light',   // 0.8856
  'freight-lane': 'light',   // 0.9295
  'frost-bakery': 'light',   // 0.8742
  'grecko-table': 'light',   // 0.8281
  'gymso-fitness': 'light',   // 1.0000
  'heritage-bakery': 'light',   // 0.8975
  'horizontal-story': 'dark',   // 0.0082
  'infinite': 'dark',   // 0.0065
  'kinetic': 'light',   // 0.8720
  'klassy-cafe': 'light',   // 1.0000
  'living': 'light',   // 0.8714
  'marble': 'light',   // 0.9560
  'medic-care': 'light',   // 1.0000
  'microbakery-lab': 'light',   // 0.7908
  'morning-journal': 'light',   // 0.9592
  'moso-interior': 'light',   // 1.0000
  'motor': 'dark',   // 0.0114
  'neighborhood-market': 'light',   // 0.8367
  'novena-care': 'light',   // 0.9703
  'price-first': 'light',   // 0.9071
  'property-atlas': 'light',   // 0.9053
  'pulse': 'light',   // 0.9873
  'quiet': 'light',   // 0.9283
  'runway': 'light',   // 1.0000
  'scandinavian-coffee': 'light',   // 0.8784
  'signature': 'light',   // 0.9566
  'terra': 'light',   // 0.8511
  'thomson-stylist': 'light',   // 1.0000
  'type-gallery': 'light',   // 0.8738
  'vertical-snap': 'dark',   // 0.0170
  'vex-counter': 'light',   // 1.0000
  'villa-agency': 'light',   // 1.0000
  'volt': 'dark',   // 0.0091
  'warmth': 'light',   // 0.9021
}

export function themeMode(key) {
  return THEME_MODE[key] === 'dark' ? 'dark' : 'light'
}
