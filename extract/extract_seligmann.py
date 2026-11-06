# -*- coding: utf-8 -*-
r"""Seligmann, C. G. & Seligmann, B. Z. (1911) 'The Veddas', Cambridge UP,
Vedda Vocabulary, pp.423-451.

*** COPYRIGHT POSTURE - read before changing anything here. ***

The book is PUBLIC DOMAIN IN THE UNITED STATES (published 1911; the maximum US
term is 95 years from publication, so it expired in 2006, and URAA restoration
cannot extend beyond that). It remains in copyright in the UK and Sri Lanka
until 1 January 2036, because it is a work of joint authorship and Brenda Z.
Seligmann died 2 January 1965.

Copyright is territorial, so US public-domain status does NOT clear worldwide
distribution. This extractor is therefore deliberately limited to what is
defensible in EVERY jurisdiction:

  TAKEN      - the attested Vedda word forms, their English gloss, the locality
               codes attached to each form, and the Sinhalese cognate the
               entry cites. These are FACTS. Facts are not copyrightable
               anywhere. (No UK/EU database right applies either: that covers
               databases made after 1983 and runs only 15 years.)

  NOT TAKEN  - Gunasekara's etymological derivations and every other analytical
               or prose passage. That is the expressive content and it is the
               part copyright actually protects. The parser cuts each entry at
               the first derivation marker and keeps only the head.

  NOT COPIED - Seligmann's arrangement. Rows are merged into OUR concept scheme
               beside Parker, Bailey and De Silva, never published in his order
               as a standalone list.

  LINKED     - every row carries a deep link to the page image on archive.org,
               which already hosts the scan lawfully as a US public-domain work.
               The reader is sent to the original rather than served a copy.

Unlike Parker and Bailey, this vocabulary is SINGLE-COLUMN, so the plain text
layer reads in the correct order and no coordinate reconstruction is needed.
"""
import csv, json, os, re, io
import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
SRC_DIR = _os.path.join(_ROOT, 'sources')
BUILD_DIR = _os.path.join(_ROOT, 'build')


SRC = SRC_DIR + '/selig.txt'
START, END = 25806, 27412          # pp.423-451, ends where the Appendix begins
FIRST_PAGE = 423
# leaf = printed page + 182, DERIVED from the scan's own scandata.xml
# (p.423 -> leaf 605, p.425 -> leaf 607), never guessed.
IA = 'https://archive.org/details/veddas__00seliuoft/page/n{leaf}'
LEAF_OFFSET = 182

# From the vocabulary's own ABBREVIATIONS table, p.423.
LOCALITY = {
    'B': 'Bandaraduwa', 'Bl': 'Bulugahaladena', 'D': 'Dambani',
    'G': 'Godatalawa', 'K': 'Kovil Vanamai', 'L': 'Lindegala',
    'N': 'Nilgala', 'O': 'Wannaku of Uniche', 'R': 'Rerenkadi',
    'Tk': 'Tamankaduwa', 'U': 'Unuwatura Bubula', 'W': 'Sitala Wanniya',
}
REGISTER = {
    'Fl': 'Kaelebasa (jungle language, NOT Vedda)',
    'Tf': 'threshing-floor language',
    'Y': 'Yaka (spirit) language',
}
LANG = {'S', 'O.S', 'P', 'Port', 'Sk', 'T', 'Tel', 'H', 'Hind', 'M', 'Mal'}

# A derivation begins at one of these. Everything from here on is Gunasekara's
# analysis and is deliberately discarded.
CUT = re.compile(
    r'\s(?:from|perhaps|probably|apparently|cf\.|v\.\s*supra|v\.\s*p\.|possibly|'
    r'lit\.|connected with|derived from|the same as|said to|means)\b', re.I)


def load_entries():
    lines = io.open(SRC, encoding='utf-8', errors='replace').read().split('\n')
    span = lines[START:END]
    # drop running heads / page numbers, and record the page as we pass them
    entries, cur, page = [], None, FIRST_PAGE
    for ln in span:
        s = ln.strip()
        if not s:
            continue
        m = re.match(r'^(\d{3})\s+VEDDA\s+VOCABULARY$|^VEDDA\s+VOCABULARY\s+(\d{3})$', s)
        if m:
            page = int(m.group(1) or m.group(2))
            continue
        if re.fullmatch(r'VEDDA\s+VOCABULARY\.?', s) or re.fullmatch(r'\d{1,3}', s):
            continue
        m = re.match(r'^(\d{1,3})\.\s+(.*)$', s)
        if m:
            if cur:
                entries.append(cur)
            cur = {'no': int(m.group(1)), 'page': page, 'text': m.group(2)}
        elif cur:
            cur['text'] += ' ' + s
    if cur:
        entries.append(cur)
    return entries


