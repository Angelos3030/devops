# 19 — Πηγές & εργαλεία

Επιμελημένες συλλογές που αξίζουν για το Vitrina. Δεν είναι γενική λίστα —
δίπλα σε κάθε μία γράφω **τι θα λύσει σε εμάς** και **πού προσέχουμε**.

## Υποδομή με δωρεάν πλάνα

**[free-for-dev](https://github.com/ripienaar/free-for-dev)** — εκατοντάδες
υπηρεσίες με μόνιμα δωρεάν επίπεδα (hosting, βάσεις, email, monitoring, CDN).

Πού μας αφορά τώρα:
- **Email**: δεν στέλνουμε ακόμα τίποτα προγραμματικά. Όταν χρειαστεί (καλωσόρισμα
  πελάτη, υπενθύμιση ανανέωσης domain), εδώ βρίσκεις παρόχους με δωρεάν όγκο.
- **Monitoring**: κανείς δεν μας ειδοποιεί αν πέσει site πελάτη. Το μαθαίνουμε
  από τον πελάτη — δηλαδή αργά.

⚠️ Το «δωρεάν» έχει όριο. Πριν εξαρτηθούμε από κάτι, δες τι γίνεται στους 100
πελάτες, όχι στον έναν.

**[awesome-selfhosted](https://github.com/awesome-selfhosted/awesome-selfhosted)**
— ανοιχτές εναλλακτικές σε συνδρομές. Έχουμε ήδη μηχάνημα με στατική IP
(docs/16); αν κάποτε θέλουμε δικό μας n8n ή analytics, εκεί τρέχει.

## APIs

**[public-apis](https://github.com/public-apis/public-apis)** — 1.500+ δωρεάν API.

Ένα που **θα** μας χρειαστεί: αντίστροφη γεωκωδικοποίηση και δεδομένα τοποθεσίας.
Ήδη χρησιμοποιούμε Nominatim δωρεάν ([src/geocode.py](../src/geocode.py)).

## Claude Code

**[anthropics/skills](https://github.com/anthropics/skills)** — τα **επίσημα**
skills της Anthropic. Ασφαλή να μπουν κατευθείαν.

**[awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code)** ·
**[awesome-codex-skills](https://github.com/ComposioHQ/awesome-codex-skills)** ·
**[awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers)**

⚠️ **Κανόνας για ό,τι δεν είναι επίσημο:** τα skills, τα hooks και οι MCP servers
**εκτελούν κώδικα στο μηχάνημά μας**, με πρόσβαση σε ό,τι έχει και ο agent.
Αυτό το repo περιέχει **ζωντανά κλειδιά** (Supabase, Cloudflare, Railway,
Stripe, Meta, Pointer). Ένα κακόβουλο ή απλώς απρόσεκτο skill τα διαβάζει όλα.

Πριν μπει οτιδήποτε τρίτου:
1. Διάβασε τι τρέχει — όχι μόνο το README
2. Έλεγξε τι δικαιώματα ζητάει
3. Προτίμησε skills που μόνο *διαβάζουν* από αυτά που *εκτελούν*

**[system-prompts-and-models-of-ai-tools](https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools)**
— πώς είναι γραμμένες οι οδηγίες γνωστών AI εργαλείων. Χρήσιμο για τα δικά μας
prompts: τα κείμενα του `src/site_copy.py` και του `src/site_edit.py` είναι το
προϊόν, όχι διακόσμηση.

**[awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps)** —
100+ έτοιμες εφαρμογές AI για μελέτη.

**[awesome](https://github.com/sindresorhus/awesome)** — ο κατάλογος όλων των
καταλόγων.

---

## Τι ΔΕΝ λύνουν αυτά

Καμία από αυτές τις λίστες δεν φέρνει πελάτη. Το εμπόδιο του Vitrina σήμερα δεν
είναι τεχνικό — είναι ότι **κανείς δεν ξέρει ότι υπάρχουμε**. Χρήσιμα εργαλεία,
αλλά όχι υποκατάστατο για δέκα επισκέψεις σε μαγαζιά.
