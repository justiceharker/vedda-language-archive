# Rights

**Read this before adding a source, publishing a dataset, or shipping anything built on it.**

This repository holds four sources with four different rights positions. They are not
interchangeable and there is no blanket licence over `data/`.

---

## The rule the whole repository is built on

**A word and its meaning is a fact, and facts are not copyrightable in any jurisdiction.**
What copyright protects is the *compilation*, its *arrangement*, and the *expressive prose*.
No UK or EU database right applies to any of these sources either: that right covers databases
made after 1983 and lasts fifteen years.

Every extractor here is drawn along that line deliberately:

| | |
|---|---|
| **Taken** | attested forms, English glosses, locality codes, cited cognates, per-entry provenance |
| **Not taken** | etymological derivations, analytical passages, running prose |
| **Not copied** | any source's own arrangement; rows merge into our concept scheme |
| **Linked instead** | page images at the hosting institution, so readers reach the original |

---

## Source by source

### Parker, H. (1909) *Ancient Ceylon*. London: Luzac & Co.
**Public domain everywhere.** Henry Parker died 1926.
Scan: `archive.org/details/ancientceylonacc00park`.

⚠️ The `Vaedi` column only. The adjacent **`Kaele-basa` column is not Vedda**: it is the Kandyan
Sinhalese hunters' taboo register, spoken by a different people. It is carried as labelled
comparison and must never be merged into the Vedda field.

⚠️ 163 of 248 rows carry Parker's `N.` marker, which he defines as "taken from Mr Nevill's
writings": Hugh Nevill (1848-1897), a **second collector**. Do not describe the set as
"Parker's word list".

### Bailey, J. (1863) *An Account of the Wild Tribes of the Veddahs of Ceylon*
Transactions of the Ethnological Society of London, vol. II, pp. 278-320.
**Public domain everywhere.** John Bailey died 1888.
Scan: `archive.org/details/transactionseth01londgoog`.

Bailey's `Remarks` column is his own etymological analysis and is reproduced because the work
itself is out of copyright.

### Seligmann, C. G. & Seligmann, B. Z. (1911) *The Veddas*. Cambridge University Press
**⚠️ SPLIT STATUS. Handle with care.**

| Jurisdiction | Rule | Free from |
|---|---|---|
| United States | Published 1911; maximum term 95 years from publication, and URAA restoration cannot extend beyond that | **already public domain** |
| United Kingdom | CDPA 1988 s.12(2), s.12(8): 70 years from the end of the year the last known author died | **1 January 2036** |
| Sri Lanka | Intellectual Property Act No. 36 of 2003, s.13: life + 70, from the last surviving author for joint works | **1 January 2036** |

**Joint authorship is confirmed from the title page**, not from a catalogue record: *"BY
C. G. SELIGMANN, M.D. ... AND BRENDA Z. SELIGMANN, WITH A CHAPTER BY C. S. MYERS, M.D., D.Sc.
AND AN APPENDIX BY A. MENDIS GUNASEKARA, Mudaliar."* This is load-bearing: if the book were
C. G. Seligmann's alone (d. 1940) it would have been public domain since 2011.

**Brenda Zara Seligman died 2 January 1965**, per the Pitt Rivers Museum (which holds the Seligman
collection) and Wikipedia. ⚠️ JISC ArchivesHub records "d 1960" and is an outlier.

⚠️ **Name-spelling trap.** The 1911 title page reads **SELIGMANN**, two n's. In later life both
used **Seligman**. Catalogue searches disagree because of it, which is why some records name
only C. G. as author.

⚠️⚠️ **US public-domain status does not travel.** Copyright is territorial. Publishing as a US
company from US hosting clears the extraction and US distribution; it does **not** by itself
clear making the work available in the UK or Sri Lanka. That is why `extract_seligmann.py` is
limited to facts rather than relying on jurisdiction, and why every row deep-links the page
image on archive.org instead of serving a copy.

⛔ **"Fair use" is not available here.** It is a US-only doctrine, and in the US this book is
already public domain so no defence is needed. The UK and Sri Lanka have *fair dealing*, a
closed list of purposes; the quotation exception (CDPA s.30(1ZA)) requires the extent be "no
more than is required by the specific purpose", which a whole vocabulary fails.

**The clean route to full clearance is a permissions request to Cambridge University Press**
(PLSClear, or permissions@cambridge.org). CUP grants short extracts freely and is an STM
Guidelines signatory. **Not yet sent.** If it is granted, this section should be rewritten and
the derivations become usable.

### De Silva, M. W. Sugathapala (1972) *Vedda language of Ceylon*. München: R. Kitzinger
**⛔ IN COPYRIGHT. Nothing is taken from the book, and nothing may be.**

The 42 forms in `data/lexicon-desilva.csv` come from the **ASJP Database v21** (Wichmann,
Holman, Brown, Dryer & Ran, eds., 2025), which redistributes them under **CC BY 4.0** and names
De Silva 1972 as their source (bib key `10991`, verified in ASJP's `sources.bib`; licence
verified in `cldf/cldf-metadata.json`). Wordlist compiled by Viveka Velupillai.

Attribution is required and travels with the data.

⚠️ These forms are **ASJPcode**, not a spelling: `3` = schwa, `E` = open-mid front vowel,
`C` = the *ch* affricate, `~` = nasalisation. Never character-diff them against the
romanisations in the other sources.

### Tennent, J. E. (1859) *Ceylon*
Public domain, and **measured: not a vocabulary source.** Nineteen mentions of Vedda in 1.5 MB
of text. Cite for context only; do not plan a lexicon around it.

---

## Standing obligations

1. **Every published row carries its source and page.** No unattributed forms, ever.
2. **No source's arrangement is republished as a standalone list.**
3. **The community was not consulted.** Nothing here is current speech, and no surface may
   imply otherwise. Corrections from the Vedda community or any university are wanted and
   will be credited.
4. **If CUP grants permission, update this file before using anything new.**
