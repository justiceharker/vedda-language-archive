# -*- coding: utf-8 -*-
r"""De Silva 1972, obtained legitimately via the ASJP Database.

*** The book itself is IN COPYRIGHT and nothing is taken from it. ***

De Silva, M. W. Sugathapala (1972) 'Vedda language of Ceylon', Munchen:
R. Kitzinger, is the authoritative modern lexicon and remains protected.
But 42 of its forms are already redistributed under CC BY 4.0 by:

  Wichmann, S., Holman, E. W., Brown, C. H., Dryer, M. S. & Ran, Q. (eds.)
  2025. The ASJP Database, version 21.  https://asjp.clld.org

ASJP names De Silva 1972 as the source of the Vedda wordlist (bib key 10991,
verified in the CLDF sources.bib) and licenses its own release CC BY 4.0
(verified in cldf/cldf-metadata.json). Wordlist compiled by Viveka Velupillai.
So this is De Silva's data through a licensed channel, with attribution, and
the book is never opened.

*** ASJPcode is NOT a spelling. ***
It is a deliberately reduced ASCII phonetic alphabet: 3 = schwa, E = open-mid
front vowel, C = the 'ch' affricate, ~ = nasalisation, doubled letters = length.
NEVER character-diff these forms against Parker's or Bailey's romanisations;
the comparison would be meaningless while looking rigorous.

Notes for anyone re-running this:
  - The CLLD web API does NOT work. /words?format=json returns 404 and
    /values?...&format=json returns HTML. Use the CLDF release on GitHub.
  - Language_ID is column index 2. Index 1 is Local_ID, and filtering on it
    silently returns zero rows.
"""
import csv, io, os, sys, urllib.request

FORMS = 'https://raw.githubusercontent.com/lexibank/asjp/master/cldf/forms.csv'
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
BUILD = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'build')

SOURCE = ('De Silva, M. W. Sugathapala (1972) Vedda language of Ceylon. '
          'Munchen: R. Kitzinger - redistributed in Wichmann, Holman, Brown, '
          'Dryer & Ran (eds.) 2025, The ASJP Database v21, CC BY 4.0')
LICENCE = ('CC BY 4.0 (ASJP redistribution). The 1972 book itself remains in copyright.')
SYSTEM = 'ASJPcode (NOT a spelling; 3=schwa, E=open-mid front, C=ch, ~=nasal)'


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(BUILD, exist_ok=True)
    print('streaming ASJP forms.csv (~569k rows) and keeping Language_ID == VEDDA ...')
    req = urllib.request.Request(FORMS, headers={'User-Agent': 'vedda-language-archive/1.0'})
    rows, total = [], 0
    with urllib.request.urlopen(req, timeout=900) as resp:
        r = csv.reader(io.TextIOWrapper(resp, encoding='utf-8', errors='replace'))
        hdr = next(r)
        i_lang = hdr.index('Language_ID')          # index 2, NOT 1
        i_form = hdr.index('Form')
        i_gloss = hdr.index('gloss_in_source')
        i_param = hdr.index('Parameter_ID')
        for row in r:
            total += 1
            if len(row) > i_lang and row[i_lang] == 'VEDDA':
                rows.append({
                    'english': row[i_gloss],
                    'vedda_asjpcode': row[i_form],
                    'concept': row[i_param],
                    'transcription_system': SYSTEM,
                    'attributed_to': 'De Silva 1972, via ASJP',
                    'source': SOURCE,
                    'licence': LICENCE,
                })
    if not rows:
        sys.exit('REFUSING: zero VEDDA rows. Check the Language_ID column index.')
    if len(rows) < 30:
        sys.exit('REFUSING: only %d rows; expected ~42. Upstream may have changed.' % len(rows))

    with open(os.path.join(OUT, 'lexicon-desilva.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print('rows streamed        : %d' % total)
    print('VEDDA forms kept     : %d' % len(rows))
    print('distinct glosses     : %d' % len({r['english'] for r in rows}))
    print('written              : data/lexicon-desilva.csv')


if __name__ == '__main__':
    main()
