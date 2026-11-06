# -*- coding: utf-8 -*-
"""
Parker, H. (1909) 'Ancient Ceylon', pp.125-132:
the English / Sinhalese / Kaele-basa / Vaedi comparative vocabulary.

Reconstructed from per-word coordinates in archive.org's djvu.xml.
*** The plain _djvu.txt reading order is SCRAMBLED. Never parse it. ***

The OCR emits each table CELL as its own <LINE>, so a line's first-word x0
is the cell's left edge and quantises cleanly into four columns.

*** Kaele-basa is the Kandyan Sinhalese hunters' jungle register, spoken by
*** Sinhalese and Wanniya hunters, NOT by Vaeddas. Parker says so explicitly.
*** It is carried as labelled comparison and must NEVER be merged into Vedda.
"""
import json, re, sys
import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
SRC_DIR = _os.path.join(_ROOT, 'sources')
BUILD_DIR = _os.path.join(_ROOT, 'build')

import xml.etree.ElementTree as ET

XML    = SRC_DIR + '/parker.xml'
LEAVES = range(158, 166)                    # printed pp.125-132
# Column boundaries differ by page parity (recto/verso margins).
# Every one is asserted below to fall inside an observed whitespace gap.
BOUNDS = {0: (327, 668, 1016),              # recto  (leaves 158,160,162,164)
          1: (421, 726, 1093)}              # verso  (leaves 159,161,163,165)
COLS = ['english', 'sinhalese', 'kaele_basa', 'vaedi']

def cells(el):
    out = []
    for ln in el.iter('LINE'):
        ws = list(ln.iter('WORD'))
        if not ws: continue
        c = ws[0].get('coords', '').split(',')
        if len(c) < 4: continue
        x0, y = int(c[0]), int(c[1])
        last = ws[-1].get('coords', '').split(',')
        x1 = int(last[2]) if len(last) >= 4 else x0
        txt = ' '.join((w.text or '').strip() for w in ws)
        txt = re.sub(r'\s+', ' ', txt).strip()
        if txt: out.append({'x': x0, 'x1': x1, 'y': y, 't': txt})
    return out

ROW_TOL = 20     # px. within-row y spread ~10, between-row pitch ~35-45

def group_rows(cs):
    """Cells on one visual row jitter by ~10px. A strict y-sort therefore
    pushes cells across headword boundaries (Bear's 'Walaha' lands under
    'Axe-man'). Cluster into rows first, then read each row left to right."""
    cs = sorted(cs, key=lambda c: (c['y'], c['x']))
    rows, cur = [], []
    for c in cs:
        if cur and c['y'] - cur[-1]['y'] > ROW_TOL:
            rows.append(cur); cur = []
        cur.append(c)
    if cur: rows.append(cur)
    for r in rows: r.sort(key=lambda c: c['x'])
    return rows

def main():
    ctx = ET.iterparse(XML, events=('end',))
    leaf = -1
    blocks, headings, problems = [], [], []
    cur = None

    for ev, el in ctx:
        if el.tag != 'OBJECT': continue
        leaf += 1
        if leaf not in LEAVES:
            el.clear(); continue

        cs = cells(el)
        ytop = min(c['y'] for c in cs)
        cs = [c for c in cs if c['y'] > ytop + 120]        # drop running head
        cs = [c for c in cs if not re.fullmatch(r'[\s\d.]+', c['t'])]
        # drop the column-header band
        cs = [c for c in cs if c['t'] not in
              ('English.','Sinhalese','Sinhalese.','Kaele-basa.','Kaelebasa.','Vaedi.','English')]
        cs.sort(key=lambda c: c['y'])

        bnd = BOUNDS[leaf % 2]
        # ASSERT each boundary sits inside a real gap in this page's x0s
        xs = sorted(c['x'] for c in cs)
        for b in bnd:
            below = max([x for x in xs if x < b], default=None)
            above = min([x for x in xs if x >= b], default=None)
            if below is None or above is None or above - below < 55:
                problems.append(f"leaf {leaf}: boundary {b} not in a clean gap "
                                f"({below}..{above}) - REFUSING")
        page_ink_mid = (min(c['x'] for c in cs) + max(c['x1'] for c in cs)) / 2

        def col_of(x):
            return 0 if x < bnd[0] else 1 if x < bnd[1] else 2 if x < bnd[2] else 3

        for row in group_rows(cs):
          for c in row:
            # a lone, page-centred, single English word ending '.' is a
            # SECTION HEADING spanning the table ('Animals.', 'Verbs.')
            mid = (c['x'] + c['x1']) / 2
            if re.fullmatch(r'[A-Z][a-z]+\.', c['t']) and abs(mid - page_ink_mid) < 90:
                headings.append({'leaf': leaf, 'y': c['y'], 'text': c['t']})
                continue
            i = col_of(c['x'])
            if i == 0:
                if cur: blocks.append(cur)
                cur = {'leaf': leaf, 'page': 125 + (leaf - 158), 'english': c['t'],
                       'sinhalese': [], 'kaele_basa': [], 'vaedi': []}
            elif cur is not None:
                cur[COLS[i]].append(c['t'])
            else:
                problems.append(f"leaf {leaf}: fragment before any headword: {c['t']!r}")
        el.clear()

    if cur: blocks.append(cur)

    json.dump({'blocks': blocks, 'headings': headings, 'problems': problems},
              open(BUILD_DIR + '/parker_blocks.json','w',encoding='utf-8'),
              ensure_ascii=False, indent=1)

    nv = sum(1 for b in blocks if b['vaedi'])
    print(f"headwords (English glosses) : {len(blocks)}")
    print(f"  with >=1 Vaedi form       : {nv}")
    print(f"  Vaedi cell blank          : {len(blocks)-nv}")
    print(f"total Vaedi form-lines      : {sum(len(b['vaedi']) for b in blocks)}")
    print(f"section headings found      : {[h['text'] for h in headings]}")
    print(f"problems                    : {len(problems)}")
    for p in problems[:10]: print("   !", p)
    print("\n--- first 18 headwords ---")
    for b in blocks[:18]:
        print(f"  p{b['page']} {b['english'][:24]:<24} S={str(b['sinhalese'])[:30]:<30} "
              f"K={str(b['kaele_basa'])[:32]:<32} V={b['vaedi']}")

main()
