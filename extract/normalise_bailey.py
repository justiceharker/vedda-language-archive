# -*- coding: utf-8 -*-
r"""Bailey 1863 blocks -> lexicon rows, then a CROSS-SOURCE comparison
against Parker 1909.

Bailey's four columns are English | Veddah | Singhalese | Remarks, and the
Remarks column is his OWN etymological analysis. It is kept verbatim per row
because it is what documents the periphrasis he describes in his prose
(lightning = 'fallen fire', thunder = 'the demon has cried out').

*** Bailey states his own two-category distinction in the paper: words "which
*** probably differ from the Singhalese", and those "which, though Singhalese,
*** are, in the sense here used, peculiar to the Veddahs". Where his Veddah and
*** Singhalese columns carry the SAME form, that is the second category and is
*** flagged rather than silently published as a distinct Vedda word.
"""
import csv, json, os, re, unicodedata
import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
SRC_DIR = _os.path.join(_ROOT, 'sources')
BUILD_DIR = _os.path.join(_ROOT, 'build')


blocks = json.load(open(BUILD_DIR + '/bailey_blocks.json', encoding='utf-8'))['blocks']


def fix(s):
    s = s.replace('—', '-')
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


def clean_form(t):
    # The scan leaves stray brackets and marks on some cells ('Balo )',
    # 'Kotowa >'). Strip them; never touch letters.
    t = re.sub(r'[()<>\[\]{}*^~"“”]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip(" ,.;:!'-")
    return t


rows = []
for b in blocks:
    eng = fix(b['english'])
    if not eng or len(eng) > 35:
        continue
    ved = [clean_form(y) for x in join_wrapped(b['veddah'])
           for y in re.split(r'[,;]', x)]
    sin = [clean_form(x) for x in join_wrapped(b['singhalese'])]
    rem = ' '.join(join_wrapped(b['remarks'])).strip()
    for v in ved:
        if len(v) < 2 or not re.search(r'[A-Za-z]{2}', v):
            continue
        same = any(v.lower() == s.lower() for s in sin)
        rows.append({
            'english': eng,
            'veddah': v,
            'singhalese_cf': '; '.join(sin),
            'same_as_singhalese': 'yes' if same else '',
            'bailey_remark': rem,
            'attributed_to': 'Bailey',
            'source': ('Bailey, J. (1863) An Account of the Wild Tribes of the '
                       'Veddahs of Ceylon, Trans. Ethnological Soc. London II'),
            'page': b['page'],
        })

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, 'lexicon-bailey.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

# ---------------- cross-source comparison against Parker ---------------------
parker = list(csv.DictReader(open(os.path.join(OUT, 'lexicon-parker.csv'), encoding='utf-8')))


def norm_gloss(g):
    g = g.lower().strip()
    g = re.sub(r'\(.*?\)', ' ', g)
    g = re.sub(r'^(the|a|an)\s+', '', g)
    g = re.sub(r'[^a-z, ]', ' ', g)
    g = re.sub(r'\s+', ' ', g).strip(' ,')
    return g


def norm_form(v):
    v = v.replace('&', 'a')          # this scan's accented-a
    v = re.sub(r'\d', '', v)         # OCR noise inside a word
    v = unicodedata.normalize('NFKD', v)
    v = ''.join(c for c in v if not unicodedata.combining(c))
    v = v.lower()
    v = v.replace('w', 'v').replace('dd', 'd').replace('tt', 't')
    v = re.sub(r'[^a-z]', '', v)
    return v


def norm_translit(v):
    """Bailey writes Veddah in ENGLISH spelling conventions ('Doongah',
    'Eecha kola', 'Metchan'); Parker uses a scholarly one ('Dun-ga',
    'Ica-Kola', 'Meccan'). Comparing the raw strings therefore reports
    TRANSCRIPTION differences as if they were lexical disagreement, which
    would be an artefact of our own method rather than a fact about the
    language. This folds the two conventions together before comparing."""
    v = norm_form(v)
    for a, b in (('tch', 'c'), ('ch', 'c'), ('ck', 'c'), ('q', 'g'),
                 ('oo', 'u'), ('ee', 'i'), ('ea', 'i'), ('ae', 'e'),
                 ('ai', 'e'), ('y', 'i'), ('j', 'c')):
        v = v.replace(a, b)
    v = re.sub(r'(.)\1+', r'\1', v)          # collapse doubled letters
    v = re.sub(r'h$', '', v)                 # Bailey's decorative final -h
    return v


def lev(a, b):
    if a == b:
        return 0
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr = [i]
        for j, cb in enumerate(b, 1):
            curr.append(min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = curr
    return prev[-1]


pg, bg = {}, {}
for r in parker:
    pg.setdefault(norm_gloss(r['english']), set()).add(r['vaedi'])
for r in rows:
    bg.setdefault(norm_gloss(r['english']), set()).add(r['veddah'])

shared = sorted(set(pg) & set(bg))
cross = []
n_same, n_conv, n_diff = 0, 0, 0
for g in shared:
    pf, bf = sorted(pg[g]), sorted(bg[g])
    best = None
    for a in pf:
        for b_ in bf:
            na, nb = norm_form(a), norm_form(b_)
            ta, tb = norm_translit(a), norm_translit(b_)
            if not na or not nb:
                continue
            if lev(na, nb) <= 2 or na[:4] == nb[:4]:
                cand = ('same word', a, b_, lev(na, nb))
            elif lev(ta, tb) <= 1 or (len(ta) > 3 and ta[:4] == tb[:4]):
                cand = ('same word, different transcription', a, b_, lev(ta, tb))
            else:
                continue
            if best is None or cand[3] < best[3]:
                best = cand
    verdict = best[0] if best else 'unresolved'
    if verdict == 'same word':
        n_same += 1
    elif verdict.startswith('same word,'):
        n_conv += 1
    else:
        n_diff += 1
    cross.append({
        'english': g,
        'parker_1909': '; '.join(pf),
        'bailey_1863': '; '.join(bf),
        'verdict': verdict,
        'closest_pair': ('%s = %s' % (best[1], best[2])) if best else '',
    })

with open(os.path.join(OUT, 'cross-source.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(cross[0].keys()))
    w.writeheader()
    w.writerows(cross)

print('BAILEY 1863')
print('  lexicon rows            : %d' % len(rows))
print('  distinct Veddah forms   : %d' % len({r['veddah'].lower() for r in rows}))
print('  English glosses         : %d' % len({r['english'] for r in rows}))
print('  carrying Bailey remark  : %d' % sum(1 for r in rows if r['bailey_remark']))
print()
print('CROSS-SOURCE (Parker 1909 vs Bailey 1863)')
print('  glosses in BOTH sources        : %d' % len(shared))
print('  same word, same spelling       : %d' % n_same)
print('  same word, diff transcription  : %d' % n_conv)
print('  UNRESOLVED (not a claim either way) : %d' % n_diff)
print()
print('--- same word, different transcription (would read as disagreement) ---')
for c in cross:
    if c['verdict'].startswith('same word,'):
        print('  %-12s %s' % (c['english'][:12], c['closest_pair']))
print()
print('--- unresolved: could be a different word OR scan damage ---')
for c in cross:
    if c['verdict'] == 'unresolved':
        print('  %-12s Parker: %-32s Bailey: %s'
              % (c['english'][:12], c['parker_1909'][:32], c['bailey_1863'][:26]))