def parse(entry):
    t = re.sub(r'\s+', ' ', entry['text']).strip()

    # 1. BODY = everything before the first derivation marker. Gunasekara's
    #    analysis lives after it and is deliberately never read.
    m = CUT.search(t)
    body = t[:m.start()] if m else t

    # 2. the cognate the ENTRY itself cites, taken only from the body so a
    #    derivation-internal '(T. podi)' can never be mistaken for it
    cog = ''
    for mc in re.finditer(r'\(\s*([A-Z][a-z]?\.(?:\s*[A-Z]\.)?)\s*([^)]{1,60})\)', body):
        if mc.group(1).replace(' ', '').rstrip('.') in LANG:
            cog = mc.group(1).strip() + ' ' + mc.group(2).strip()
            break

    # 3. HEAD = body with every parenthetical removed
    head = re.sub(r'[\(\[][^)\]]*[\)\]]?', ' ', body)
    head = re.sub(r'\s+', ' ', head).strip(' .,;')
    if ',' not in head:
        return None
    gloss, rest = head.split(',', 1)
    gloss = gloss.strip(' .,?')
    if not gloss:
        return None

    out = []
    # A ';' separates CODE GROUPS. A ',' separates forms WITHIN a group, and
    # every form in a group shares that group's trailing locality codes:
    # 'adane, aidanda D. Bl.' is both forms recorded at Dambani and
    # Bulugahaladena, not one tagged form and one untagged.
    STOP = {'it', 'is', 'the', 'a', 'an', 'and', 'or', 'of', 'to', 'in',
            'used', 'also', 'same', 'as', 'for', 'at', 'by', 'with', 'was',
            'are', 'this', 'that', 'one', 'who', 'not'}
    for group in rest.split(';'):
        group = group.strip(' .,')
        if not group:
            continue
        words, codes, others = [], [], []
        for tk in group.split():
            c = tk.rstrip('.,')
            if re.fullmatch(r'[A-Z][a-z]?', c):
                if c in LOCALITY or c in REGISTER:
                    codes.append(c)
                else:
                    others.append(c)
                continue
            if not codes and not others:
                words.append(tk)
        for f in ' '.join(words).split(','):
            f = f.strip(' .,')
            if len(f) < 2 or not re.search(r'[a-zA-Z]{2}', f):
                continue
            if all(w.lower().strip('.,') in STOP for w in f.split()):
                continue
            # reject anything that reads as English prose rather than a form
            if len(f.split()) > 3:
                continue
            if re.search(r'(the|and|from|with|which|being|has|who|to move)', f, re.I):
                continue
            if re.search(r'["“”{}^]', f):
                continue
            out.append((f, codes, others))
    if not out:
        return None
    return {'gloss': gloss, 'forms': out, 'cognate': cog}


def main():
    entries = load_entries()
    rows, skipped = [], 0
    for e in entries:
        p = parse(e)
        if not p:
            skipped += 1
            continue
        leaf = e['page'] + LEAF_OFFSET
        for form, codes, others in p['forms']:
            locs = [LOCALITY[c] for c in codes if c in LOCALITY]
            regs = [REGISTER[c] for c in codes if c in REGISTER]
            rows.append({
                'english': p['gloss'],
                'vedda': form,
                'localities': '; '.join(locs),
                'register': '; '.join(regs),
                'other_codes': '; '.join(others),
                'sinhalese_cf': p['cognate'],
                'entry_no': e['no'],
                'page': e['page'],
                'page_image': IA.format(leaf=leaf),
                'attributed_to': 'Seligmann & Seligmann',
                'source': ('Seligmann, C. G. & Seligmann, B. Z. (1911) The Veddas. '
                           'Cambridge University Press, Vedda Vocabulary pp.423-451'),
                'rights': ('Public domain in the United States (published 1911). '
                           'In copyright in the UK and Sri Lanka until 1 Jan 2036. '
                           'Facts only: no derivation or prose reproduced.'),
            })
    OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, 'lexicon-seligmann.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    tagged = sum(1 for r in rows if r['localities'])
    print('numbered entries parsed   : %d  (skipped %d)' % (len(entries) - skipped, skipped))
    print('form rows                 : %d' % len(rows))
    print('distinct Vedda forms      : %d' % len({r['vedda'].lower() for r in rows}))
    print('English glosses           : %d' % len({r['english'] for r in rows}))
    print('rows with a LOCALITY tag  : %d  (%.0f%%)' % (tagged, 100*tagged/len(rows)))
    print('rows in a special register: %d' % sum(1 for r in rows if r['register']))
    print('rows citing a cognate     : %d' % sum(1 for r in rows if r['sinhalese_cf']))
    print('\n--- sample ---')
    for r in rows[:14]:
        print('  %-18s %-16s %-34s %s' % (r['english'][:18], r['vedda'][:16],
                                          r['localities'][:34], r['sinhalese_cf'][:18]))


main()
