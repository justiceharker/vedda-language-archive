> **Detailed extraction record**, kept verbatim from the original Phase 0 working notes.
> The [README](../README.md) is the summary; this is the long-form account of what was
> tried, what failed, and why, for Parker and Bailey. Rights live in
> [RIGHTS.md](../RIGHTS.md).

# Vedda Language Archive: corpus extraction (Phase 0)

Plan: `.claude/plans/can-we-do-a-clever-hopper.md`.

**Phase 0 was a go/no-go gate: does the public-domain record hold enough attested Vedda
vocabulary to justify an app at all? It does.**

| | |
|---|---|
| **Distinct Vaedi word forms** | **242** |
| Lexicon rows (form + gloss pairs) | 248 |
| English headwords covered | 129 |
| Attributed to Parker | 85 |
| **Attributed to Nevill, via Parker** | **163 (66%)** |
| Carrying a feminine form | 8 |
| Carrying a plural form | 4 |
| Carrying a grammatical note | 4 |
| Marked uncertain by Parker | 1 |
| Headwords with **no** Vaedi word recorded | 20 |
| Rows with OCR-suspect characters | **0** |

The gate floor was ~200 distinct items. **242 clears it from Parker alone**, before Bailey
1863 is opened and before the Seligmann 1911 copyright question is settled.

## Files

| File | What |
|---|---|
| `lexicon.csv` | One row per attested Vaedi form, with gloss, provenance, page |
| `uses-sinhalese.csv` | The 20 headwords where Parker recorded **no** Vaedi word |
| `extract_parker.py` | djvu.xml → column-reconstructed blocks (`parker_blocks.json`) |
| `normalise.py` | blocks → the two CSVs |

## Source

**Parker, H. (1909) _Ancient Ceylon: an account of the aborigines and of part of the early
civilization_. London: Luzac & Co.**, pp. 123-132. Henry Parker died 1926, so this is public
domain in every relevant jurisdiction. Scan: `archive.org/details/ancientceylonacc00park`.

Parker's table has four columns: `English | Sinhalese | Kaele-basa | Vaedi`.

---

## ⛔⛔ Kaele-basa is NOT Vedda, and merging it would corrupt the entire archive

Parker states plainly what it is: the Kandyan Sinhalese and the Wanniyas *"apparently imitate
the Vaeddas while they are hunting"* and use *"another series of expressions or nicknames"*.
It is a **Sinhalese hunters' taboo register**, spoken by a different people, sitting in the
column immediately left of the Vedda one.

`lexicon.csv` takes the **`vaedi` column only**. `kaele_basa_cf` and `sinhalese_cf` are
carried as **labelled comparison** and must never be promoted into the Vedda field. A naive
four-column read publishes Sinhalese hunting words as Vedda.

## ⭐ 66% of this vocabulary is not Parker's, and the source says so

Parker: *"Where the letter N is suffixed the word is taken from Mr. Nevill's writings."*

That `N.` is a **second collector**, not a dialect tag: Hugh Nevill (1848-1897). **163 of 248
rows carry it.** So one book yields two collectors, and every row records which. Do not strip
the marker, and do not describe the whole set as "Parker's word list".

## ⛔ A blank Vaedi cell is a MEANING, not missing data

Parker: *"In the cases where no word is given in the Vaedi dialect or Kaele-basa, both the
Vaeddas and other hunters employ colloquial Sinhalese words, often slightly altered in
pronunciation by the Vaeddas, as by using c for s."*

So the 20 blanks say **"they use the Sinhalese word"**. They are in `uses-sinhalese.csv`, not
discarded, and they must never be rendered as a gap or an unknown. This is the same
zero-versus-blank distinction the bond ledger documents, except here the source resolves it.

## The only pronunciation guidance that exists, quoted not invented

Parker: *"in these lists the letter c is pronounced like the English ch in church."*

That is the **entire** phonetic record available. There is no audio in the public domain at
all. Quote this line and attribute it; never generate a pronunciation.

## Parker rates his own coverage, and it is a floor

Parker: *"The Vaedi vocabulary which I append is extremely deficient, but that of the
Kaele-basa is nearly complete."*

The author states the asymmetry himself. Every count here is a **floor**, and the app must
say so. Note the irony worth publishing: the coloniser's record of the Sinhalese hunters'
imitation of Vedda speech is more complete than its record of Vedda speech.

## ⭐ Parker takes a position on the classification debate, in 1909

> *"The Vaedi dialect is to a great extent the colloquial Sinhalese tongue, but is slightly
> changed in form and accent... a very few may possibly belong to, or be modifications of
> words in, their original language."*

The creole-versus-isolate question does not have to be imported from modern scholarship and
hedged. The primary source argues it, and the `sinhalese_cf` column on every row is the
evidence sitting right there.

---

## How the extraction works, and the traps

