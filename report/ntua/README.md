# Έκδοση ΕΜΠ / Artemis

| Αρχείο | Περιγραφή |
|--------|-----------|
| `main_ntua_final.pdf` | Τελικό PDF για υποβολή στο Artemis |
| `../main_ntua.tex` | Πηγαίος κώδικας LaTeX (μένει στο `report/` για σωστά paths) |
| `../frontmatter/ntua/` | Ελληνικά εξώφυλλα, Περίληψη, Εκτεταμένη Περίληψη, Πλαίσιο Εκπόνησης |

## Μεταγλώττιση

```bash
cd report
tectonic main_ntua.tex
cp main_ntua.pdf ntua/main_ntua_final.pdf
```

Η έκδοση UPC (`main.tex` / `main.pdf`) παραμένει ανέπαφη.
