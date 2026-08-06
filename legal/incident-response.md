# Vitrina — Personal Data Incident Runbook

1. **Contain:** ανάκληση keys/tokens, περιορισμός πρόσβασης, διατήρηση αποδεικτικών.
2. **Record:** ώρα γνώσης, συστήματα, δεδομένα, υποκείμενα, πιθανές συνέπειες.
3. **Assess:** confidentiality/integrity/availability και κίνδυνος για δικαιώματα.
4. **Notify controllers:** αν η Vitrina είναι processor, χωρίς αδικαιολόγητη καθυστέρηση.
5. **Authority:** ο controller γνωστοποιεί στην αρμόδια αρχή εντός 72 ωρών όταν
   είναι πιθανός κίνδυνος. Καταγράφεται και η αιτιολογία μη γνωστοποίησης.
6. **Individuals:** ενημέρωση όταν υπάρχει υψηλός κίνδυνος, εκτός νόμιμης εξαίρεσης.
7. **Recover:** ασφαλής επαναφορά, rotation όλων των επηρεαζόμενων credentials.
8. **Review:** root cause, διορθώσεις, owner και deadline. Το incident log δεν διαγράφεται.

Emergency owner και στοιχεία επικοινωνίας συμπληρώνονται πριν το production launch.