**⛔⛔ NEVER PARSE `ancientceylonacc00park_djvu.txt`.** Its reading order is scrambled: the
four columns interleave and entries wrap, so a regex over it produces confident garbage that
looks fine. Everything here is reconstructed from **per-word coordinates** in
`ancientceylonacc00park_djvu.xml`.

Four things that were tried and failed, recorded so nobody repeats them:

1. **⛔ k-means on per-WORD x0: WRONG, and it fails silently.** The Vaedi column is dense and
   wide, so k-means split it in two and merged English with Sinhalese, shifting **every column
   by one**. The output looked plausible. The tell was `Ant-eater | Kaballaya` landing in a
   single cell.
2. **⛔ Whole-page whitespace gutters: fails on 2 of 8 pages.** Long entries and centred
   section headings bridge the gutters; leaves 163 and 164 yield no clean gutter at all.
3. **⛔ "Three widest gaps per page": fails on leaf 160**, where a gap *inside* the Vaedi
   column is wider than the real Sinhalese/Kaele-basa separator.
4. **✅ What works: the OCR emits every table CELL as its own `<LINE>`**, so a line's
   first-word x0 is the cell's left edge and quantises cleanly. Column boundaries are fixed
   per **page parity** (recto/verso margins differ by ~90px) and **every boundary is asserted
   to fall inside an observed whitespace gap on every page**; the build refuses otherwise.

Two more that produced real, visible corruption:

- **⚠️⚠️ Cells on one visual row jitter by ~10px in y, so a strict y-sort pushes them across
  headword boundaries.** `Bear`'s Sinhalese `Walaha` (y=875) sorts *before* `Bear` (y=876) and
  attached itself to the previous headword, `Axe-man`. Cells are clustered into **rows**
  first (tolerance 20px against a 35-45px line pitch), then read left to right.
- **⚠️ A headword's continuation cells run past the page break.** The open headword is carried
  across leaves; resetting it per page orphaned 17 cells.

Two more found only by inspecting the output:

- **⚠️ The English column wraps too**, so `Stage (of jour-` + `ney)` and
  `Monkey (Sem-` + `nopithecus)` each became a **separate headword**, splitting one concept in
  two and mis-glossing every Vaedi form beneath it. 32 blocks were affected. Wrapped cells are
  now merged on hyphen, open-paren depth, and lowercase continuation. The fix validates
  itself: the genus names come back as real taxa (`Varanus`, `Semnopithecus`, `Lobivanellus`).
- **⚠️ Parker's page FOOTNOTES sit in the same column and wrap as well.** Dropping only a
  footnote's first line left its tail to be absorbed as a continuation, so
  `Shoot (with arrow), to` silently acquired *"particle kadawa would thus mean 'never'"*.
  A footnote and all of its continuation lines are dropped together.

**⚠️⚠️ And one "defect" that was the instrument, not the data.** A headword reading
`' Iguana ? ( Varanus )` looked corrupted. The character is **U+2019**, an ordinary curly
quote, rendered as a replacement glyph by the Windows console. Checking the codepoints before
"fixing" it is the only reason correct data was not mangled. Same lesson this repo already
records for measuring em-dashes on bytes.

Smaller ones, all handled: OCR renders `f.` as `/.` and `pl.` as `pi.`; hyphen-wrapped words
split across cells (`Bumbaeli-` + `maessa`); `,,` ditto headwords inherit their parent
(`,, humble` under `Bee, honey` → `Bee, humble`); grammatical notes span several cells and
must be merged on **paren depth** before any comma split, or `Go, to` shreds into fragments.

## Reproduce

```bash
curl -sL https://archive.org/download/ancientceylonacc00park/ancientceylonacc00park_djvu.xml -o parker.xml
python extract_parker.py     # -> parker_blocks.json   (asserts column geometry)
python normalise.py          # -> lexicon.csv, uses-sinhalese.csv
```

---

# Source 2: Bailey 1863, and the cross-source view

**Bailey, J. (1863) _An Account of the Wild Tribes of the Veddahs of Ceylon_**, Transactions
of the Ethnological Society of London, vol. II, pp. 278-320. Vocabulary appendix on
pp. 314-318 (leaves 338-342 of `archive.org/details/transactionseth01londgoog`). John Bailey
died 1888, so it is public domain outright.

| | |
|---|---|
| Bailey lexicon rows | 97 |
| Distinct Veddah forms | 97 |
| English glosses | 75 |
| **Rows carrying Bailey's own etymological remark** | **61** |
| **COMBINED distinct forms, both sources** | **328** |

Bailey's table is **four columns: `English | Veddah | Singhalese | Remarks`**, and the
Remarks column is the reason this source is worth more than its row count. It is Bailey's own
analysis, per word:

> Lightning, Veddah *Ginna wetunu*: *"'Gini wetunu' (Singh.), fallen fire."*
> Thunder, Veddah *Dewōla andapi*: *"'Dewōla' (Singh.), a spirit, a demon, a god; 'andapi'
> (Singh.), has cried out."*

