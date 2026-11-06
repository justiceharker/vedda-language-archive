# -*- coding: utf-8 -*-
r"""Turn extracted Parker blocks into a lexicon: one row per attested Vaedi form.

Markers Parker DEFINES in his own introduction (Ancient Ceylon, pp.123-124),
and which are therefore carried as DATA rather than stripped as noise:

  N.    "Where the letter N is suffixed the word is taken from Mr. Nevill's
        writings."  -> a SECOND COLLECTOR (Hugh Nevill, 1848-1897), not a dialect.
  f.    feminine form. OCR renders it '/.'
  pl.   plural.       OCR renders it 'pi.'
  (?)   Parker's own uncertainty marker.

  A BLANK Vaedi cell is NOT missing data. Parker: "In the cases where no word
  is given in the Vaedi dialect or Kaele-basa, both the Vaeddas and other
  hunters employ colloquial Sinhalese words, often slightly altered in
  pronunciation by the Vaeddas."  Those headwords go to uses-sinhalese.csv.

*** Kaele-basa is the Kandyan Sinhalese / Wanniya hunters' jungle register.
*** It is NOT Vedda. Carried as labelled comparison only. Never merge it.
"""
import csv, json, re, os
import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
SRC_DIR = _os.path.join(_ROOT, 'sources')
BUILD_DIR = _os.path.join(_ROOT, 'build')


blocks = json.load(open(BUILD_DIR + '/parker_blocks.json', encoding='utf-8'))['blocks']


def fix(s):
    s = s.replace('—', '-').replace('�', '')
    s = re.sub(r'(?<![A-Za-z])/\.', 'f.', s)
    s = re.sub(r'(?<![A-Za-z])pi\.', 'pl.', s)
    return re.sub(r'\s+', ' ', s).strip(' _')


def join_wrapped(parts):
    out = []
    for p in parts:
        p = fix(p)
        if not p:
            continue
        if out and out[-1].endswith('-'):
            out[-1] = out[-1][:-1] + p
        else:
            out.append(p)
    return out


def merge_unbalanced_parens(lines):
    """A grammatical note can span several cell LINEs, e.g. 'Go, to' reads
    ['Mangaccana', '(Fut. 1st pers. sing.', 'Mangaccan.', ... , 'Mangaccapa).'].
    Absorb following lines until the parentheses balance again."""
    out, buf, depth = [], '', 0
    for ln in lines:
        depth += ln.count('(') - ln.count(')')
        buf = (buf + ' ' + ln).strip() if buf else ln
        if depth <= 0:
            out.append(buf)
            buf, depth = '', 0
    if buf:
        out.append(buf)
    return out


def split_outside_parens(line):
    depth, buf, out = 0, '', []
    for ch in line:
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth = max(0, depth - 1)
        if ch == ',' and depth == 0:
            out.append(buf)
            buf = ''
        else:
            buf += ch
    out.append(buf)
    return [t.strip() for t in out if t.strip()]


# ---- drop Parker's page footnotes, which are not table rows -----------------
# A footnote wraps too, so dropping only its first line leaves the tail to be
# absorbed as a continuation of a real headword ('Shoot (with arrow), to' once
# ended up carrying "...particle kadawa would thus mean 'never'").
kept, dropping = [], False
for b in blocks:
    e = fix(b['english'])
    if re.match(r'^\d+\s+[A-Z]', e) or 'Compare Sin.' in e:
        dropping = True
        continue
    if dropping and e[:1].islower():
        continue
    dropping = False
    kept.append(b)
blocks = kept

# ---- merge WRAPPED headwords -----------------------------------------------
# The English column is narrow, so one headword wraps over several cells:
# 'Stage (of jour-' + 'ney)' and 'Monkey (Sem-' + 'nopithecus)'. Each wrap
# had become its own headword, splitting one concept in two and mis-glossing
# every Vaedi form under it.
def tidy_head(e):
    e = re.sub(r'\(\s+', '(', e)
    e = re.sub(r'\s+\)', ')', e)
    e = re.sub(r'\)\s+[a-z]$', ')', e)          # stray OCR letter
    e = e.strip(' ‘’“”\'"')
    return re.sub(r'\s+', ' ', e).strip()

merged_blocks = []
for b in blocks:
    e = fix(b['english'])
    prev = merged_blocks[-1] if merged_blocks else None
    pe = fix(prev['english']) if prev else ''
    cont = bool(prev) and (
        pe.endswith('-')                                  # hyphen wrap
        or pe.count('(') > pe.count(')')                  # paren still open
        or (e[:1].islower() and e.lower() != 'no')        # lowercase tail
        or e.startswith('(') or e.startswith(')')
    )
    if cont:
        sep = '' if pe.endswith('-') else ' '
        base = pe[:-1].rstrip() if pe.endswith('-') else pe
        prev['english'] = tidy_head(base + sep + e)
        for k in ('sinhalese', 'kaele_basa', 'vaedi'):
            prev[k].extend(b[k])
    else:
        merged_blocks.append(dict(b, english=tidy_head(e)))
blocks = merged_blocks

