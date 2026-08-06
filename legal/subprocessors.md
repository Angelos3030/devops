# Vitrina — Subprocessor Register

Πριν το production συμπληρώνονται ακριβής νομική οντότητα παρόχου, υπηρεσία,
τοποθεσία/region, DPA URL, μηχανισμός διαβίβασης και ημερομηνία ελέγχου.

| Πάροχος | Σκοπός | Δεδομένα | Έλεγχος πριν launch |
|---|---|---|---|
| Supabase | Database, storage, auth | account, business, assets, tokens | Region, DPA, backups, RLS |
| Railway | API hosting | request metadata, runtime data | Region, DPA, logs, retention |
| Cloudflare | DNS/CDN/security | IP, request metadata | DPA, logs, proxy settings |
| Stripe | Payments/subscriptions | billing and transaction data | DPA, retention, portal |
| Meta | OAuth/publishing | identifiers, tokens, content | Platform terms, permissions |
| Anthropic | AI content generation | prompt/business content | DPA, retention, training setting |
| GitHub | Source/CI | code and CI logs | secrets, access, retention |

Δεν στέλνουμε access tokens, service-role keys ή μη αναγκαία προσωπικά δεδομένα
σε AI prompts.

