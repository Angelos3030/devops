# Vitrina Template Collection

Η επίσημη συλλογή περιλαμβάνει 20 structurally distinct React templates. Τα templates
επιλέγονται από το backend ανά επάγγελμα και αποδίδονται από το κοινό multi-tenant `sites/` app.

## Επίσημα templates

| Template | Κατεύθυνση | Κατάλληλο για |
|---|---|---|
| `editorial` | premium editorial | ξυλουργούς, δημιουργικά επαγγέλματα |
| `split` | fixed identity panel | portfolio και επαγγελματίες |
| `bento` | modular visual grid | πολλές υπηρεσίες και έργα |
| `longform` | text-led story | επαγγελματίες χωρίς πολλές εικόνες |
| `poster` | typography-first | έντονα brands, no-photo περιπτώσεις |
| `sidebar` | conversion rail | τεχνίτες και τοπικές υπηρεσίες |
| `grid` | Swiss structured | δικηγόρους, λογιστές, studios |
| `magazine` | newspaper layout | εστίαση, παραγωγούς, editorial brands |
| `warmth` | local hospitality | ταβέρνες, φούρνους, καφέ |
| `ember` | premium night food | εστιατόρια, ψησταριές, bars |
| `marble` | quiet luxury | ιατρούς και επαγγελματίες κύρους |
| `runway` | fashion portfolio | κομμωτήρια, beauty, fashion |
| `forge` | industrial trust | τεχνίτες και συνεργεία |
| `aegean` | destination hospitality | δωμάτια και τουρισμό |
| `bloom` | organic retail | καφέ, φούρνους, ανθοπωλεία |
| `volt` | high-energy | γυμναστήρια και trainers |
| `motor` | work-order visual language | συνεργεία αυτοκινήτων |
| `terra` | provenance/product label | παραγωγούς και αγροτικά brands |
| `dispatch` | immediate call conversion | επείγουσες τεχνικές υπηρεσίες |
| `canvas` | project-first catalogue | ξυλουργούς και ανακαινίσεις |

## Legacy compatibility

Τα `showcase`, `corporate`, `coast` και `pulse` παραμένουν renderable για υπάρχοντες πελάτες,
αλλά δεν εμφανίζονται πλέον στη δημόσια συλλογή και δεν προτείνονται από το backend.

## Photo modes

Το `sites/lib/mediaFallback.js` εφαρμόζει κοινό συμβόλαιο:

- `real`: πραγματικές φωτογραφίες πελάτη,
- `mixed`: πραγματικές μαζί με ενδεικτικές συμπληρωματικές,
- `no-photo`: profession-specific εικόνες μέχρι να ανεβάσει δικό του υλικό.

Οι συμπληρωματικές εικόνες δηλώνονται ως ενδεικτικές. Το preview mode δοκιμάζεται με:

```text
/preview/canvas?biz=carpenter&photos=none
```

## Smart matching

Η μοναδική production πηγή επιλογής είναι το `recommend_templates()` στο
`src/premium_generator.py`. Επιστρέφει τέσσερις επιλογές ανά vertical, με την πιο κατάλληλη πρώτη.
Παράδειγμα ξυλουργού: `canvas`, `editorial`, `split`, `bento`.

## Quality gate

```bash
cd sites
npm run dev
npm run audit:templates
npm run build
```

Το audit καλύπτει:

- desktop 1440 x 1024 και mobile 390 x 844,
- όλα τα 24 renderable templates για compatibility,
- mobile `no-photo` mode για τα 20 επίσημα,
- HTTP status, horizontal overflow, broken images και console errors,
- screenshots στο `sites/artifacts/template-audit/`.

Τελευταίο αποτέλεσμα: 68 browser runs, 0 issues.