# ---- resolve ',,' ditto headwords against their parent ---------------------
parent = None
for b in blocks:
    e = fix(b['english'])
    if re.match(r'^(,,|-)\s*\S', e):
        tail = re.sub(r'^(,,|-)\s*', '', e)
        base = (parent or '').split(',')[0]
        e = (base + ', ' + tail).strip(', ')
    else:
        parent = e
    b['english_resolved'] = e

rows, uses_sinhalese = [], []
for b in blocks:
    sin = join_wrapped(b['sinhalese'])
    kae = join_wrapped(b['kaele_basa'])
    vae = join_wrapped(b['vaedi'])

    if not vae:
        uses_sinhalese.append({'english': b['english_resolved'],
                               'sinhalese_cf': '; '.join(sin),
                               'kaele_basa_cf': '; '.join(kae),
                               'page': b['page']})
        continue

    toks = []
    for line in merge_unbalanced_parens(vae):
        toks.extend(split_outside_parens(line))

    # Rebuild forms. A token that is 'N.' or starts 'N. <word>' attributes the
    # PRECEDING form to Nevill; any remainder begins a new form.
    forms = []
    for t in toks:
        m = re.match(r'^N\.\s*(.*)$', t)
        if m:
            if forms:
                forms[-1]['nevill'] = True
            if m.group(1).strip():
                forms.append({'text': m.group(1).strip(), 'nevill': False})
            continue
        m = re.match(r'^(f|pl)\.\s*(\S+)$', t)
        if m and forms:
            forms[-1]['fem' if m.group(1) == 'f' else 'plu'] = m.group(2).strip(' ,.')
            continue
        if re.fullmatch(r'\(.*\)\.?', t.strip()) and forms:
            forms[-1]['note'] = t.strip().strip('().')
            continue
        if re.fullmatch(r'[Nfpl.\s?()]+', t):
            continue
        forms.append({'text': t, 'nevill': False})

    for fo in forms:
        txt = fo['text']
        if re.search(r'(?<![A-Za-z])N\.', txt):
            fo['nevill'] = True
            txt = re.sub(r'(?<![A-Za-z])N\.', ' ', txt)
        note = fo.get('note', '')
        m = re.search(r'\(([^)]*)\)', txt)
        if m:
            note = m.group(1).strip()
            txt = txt[:m.start()] + ' ' + txt[m.end():]
        uncertain = ('?' in note) or ('?' in txt)
        mf = re.search(r'(?<![A-Za-z])f\.\s*([A-Za-z\-]+)', txt)
        mp = re.search(r'(?<![A-Za-z])pl\.\s*([A-Za-z\-]+)', txt)
        head = re.split(r'(?<![A-Za-z])(?:f|pl)\.', txt)[0]
        head = re.sub(r'(?<=[a-z])\.(?=[a-z])', '', head)      # 'Keri-bot.a'
        head = re.sub(r'\d+$', '', head)                       # 'Kodawa1'
        head = re.sub(r'[?;]', '', head)
        head = re.sub(r'\s+', ' ', head).strip(' ,.-')
        if len(head) < 2 or not re.search(r'[A-Za-z]{2}', head):
            continue
        rows.append({
            'english':             b['english_resolved'],
            'vaedi':               head,
            'vaedi_feminine':      fo.get('fem', '') or (mf.group(1) if mf else ''),
            'vaedi_plural':        fo.get('plu', '') or (mp.group(1) if mp else ''),
            'grammatical_note':    note,
            'uncertain_in_source': 'yes' if uncertain else '',
            'attributed_to':       'Nevill (via Parker)' if fo['nevill'] else 'Parker',
            'sinhalese_cf':        '; '.join(sin),
            'kaele_basa_cf':       '; '.join(kae),
            'source':              'Parker, H. (1909) Ancient Ceylon, London: Luzac & Co.',
            'page':                b['page'],
        })

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
os.makedirs(OUT, exist_ok=True)
os.makedirs(OUT, exist_ok=True)
for name, data in (('lexicon-parker.csv', rows), ('uses-sinhalese.csv', uses_sinhalese)):
    with open(os.path.join(OUT, name), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(data[0].keys()))
        w.writeheader()
        w.writerows(data)

uniq = {r['vaedi'].lower() for r in rows}
print('*** LEXICON ROWS (attested Vaedi forms) : %d' % len(rows))
print('*** DISTINCT Vaedi word forms           : %d' % len(uniq))
print('    English headwords covered           : %d' % len({r['english'] for r in rows}))
print('    attributed to Parker                : %d' % sum(1 for r in rows if r['attributed_to'] == 'Parker'))
print('    attributed to Nevill (via Parker)   : %d' % sum(1 for r in rows if r['attributed_to'] != 'Parker'))
print('    with a feminine form                : %d' % sum(1 for r in rows if r['vaedi_feminine']))
print('    with a plural form                  : %d' % sum(1 for r in rows if r['vaedi_plural']))
print('    with a grammatical note             : %d' % sum(1 for r in rows if r['grammatical_note']))
print('    marked uncertain by Parker          : %d' % sum(1 for r in rows if r['uncertain_in_source']))
print('    no Vaedi word, they use Sinhalese   : %d' % len(uses_sinhalese))
bad = [r['vaedi'] for r in rows if re.search(r'[0-9!_]|\.\.|^-|-$', r['vaedi'])]
print('    still OCR-suspect                   : %d %s' % (len(bad), bad[:8]))
