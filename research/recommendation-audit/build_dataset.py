#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Χτίζει το σύνολο αξιολόγησης προτάσεων. ΝΤΕΤΕΡΜΙΝΙΣΤΙΚΟ, χωρίς AI.

    python research/recommendation-audit/build_dataset.py

Γράφει `dataset.json` δίπλα του.

ΑΠΟ ΠΟΥ ΒΓΑΙΝΕΙ Η ΛΙΣΤΑ ΕΠΑΓΓΕΛΜΑΤΩΝ. Όχι από φαντασία: από το
`premium_generator._VERTICAL_RULES`, που είναι η μοναδική πηγή που ξέρει η
παραγωγή. Αν κάποιο vertical δεν υπάρχει εκεί, δεν υπάρχει στο προϊόν και δεν
μπαίνει εδώ.

ΓΙΑΤΙ ΧΕΙΡΟΓΡΑΦΕΣ ΦΡΑΣΕΙΣ. Ο ρεαλισμός ζει στη γλώσσα, όχι στο πλήθος. Οι
βασικές διατυπώσεις ανά επάγγελμα γράφτηκαν στο χέρι, όπως θα τις έγραφε
ιδιοκτήτης· ο κώδικας κάνει μόνο τις μηχανικές παραλλαγές (τοποθεσία,
greeklish, ορθογραφικά). Έτσι το σύνολο μένει αναπαραγώγιμο ΚΑΙ αληθοφανές.
"""
from __future__ import annotations

import io
import json
import os
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("VITRINA_ENV", "staging")

from src import premium_generator as pg  # noqa: E402

# ── Τοποθεσίες. Μπαίνουν για να ΜΗΝ επηρεάζουν το επάγγελμα. ────────────────
# Μερικές είναι επίτηδες παγίδες: «Ψυρρή» και «Γκάζι» είναι περιοχές γεμάτες
# μπαρ, «Κολωνάκι» συνδέεται με μπουτίκ. Αν η τοποθεσία μετακινεί το vertical,
# αυτές θα το δείξουν.
CITIES = ["στη Γλυφάδα", "στο Χαλάνδρι", "στη Νέα Σμύρνη", "στον Πειραιά",
          "στο Περιστέρι", "στη Θεσσαλονίκη", "στο Κολωνάκι", "στου Ψυρρή",
          "στο Γκάζι", "στη Λάρισα", "στο Ηράκλειο", "στα Εξάρχεια"]

# ── Ανά επάγγελμα: πώς το λέει ο ίδιος ο ιδιοκτήτης ─────────────────────────
# `word`     : η σκέτη λέξη (σύντομη είσοδος)
# `plain`    : καθαρή δήλωση
# `natural`  : κουβεντιαστά, με λεπτομέρεια
# `indirect` : ΜΟΝΟ υπηρεσίες, χωρίς να πει το επάγγελμα — το δύσκολο σενάριο
# `brand`    : επωνυμία + επάγγελμα
# `mixed`    : ελληνικά + αγγλικά, όπως γράφουν πραγματικά
BUSINESSES: list[dict] = [
    # ---------------------------------------------------------------- beauty
    {"vertical": "beauty", "word": "κομμωτήριο",
     "plain": "Έχω κομμωτήριο",
     "natural": "Έχω ένα μικρό κομμωτήριο για γυναίκες",
     "indirect": "Κάνουμε balayage, βαφές και γυναικεία κουρέματα",
     "brand": "Maria Hair Studio, κομμωτήριο",
     "mixed": "Hair salon για βαφές και χτενίσματα"},
    {"vertical": "beauty", "word": "κουρείο",
     "plain": "Έχω κουρείο",
     "natural": "Παραδοσιακό κουρείο, δουλεύω μόνος μου εδώ και 15 χρόνια",
     "indirect": "Κουρέματα, ξύρισμα με ξυράφι και περιποίηση γενιού",
     "brand": "Barber House, κουρείο",
     "mixed": "Barber shop για ανδρικά κουρέματα και beard trim"},
    {"vertical": "beauty", "word": "νυχάδικο",
     "plain": "Έχω νυχάδικο",
     "natural": "Έχουμε ένα στούντιο νυχιών με τρεις θέσεις",
     "indirect": "Κάνουμε ημιμόνιμο, pedicure και σχέδια στα νύχια",
     "brand": "Nail Bar Elena, νύχια",
     "mixed": "Beauty salon για νύχια και lashes"},
    # ------------------------------------------------------------ aesthetics
    {"vertical": "aesthetics", "word": "αισθητικός",
     "plain": "Είμαι αισθητικός και έχω δικό μου χώρο",
     "natural": "Ινστιτούτο αισθητικής, δουλεύουμε δύο αισθητικοί",
     "indirect": "Κάνουμε αποτρίχωση με laser, καθαρισμό προσώπου και μεσοθεραπεία",
     "brand": "Derma Care, κέντρο αισθητικής",
     "mixed": "Beauty clinic για laser αποτρίχωση και facial"},
    # --------------------------------------------------------------- massage
    {"vertical": "massage", "word": "μασάζ",
     "plain": "Κάνω θεραπευτικό μασάζ",
     "natural": "Έχω έναν μικρό χώρο για μασάζ και χαλάρωση",
     "indirect": "Θεραπευτικό μασάζ πλάτης, αρωματοθεραπεία και reflexology",
     "brand": "Zen Spa, μασάζ",
     "mixed": "Wellness studio για massage και spa treatments"},
    # ---------------------------------------------------------------- bakery
    {"vertical": "bakery", "word": "φούρνος",
     "plain": "Έχω φούρνο",
     "natural": "Παραδοσιακός φούρνος με ξυλόφουρνο, ψήνουμε από τις 5 το πρωί",
     "indirect": "Ψήνουμε χωριάτικο ψωμί με προζύμι, τυρόπιτες και κουλούρια",
     "brand": "Ο Φούρνος του Γιάννη",
     "mixed": "Artisan bakery με προζύμι και sourdough"},
    {"vertical": "bakery", "word": "ζαχαροπλαστείο",
     "plain": "Έχω ζαχαροπλαστείο",
     "natural": "Οικογενειακό ζαχαροπλαστείο, τρίτη γενιά",
     "indirect": "Φτιάχνουμε τούρτες γενεθλίων, γλυκά ταψιού και σοκολατάκια",
     "brand": "Γλυκές Στιγμές, ζαχαροπλαστείο",
     "mixed": "Patisserie για τούρτες και handmade desserts"},
    # ------------------------------------------------------------------ cafe
    {"vertical": "cafe", "word": "καφετέρια",
     "plain": "Έχω καφετέρια",
     "natural": "Μικρή καφετέρια της γειτονιάς με έξι τραπέζια",
     "indirect": "Σερβίρουμε espresso, filter και brunch το Σαββατοκύριακο",
     "brand": "Coffee Point, καφετέρια",
     "mixed": "Specialty coffee shop με single origin"},
    # ------------------------------------------------------------------ food
    {"vertical": "food", "word": "ταβέρνα",
     "plain": "Έχω ταβέρνα",
     "natural": "Οικογενειακή ταβέρνα με μαγειρευτά και κρασί χύμα",
     "indirect": "Μαγειρεύουμε κατσικάκι στο φούρνο, γεμιστά και φρέσκα ψάρια",
     "brand": "Το Στέκι του Μανώλη, ταβέρνα",
     "mixed": "Greek taverna με traditional πιάτα"},
    {"vertical": "food", "word": "εστιατόριο",
     "plain": "Έχω εστιατόριο",
     "natural": "Εστιατόριο μεσογειακής κουζίνας, 40 θέσεις",
     "indirect": "Σερβίρουμε πιάτα ημέρας, κρασιά και επιδόρπια",
     "brand": "Elia Restaurant, εστιατόριο",
     "mixed": "Mediterranean restaurant με seasonal menu"},
    # --------------------------------------------------------------- dentist
    {"vertical": "dentist", "word": "οδοντιατρείο",
     "plain": "Έχω οδοντιατρείο",
     "natural": "Οδοντιατρείο με δύο γιατρούς και σύγχρονο εξοπλισμό",
     "indirect": "Κάνουμε λεύκανση, εμφυτεύματα και αόρατα σιδεράκια",
     "brand": "Dental Care Παπαδόπουλος, οδοντίατρος",
     "mixed": "Dental clinic για implants και ορθοδοντική"},
    # ---------------------------------------------------------------- doctor
    {"vertical": "doctor", "word": "ιατρείο",
     "plain": "Έχω ιατρείο",
     "natural": "Παθολογικό ιατρείο, δέχομαι με ραντεβού",
     "indirect": "Κάνουμε προληπτικό έλεγχο, καρδιογράφημα και εμβολιασμούς",
     "brand": "Ιατρείο Δρ. Αντωνίου",
     "mixed": "Private clinic για γενική ιατρική"},
    {"vertical": "doctor", "word": "φυσικοθεραπευτήριο",
     "plain": "Έχω φυσικοθεραπευτήριο",
     "natural": "Φυσικοθεραπευτής, δουλεύω με αθλητές και μετεγχειρητικά",
     "indirect": "Κάνουμε αποκατάσταση μετά από τραυματισμό και θεραπευτική άσκηση",
     "brand": "Physio Lab, φυσικοθεραπεία",
     "mixed": "Physiotherapy center για rehab και manual therapy"},
    # -------------------------------------------------------------- pharmacy
    {"vertical": "pharmacy", "word": "φαρμακείο",
     "plain": "Έχω φαρμακείο",
     "natural": "Φαρμακείο γειτονιάς, ανοιχτά και τα Σάββατα",
     "indirect": "Εκτελούμε συνταγές, έχουμε παραφαρμακευτικά και ορθοπεδικά",
     "brand": "Φαρμακείο Γεωργίου",
     "mixed": "Pharmacy με dermocosmetics"},
    # ---------------------------------------------------------- professional
    {"vertical": "professional", "word": "δικηγόρος",
     "plain": "Είμαι δικηγόρος",
     "natural": "Δικηγορικό γραφείο, ασχολούμαι με εμπορικό δίκαιο",
     "indirect": "Αναλαμβάνουμε συμβάσεις, εργατικές διαφορές και δικαστικές υποθέσεις",
     "brand": "Αντωνίου & Συνεργάτες, δικηγορικό γραφείο",
     "mixed": "Law firm για corporate και εργατικά"},
    {"vertical": "professional", "word": "λογιστής",
     "plain": "Είμαι λογιστής",
     "natural": "Λογιστικό γραφείο, εξυπηρετούμε μικρές επιχειρήσεις",
     "indirect": "Κάνουμε φορολογικές δηλώσεις, μισθοδοσία και ΦΠΑ",
     "brand": "Tax Office Παπαδάκη, λογιστικό γραφείο",
     "mixed": "Accounting office για bookkeeping και payroll"},
    # --------------------------------------------------------------- trade
    {"vertical": "trade", "word": "υδραυλικός",
     "plain": "Είμαι υδραυλικός",
     "natural": "Υδραυλικός, 24ωρη εξυπηρέτηση σε όλη την Αττική",
     "indirect": "Φτιάχνουμε διαρροές, θερμοσίφωνες και αποφράξεις",
     "brand": "Υδραυλικές Εργασίες Νίκος",
     "mixed": "Plumber για emergency διαρροές"},
    {"vertical": "trade", "word": "ηλεκτρολόγος",
     "plain": "Είμαι ηλεκτρολόγος",
     "natural": "Αδειούχος ηλεκτρολόγος, αναλαμβάνω και πιστοποιητικά ΔΕΗ",
     "indirect": "Κάνουμε ηλεκτρολογικές εγκαταστάσεις, πίνακες και φωτισμό",
     "brand": "Volt Service, ηλεκτρολόγος",
     "mixed": "Electrician για installations και smart home"},
    {"vertical": "trade", "word": "ανακαινίσεις",
     "plain": "Κάνω ανακαινίσεις σπιτιών",
     "natural": "Αναλαμβάνουμε ανακαινίσεις διαμερισμάτων με το κλειδί στο χέρι",
     "indirect": "Κάνουμε μπάνια, κουζίνες, ελαιοχρωματισμούς και πλακάκια",
     "brand": "Domus Ανακαινίσεις",
     "mixed": "Renovation company για full ανακαίνιση"},
    # ------------------------------------------------------------------ wood
    {"vertical": "wood", "word": "ξυλουργός",
     "plain": "Είμαι ξυλουργός",
     "natural": "Ξυλουργείο, φτιάχνω έπιπλα κατά παραγγελία",
     "indirect": "Κατασκευάζουμε ντουλάπες, κουζίνες και ξύλινες σκάλες",
     "brand": "Ξυλουργική Κουτράκης",
     "mixed": "Carpenter για custom έπιπλα και wood design"},
    # ---------------------------------------------------------------- garage
    {"vertical": "garage", "word": "συνεργείο αυτοκινήτων",
     "plain": "Έχω συνεργείο αυτοκινήτων",
     "natural": "Συνεργείο αυτοκινήτων, service και διαγνωστικός έλεγχος",
     "indirect": "Κάνουμε αλλαγή λαδιών, φρένα και ευθυγράμμιση",
     "brand": "Auto Service Σταθόπουλος",
     "mixed": "Car service για diagnostics και ελαστικά"},
    # ------------------------------------------------------------------- gym
    {"vertical": "gym", "word": "γυμναστήριο",
     "plain": "Έχω γυμναστήριο",
     "natural": "Γυμναστήριο 400 τετραγωνικών με ομαδικά προγράμματα",
     "indirect": "Κάνουμε προπονήσεις δύναμης, ομαδικά και personal training",
     "brand": "Iron Works Gym",
     "mixed": "Fitness studio για crossfit και HIIT"},
    {"vertical": "gym", "word": "πιλάτες",
     "plain": "Έχω στούντιο πιλάτες",
     "natural": "Στούντιο πιλάτες με reformer, μικρά γκρουπ",
     "indirect": "Κάνουμε reformer, mat και ενδυνάμωση κορμού",
     "brand": "Core Studio, πιλάτες",
     "mixed": "Pilates studio με reformer classes"},
    # ------------------------------------------------------------ realestate
    {"vertical": "realestate", "word": "μεσιτικό",
     "plain": "Έχω μεσιτικό γραφείο",
     "natural": "Μεσιτικό γραφείο, ασχολούμαι με πωλήσεις και ενοικιάσεις",
     "indirect": "Αναλαμβάνουμε πωλήσεις διαμερισμάτων και εκτιμήσεις ακινήτων",
     "brand": "Atlas Estate, μεσιτικό",
     "mixed": "Real estate agency για πωλήσεις και rentals"},
    # ----------------------------------------------------------------- rooms
    {"vertical": "rooms", "word": "ενοικιαζόμενα δωμάτια",
     "plain": "Έχω ενοικιαζόμενα δωμάτια",
     "natural": "Έχουμε οκτώ δωμάτια με θέα στη θάλασσα και πρωινό",
     "indirect": "Νοικιάζουμε δωμάτια με πρωινό, δίπλα στην παραλία",
     "brand": "Θαλασσιά Rooms",
     "mixed": "Boutique guesthouse με sea view δωμάτια"},
    # ---------------------------------------------------------------- retail
    {"vertical": "retail", "word": "κατάστημα ρούχων",
     "plain": "Έχω κατάστημα με ρούχα",
     "natural": "Μικρό κατάστημα με γυναικεία ρούχα και αξεσουάρ",
     "indirect": "Πουλάμε γυναικεία ρούχα, τσάντες και κοσμήματα",
     "brand": "Méra Boutique, ρούχα",
     "mixed": "Concept store με fashion και accessories"},
    # ------------------------------------------------------------------- pet
    {"vertical": "pet", "word": "pet shop",
     "plain": "Έχω pet shop",
     "natural": "Pet shop με τροφές και αξεσουάρ για σκύλους και γάτες",
     "indirect": "Πουλάμε τροφές για κατοικίδια και κάνουμε grooming σε σκύλους",
     "brand": "Happy Paws, pet shop",
     "mixed": "Pet shop για dog grooming και τροφές"},
    # ------------------------------------------------------------------ farm
    {"vertical": "farm", "word": "ελαιώνας",
     "plain": "Έχω ελαιώνα και παράγω ελαιόλαδο",
     "natural": "Οικογενειακός ελαιώνας, παράγουμε εξαιρετικό παρθένο ελαιόλαδο",
     "indirect": "Παράγουμε βιολογικό ελαιόλαδο και μέλι από δικά μας κτήματα",
     "brand": "Κτήμα Παπαδόπουλου, ελαιόλαδο",
     "mixed": "Family farm με organic ελαιόλαδο"},

    # ══ Δεύτερο κύμα: περισσότερα δείγματα στα επαγγέλματα του brief ═══════
    {"vertical": "beauty", "word": "κομμωτήριο ανδρικό",
     "plain": "Έχω ανδρικό κομμωτήριο",
     "natural": "Ανδρικό κομμωτήριο, δουλεύουμε με ραντεβού",
     "indirect": "Ανδρικά κουρέματα, fade και περιποίηση μαλλιών",
     "brand": "The Cut Room, ανδρικά κουρέματα",
     "mixed": "Men's grooming για haircut και styling"},
    {"vertical": "aesthetics", "word": "κέντρο ομορφιάς",
     "plain": "Έχω κέντρο ομορφιάς",
     "natural": "Κέντρο ομορφιάς με θεραπείες προσώπου και σώματος",
     "indirect": "Κάνουμε θεραπείες προσώπου, peeling και σύσφιξη",
     "brand": "Aurea Skin Studio, αισθητική",
     "mixed": "Skin clinic για anti-aging treatments"},
    {"vertical": "bakery", "word": "αρτοποιείο",
     "plain": "Έχω αρτοποιείο",
     "natural": "Αρτοποιείο με δικό μας προζύμι και καθημερινό ψήσιμο",
     "indirect": "Ψήνουμε ψωμιά ολικής, κριτσίνια και σφολιάτες",
     "brand": "Ζυμωτό, αρτοποιείο",
     "mixed": "Micro bakery με slow fermentation"},
    {"vertical": "cafe", "word": "καφεκοπτείο",
     "plain": "Έχω καφεκοπτείο",
     "natural": "Καφεκοπτείο, καβουρδίζουμε δικό μας καφέ κάθε βδομάδα",
     "indirect": "Καβουρδίζουμε κόκκους και σερβίρουμε espresso και φίλτρου",
     "brand": "Roast & Co, καφεκοπτείο",
     "mixed": "Coffee roastery με specialty beans"},
    {"vertical": "food", "word": "ψητοπωλείο",
     "plain": "Έχω ψητοπωλείο",
     "natural": "Ψητοπωλείο με σουβλάκι και delivery στη γειτονιά",
     "indirect": "Φτιάχνουμε σουβλάκια, γύρο και μερίδες σε πακέτο",
     "brand": "Ο Θανάσης, ψητοπωλείο",
     "mixed": "Souvlaki spot με delivery"},
    {"vertical": "dentist", "word": "ορθοδοντικός",
     "plain": "Είμαι ορθοδοντικός",
     "natural": "Ορθοδοντικό ιατρείο για παιδιά και ενήλικες",
     "indirect": "Βάζουμε σιδεράκια και διαφανείς νάρθηκες ευθυγράμμισης",
     "brand": "Smile Line, ορθοδοντική",
     "mixed": "Orthodontics για invisible aligners"},
    {"vertical": "doctor", "word": "παιδίατρος",
     "plain": "Είμαι παιδίατρος",
     "natural": "Παιδιατρικό ιατρείο, παρακολούθηση από τη γέννηση",
     "indirect": "Κάνουμε εμβολιασμούς, παρακολούθηση ανάπτυξης και συνταγογράφηση",
     "brand": "Ιατρείο Παιδιατρικής Δρ. Λάμπρου",
     "mixed": "Pediatric clinic για well-child visits"},
    {"vertical": "professional", "word": "σύμβουλος επιχειρήσεων",
     "plain": "Είμαι σύμβουλος επιχειρήσεων",
     "natural": "Σύμβουλος επιχειρήσεων, βοηθάω μικρές εταιρείες με χρηματοδοτήσεις",
     "indirect": "Αναλαμβάνουμε επιχειρηματικά σχέδια, ΕΣΠΑ και οργάνωση",
     "brand": "Nexus Consulting, σύμβουλοι",
     "mixed": "Business consulting για funding και strategy"},
    {"vertical": "trade", "word": "ελαιοχρωματιστής",
     "plain": "Είμαι ελαιοχρωματιστής",
     "natural": "Ελαιοχρωματιστής, βάφω σπίτια και καταστήματα",
     "indirect": "Βάφουμε εσωτερικούς χώρους, σοβατίζουμε και κάνουμε μονώσεις",
     "brand": "Χρώμα & Τέχνη, ελαιοχρωματισμοί",
     "mixed": "Painting services για interior και exterior"},
    {"vertical": "trade", "word": "ψυκτικός",
     "plain": "Είμαι ψυκτικός",
     "natural": "Τεχνικός κλιματισμού, τοποθετήσεις και συντηρήσεις",
     "indirect": "Τοποθετούμε κλιματιστικά και κάνουμε συντήρηση ψυκτικών",
     "brand": "Cool Tech, κλιματισμός",
     "mixed": "HVAC technician για installation και service"},
    {"vertical": "wood", "word": "επιπλοποιείο",
     "plain": "Έχω επιπλοποιείο",
     "natural": "Επιπλοποιείο, κατασκευάζουμε έπιπλα κατά παραγγελία",
     "indirect": "Φτιάχνουμε ντουλάπες, βιβλιοθήκες και τραπέζια μασίφ",
     "brand": "Moso Interior, έπιπλα",
     "mixed": "Furniture workshop για bespoke κατασκευές"},
    {"vertical": "garage", "word": "φανοποιείο",
     "plain": "Έχω φανοποιείο",
     "natural": "Φανοποιείο και βαφείο αυτοκινήτων",
     "indirect": "Επισκευάζουμε ζημιές αμαξώματος και βάφουμε αυτοκίνητα",
     "brand": "Body Shop Καρράς, φανοποιείο",
     "mixed": "Body shop για dent repair και βαφή"},
    {"vertical": "gym", "word": "σχολή πολεμικών τεχνών",
     "plain": "Έχω σχολή πολεμικών τεχνών",
     "natural": "Σχολή πολεμικών τεχνών με τμήματα παίδων και ενηλίκων",
     "indirect": "Κάνουμε προπονήσεις kick boxing και αυτοάμυνας",
     "brand": "Spartan Dojo, πολεμικές τέχνες",
     "mixed": "Martial arts academy για kickboxing"},
    {"vertical": "realestate", "word": "κτηματομεσιτικό",
     "plain": "Έχω κτηματομεσιτικό γραφείο",
     "natural": "Κτηματομεσιτικό γραφείο με εξειδίκευση σε εξοχικά",
     "indirect": "Πουλάμε και ενοικιάζουμε ακίνητα, με φωτογράφιση και εκτίμηση",
     "brand": "Villa Agency, ακίνητα",
     "mixed": "Property agency για holiday homes"},
    {"vertical": "rooms", "word": "ξενώνας",
     "plain": "Έχω ξενώνα",
     "natural": "Πέτρινος ξενώνας στο βουνό, ανοιχτά όλο τον χρόνο",
     "indirect": "Έχουμε δωμάτια με τζάκι και σερβίρουμε σπιτικό πρωινό",
     "brand": "Πέτρινο Αρχοντικό, ξενώνας",
     "mixed": "Mountain guesthouse με cozy δωμάτια"},
    {"vertical": "retail", "word": "βιβλιοπωλείο",
     "plain": "Έχω βιβλιοπωλείο",
     "natural": "Βιβλιοπωλείο γειτονιάς με ελληνική λογοτεχνία",
     "indirect": "Πουλάμε βιβλία, χαρτικά και είδη δώρου",
     "brand": "Σελίδες, βιβλιοπωλείο",
     "mixed": "Bookstore με literature και gifts"},
    {"vertical": "pharmacy", "word": "παραφαρμακείο",
     "plain": "Έχω παραφαρμακείο",
     "natural": "Παραφαρμακείο με καλλυντικά και συμπληρώματα",
     "indirect": "Πουλάμε συμπληρώματα διατροφής, βρεφικά και δερμοκαλλυντικά",
     "brand": "Vita Point, παραφαρμακείο",
     "mixed": "Parapharmacy για supplements και skincare"},

    # ══ ΔΙΦΟΡΟΥΜΕΝΑ: δύο εύλογες απαντήσεις. Κρίνονται με ανοχή. ══════════
    {"vertical": "massage", "word": "σπα", "ambiguous": ["aesthetics", "beauty"],
     "plain": "Έχω σπα",
     "natural": "Κέντρο ευεξίας με σάουνα, μασάζ και θεραπείες",
     "indirect": "Προσφέρουμε χαλαρωτικά μασάζ, σάουνα και θεραπείες σώματος",
     "brand": "Serenity Spa",
     "mixed": "Day spa για wellness και relaxation"},
    {"vertical": "cafe", "word": "καφέ μπαρ", "ambiguous": ["food"],
     "plain": "Έχω καφέ μπαρ",
     "natural": "Καφέ μπαρ, καφές το πρωί και ποτό το βράδυ",
     "indirect": "Σερβίρουμε καφέ, cocktails και μεζέδες",
     "brand": "Λωτός, καφέ μπαρ",
     "mixed": "Cafe bar με coffee και cocktails"},
    {"vertical": "retail", "word": "κάβα", "ambiguous": ["food"],
     "plain": "Έχω κάβα",
     "natural": "Κάβα με ελληνικά κρασιά και αποστάγματα",
     "indirect": "Πουλάμε κρασιά, ποτά και προϊόντα delicatessen",
     "brand": "Οίνος & Πνεύμα, κάβα",
     "mixed": "Wine shop με local κρασιά"},
]

# ── Greeklish: ντετερμινιστική μεταγραφή ────────────────────────────────────
GREEKLISH = {
    "θ": "th", "χ": "ch", "ψ": "ps", "ω": "o", "η": "i", "ξ": "x",
    "α": "a", "β": "v", "γ": "g", "δ": "d", "ε": "e", "ζ": "z", "ι": "i",
    "κ": "k", "λ": "l", "μ": "m", "ν": "n", "ο": "o", "π": "p", "ρ": "r",
    "σ": "s", "ς": "s", "τ": "t", "υ": "y", "φ": "f",
}


def strip_accents(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", text)
                   if unicodedata.category(c) != "Mn")


def to_greeklish(text: str) -> str:
    out = []
    for ch in strip_accents(text).lower():
        out.append(GREEKLISH.get(ch, ch))
    return "".join(out)


# ── Ορθογραφικά: τα λάθη που κάνει πραγματικά ο κόσμος ──────────────────────
# Χωρίς τόνους, διπλό σύμφωνο σε απλό, και η κλασική σύγχυση ι/η/υ.
TYPO_MAP = [("μμ", "μ"), ("ττ", "τ"), ("λλ", "λ"), ("σσ", "σ"),
            ("ω", "ο"), ("η", "ι"), ("υ", "ι"), ("ει", "ι"), ("αι", "ε")]


def add_typos(text: str) -> str:
    out = strip_accents(text).lower()
    for a, b in TYPO_MAP:
        out = out.replace(a, b)
    return out


def build() -> list[dict]:
    """Δέκα μορφές εισόδου ανά επιχείρηση, σύμφωνα με το brief."""
    rows: list[dict] = []
    qid = 0
    for i, biz in enumerate(BUSINESSES):
        city = CITIES[i % len(CITIES)]
        city2 = CITIES[(i + 5) % len(CITIES)]
        variants = [
            ("short", biz["word"]),
            ("clean", f"{biz['plain']} {city}"),
            ("natural", f"{biz['natural']} {city}"),
            ("indirect", f"{biz['indirect']} {city}"),
            ("brand", f"{biz['brand']}, {city.split()[-1]}"),
            ("mixed", f"{biz['mixed']} {city}"),
            ("greeklish", to_greeklish(f"{biz['plain']} {city}")),
            ("greeklish_natural", to_greeklish(f"{biz['natural']}")),
            ("typos", add_typos(f"{biz['plain']} {city}")),
            # Η τοποθεσία δεν επιτρέπεται να μετακινήσει το επάγγελμα. Δεύτερη
            # πόλη, επίτηδες «φορτισμένη» (Ψυρρή/Γκάζι/Κολωνάκι).
            ("location_noise", f"{biz['plain']} {city2}, κοντά στο μετρό"),
        ]
        for style, text in variants:
            qid += 1
            rows.append({
                "id": f"q{qid:04d}",
                "text": text,
                "style": style,
                "expected_vertical": biz["vertical"],
                # Διφορούμενα: δεύτερη εύλογη απάντηση, δεκτή χωρίς ποινή.
                "also_acceptable": biz.get("ambiguous", []),
                "business": biz["word"],
            })
    return rows


def main() -> None:
    known = {v for v, _ in pg._VERTICAL_RULES}
    rows = build()
    bad = sorted({r["expected_vertical"] for r in rows} - known)
    if bad:
        raise SystemExit(f"Vertical εκτός προϊόντος: {bad}")

    out = {
        "generated_from": "src/premium_generator._VERTICAL_RULES",
        "product_verticals": sorted(known),
        "verticals_covered": sorted({r["expected_vertical"] for r in rows}),
        "styles": sorted({r["style"] for r in rows}),
        "count": len(rows),
        "queries": rows,
    }
    path = HERE / "dataset.json"
    io.open(path, "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
    print(f"  ερωτήματα: {len(rows)}")
    print(f"  επαγγέλματα: {len(BUSINESSES)} · verticals: {len(out['verticals_covered'])}/{len(known)}")
    print(f"  μορφές εισόδου: {len(out['styles'])}")
    missing = sorted(known - set(out["verticals_covered"]))
    if missing:
        print(f"  ΧΩΡΙΣ ΚΑΛΥΨΗ: {missing}")
    print(f"  -> {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