That is the **periphrasis** Bailey describes in his prose: *"to walk is 'to beat the ground
with hammers'; a child is 'a bud'; an elephant is 'a beast like a mountain'"*, documented
word by word rather than merely asserted.

## ⭐ A second pronunciation note, and it is the only other one in existence

Bailey heads his list: **"(Vowels to be pronounced as in Italian.)"**

With Parker's *"the letter c is pronounced like the English ch in church"*, that is now the
**complete** phonetic record available from the public domain. Two lines, from two collectors,
46 years apart. Quote both, attribute both, invent nothing beyond them.

## ⭐⭐ The cross-source view, which is what needed a second source

`cross-source.csv`. **39 English glosses appear in both Parker and Bailey.**

| Verdict | Count |
|---|---|
| Same word, same spelling | **28** |
| Same word, different transcription | 3 |
| **Unresolved** | **8** |

Several agreements are *character-identical* across two books, two scans, two OCR runs and 46
years: **`Ehna`** (cold), **`Bilinda`** (child), **`Minna`** (man), **`Bimi`** (earth), plus
near-identical `Ira-pojja`/`Irra podja` (sun) and `Araci`/`Arachi` (bear).

**⭐ That convergence is also the strongest available check on the extraction itself.** Two
independent column reconstructions, from differently-laid-out tables in different books,
cannot both be column-shifted and still agree on 28 of 39 glosses. It validates the geometry
work in a way no internal assertion can.

**⚠️⚠️ A NAIVE STRING COMPARISON REPORTS 13 DISAGREEMENTS AND ELEVEN OF THEM ARE FALSE.**
Bailey writes Veddah in **English spelling conventions** and Parker in a **scholarly** one:

| Gloss | Parker 1909 | Bailey 1863 |
|---|---|---|
| bow | `Dun-ga` | `Doongah` |
| hair | `Ica-Kola` | `Eecha kola` |
| honey | `Meccan` | `Metchan` |

`tch`/`c`, `oo`/`u`, `ee`/`i`, a decorative final `-h`. Publishing that as "the sources
disagree" would report **our own matching method** as a fact about the language. The
comparison folds the two conventions together before scoring, and says which test each row
passed.

**⛔ The 8 remaining rows are labelled `unresolved`, NOT "different words".** Some are plainly
scan damage (`GiDna` for `Ginna`, `DewQ5la` for `Dewōla`, both of which then match Parker);
others (monkey, pig, snake, sky, here) may be real lexical variation between communities and
decades. **Nothing here can separate the two automatically, so nothing claims to.** Deciding
would be a false merge of exactly the kind the vessel-attribution tool refuses 69 times.

## ⛔ Bailey's two categories, and the names appendix that is NOT vocabulary

Bailey states he distinguishes words *"which probably differ from the Singhalese"* from those
*"which, though Singhalese, are, in the sense here used, peculiar to the Veddahs."* Where his
Veddah and Singhalese columns carry the same form, `same_as_singhalese` flags it rather than
publishing it as a distinct Vedda word.

**⚠️⚠️ pp.318-319 carry a SECOND appendix, "SPECIMENS OF VEDDAH NAMES": personal names with
etymologies (Oodira, Buduwa, Nanga, Pusamittya...), not vocabulary.** It is excluded. This
heading also caused a real bug: the extractor's start marker matched bare `SPECIMEN`, so
`SPECIMENS OF VEDDAH NAMES` on p.318 truncated that page's word list to nothing and the
boundary assertion fired. The marker now matches `SPECIMEN OF VEDDAH DIAL` specifically, and
the names heading is used as the **end** boundary it actually is.

## ⚠️ Two more instrument failures, both mine

- **`iterparse` with `el.clear()` on non-target elements destroys the words before the parent
  page's end event fires.** Every page came back empty and it looked like the file had no
  text, in a file that demonstrably contains 236 instances of "Veddah". Clear only the pages
  you have finished with.
- p.314 carries **the end of the prose paper above the table and footnotes below it**, both in
  the English column. Gating on Bailey's own heading plus a gloss-length rule (a real English
  gloss is short) removes them; without it, sentence fragments entered the lexicon as
  headwords.

---

## Still open

- **Seligmann & Seligmann 1911** is jointly authored and **Brenda Z. Seligman died 1965**, so a
  life-plus-70 jurisdiction runs to ~2036. Public domain in the US on 1911 publication.
  Unresolved; do not treat "it is on archive.org" as permission.
- **The 8 unresolved cross-source rows** want a human eye on the page images to separate scan
  damage from real variation. That is a reading task, not a code task.
- **Bailey's personal-names appendix** (pp.318-319) is extracted but unused. It is a different
  kind of record and would need its own framing.
- **Tennent 1859** remains a context citation only.
