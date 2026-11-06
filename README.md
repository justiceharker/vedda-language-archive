# Vedda Language Archive

Every Vedda word four collectors wrote down between 1863 and 1972, rebuilt from the original
scans, with who recorded it, where, when, and on which page.

**786 distinct word forms · 816 rows · 4 sources · 12 named settlements**

**Browse and search it:** https://justiceharker.github.io/vedda-language-archive/

Vedda (ISO 639-3 `ved`) is the language of the Wanniyala-Aetto, the indigenous people of Sri
Lanka. UNESCO classifies it **Definitely Endangered**: roughly 300 native speakers by one
count, against ~2,500 people identifying as Vedda in 2002, of whom about 11% are conversant.

---

## ⛔ This is an archive, not a course, and the distinction is not cosmetic

- **No living speaker was consulted.** Nothing here is the language spoken at Dambana today.
- **There is no audio of Vedda in the public domain at all.** Two sentences of pronunciation
  guidance exist in the entire record: Parker's *"the letter c is pronounced like the English
  ch in church"* and Bailey's *"vowels to be pronounced as in Italian"*. Nothing else. No
  recording, no phonetic key, nothing to generate from.
- Most of the content is **colonial ethnography**: British observers describing a people they
  called primitive. That is a historical artefact, and the archive says so rather than
  presenting it as current usage.
- **Corrections from the Vedda community or from any university department are wanted** and
  will be credited. Nothing here is presented as settled.

Read [`RIGHTS.md`](RIGHTS.md) before adding a source or publishing anything built on this.

---

## The data

| File | Rows | What |
|---|---|---|
| `data/lexicon-parker.csv` | 248 | Parker 1909. Includes Sinhalese and Kaele-basa comparison columns |
| `data/lexicon-bailey.csv` | 97 | Bailey 1863. 61 rows carry his own etymological remark |
| `data/lexicon-seligmann.csv` | 429 | Seligmann 1911. **93% tagged with the settlement recorded in** |
| `data/lexicon-desilva.csv` | 42 | De Silva 1972 via ASJP, CC BY 4.0. ASJPcode, not a spelling |
| `data/cross-source.csv` | 39 | Glosses Parker and Bailey both recorded, scored |
| `data/uses-sinhalese.csv` | 20 | Meanings where Parker records **no** Vedda word |

Every row carries `source` and `page`. Seligmann rows carry `page_image`, a deep link to the
scan at archive.org, so any form can be checked against the original.

### Twelve settlements

Seligmann is the only source that records **where** each form was collected. The others show
the language varying across decades, this one across places.

`Dambani 129 · Bulugahaladena 117 · Kovil Vanamai 80 · Sitala Wanniya 52 · Bandaraduwa 44 ·
Wannaku of Uniche 43 · Lindegala 40 · Nilgala 37 · Rerenkadi 21 · Godatalawa 15 ·
Unuwatura Bubula 12 · Tamankaduwa 4`

**Dambani is Dambana**, the settlement the community still lives in, and it supplies more
recorded forms than anywhere else.

---

## Rebuild it

```bash
./fetch-sources.sh    # ~40 MB of scans into sources/ (gitignored)
./build.sh            # rebuilds every file in data/
```

Python 3, standard library only. No dependencies.

`site/index.html` is a self-contained viewer with the data embedded: searchable lexicon,
source filters, and a character-level comparison of the two Victorian word lists.

---

## Things that will bite you

**⛔⛔ Never parse `*_djvu.txt` from archive.org for a table.** The reading order is scrambled:
columns interleave and entries wrap, so a regex over it produces confident garbage that looks
correct. Parker and Bailey are rebuilt from **per-word coordinates** in `_djvu.xml`. Seligmann's
vocabulary is single-column, so its text layer is safe. That is a property of the page, not a
general rule.

**⛔⛔ Kaele-basa is not Vedda.** It sits in the column next to the Vedda one in Parker and is
the Kandyan Sinhalese hunters' taboo register, spoken by a different people imitating Veddas
while hunting. A naive four-column read publishes Sinhalese hunting words as Vedda.

**⛔ A blank is a meaning, not a gap.** Where Parker records no Vedda word, he states the Veddas
use the Sinhalese one. Those 20 meanings are in `uses-sinhalese.csv`, not discarded and not
rendered as unknowns.

**⚠️ Two thirds of "Parker" is Nevill's.** 163 of 248 rows carry his `N.` marker.

**⚠️ Transcription conventions are not lexical disagreement.** Bailey writes English-style
(`Doongah`, `Metchan`), Parker scholarly (`Dun-ga`, `Meccan`). A plain string comparison of the
39 shared glosses reports 13 disagreements and 11 are false. `cross-source.csv` folds the
conventions together before scoring, and the leftovers are labelled `unresolved`, never
"different words", because scan damage and real variation cannot be separated automatically.

**⚠️ Column geometry is fragile in three separate ways.** k-means on per-word x-coordinates
splits a dense column and merges two sparse ones, shifting every column by one; whole-page
whitespace gutters get bridged by long entries; "three widest gaps" picks a gap *inside* a
column. What works is fixed boundaries per page parity, each asserted to fall inside an
observed gap on every page; the build refuses otherwise.

**⚠️ Check the instrument before the code.** Several apparent defects here were the measuring
tool: `iterparse` with `el.clear()` on non-target elements wipes every word before the page's
end event; a curly quote (U+2019) renders as a replacement glyph in a Windows console and looks
like corruption; `Language_ID` is column index 2 in the ASJP CLDF, and index 1 returns zero rows
silently.

---

## Sources

- **Parker, H.** (1909) *Ancient Ceylon*. London: Luzac & Co., pp. 123-132.
- **Bailey, J.** (1863) *An Account of the Wild Tribes of the Veddahs of Ceylon*. Transactions
  of the Ethnological Society of London, vol. II, pp. 278-320.
- **Seligmann, C. G. & Seligmann, B. Z.** (1911) *The Veddas*. Cambridge University Press,
  Vedda Vocabulary pp. 423-451. *See `RIGHTS.md`: split status by jurisdiction.*
- **De Silva, M. W. S.** (1972) *Vedda language of Ceylon*. München: R. Kitzinger. Accessed
  only via **Wichmann, Holman, Brown, Dryer & Ran (eds.) 2025, The ASJP Database v21**,
  CC BY 4.0. The book itself is in copyright and is not used.

Compiled by **Harker International** (Sri Lanka).

---

## Licence

**The code** in `extract/` and the build scripts: MIT, see `LICENSE`.

**The data is not under a single licence.** It carries the rights of its sources, which differ.
`data/lexicon-desilva.csv` is CC BY 4.0 and its attribution must travel with it.
`data/lexicon-seligmann.csv` derives from a work still protected in the UK and Sri Lanka until
2036. Read [`RIGHTS.md`](RIGHTS.md) before redistributing any of it.
