# -*- coding: utf-8 -*-
r"""Bailey, J. (1863) 'An Account of the Wild Tribes of the Veddahs of Ceylon',
Transactions of the Ethnological Society of London, vol. II, pp. 278-320.
The appended vocabulary runs pp.314-319 (leaves 338-343 of the archive.org scan).

FOUR columns:  English | Veddah | Singhalese | Remarks

The Remarks column is Bailey's OWN etymological analysis and is the most
valuable thing in this source, e.g. lightning 'Ginna wetunu' is glossed
"'Gini wetunu' (Singh.), fallen fire." It documents the periphrasis Bailey
describes in his prose ("to walk is 'to beat the ground with hammers';
a child is 'a bud'").

*** Same rules as the Parker extractor: NEVER parse _djvu.txt (scrambled
*** reading order). Columns are reconstructed from LINE-level x0 coordinates,
*** and every boundary is asserted to fall inside an observed whitespace gap.
"""
import json, re
import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
SRC_DIR = _os.path.join(_ROOT, 'sources')
BUILD_DIR = _os.path.join(_ROOT, 'build')

import xml.etree.ElementTree as ET

XML = SRC_DIR + '/bailey.xml'
LEAVES = range(338, 343)   # 343 is a separate PERSONAL NAMES appendix, not vocabulary
BOUNDS = (700, 1020, 1370)          # 600 DPI scan; stable across page parity
COLS = ['english', 'veddah', 'singhalese', 'remarks']
ROW_TOL = 40                        # 600 DPI: line pitch ~70, within-row spread ~5


def cells(el):
    out = []
    for ln in el.iter('LINE'):
        ws = list(ln.iter('WORD'))
        if not ws:
            continue
        c = ws[0].get('coords', '').split(',')
        if len(c) < 4:
            continue
        last = ws[-1].get('coords', '').split(',')
        txt = ' '.join((w.text or '').strip() for w in ws)
        txt = re.sub(r'\s+', ' ', txt).strip()
        if txt:
            out.append({'x': int(c[0]), 'y': int(c[1]),
                        'x1': int(last[2]) if len(last) >= 4 else int(c[0]),
                        't': txt})
    return out


def group_rows(cs):
    cs = sorted(cs, key=lambda c: (c['y'], c['x']))
    rows, cur = [], []
    for c in cs:
        if cur and c['y'] - cur[-1]['y'] > ROW_TOL:
            rows.append(cur)
            cur = []
        cur.append(c)
    if cur:
        rows.append(cur)
    for r in rows:
        r.sort(key=lambda c: c['x'])
    return rows


def col_of(x):
    for i, b in enumerate(BOUNDS):
        if x < b:
            return i
    return 3


def main():
    ctx = ET.iterparse(XML, events=('end',))
    leaf = -1
    blocks, problems = [], []
    cur = None

    for ev, el in ctx:
        if el.tag != 'OBJECT':
            continue
        leaf += 1
        if leaf not in LEAVES:
            continue

        cs = cells(el)
        if not cs:
            continue
        ytop = min(c['y'] for c in cs)
        cs = [c for c in cs if c['y'] > ytop + 150]          # running head
        # p.314 carries the END OF THE PROSE PAPER above the table and
        # FOOTNOTES below it. Start at Bailey's own heading.
        # START: Bailey's own heading, on p.314 only. Must match DIALECT
        # specifically -- p.318 carries 'SPECIMENS OF VEDDAH NAMES', and
        # matching bare 'SPECIMEN' truncated that page's vocabulary to nothing.
        start = [c['y'] for c in cs if 'SPECIMEN OF VEDDAH DIAL' in c['t'].upper()]
        if start:
            cs = [c for c in cs if c['y'] >= start[0]]
        # END: the word list stops where the PERSONAL NAMES appendix begins.
        stop = [c['y'] for c in cs if 'VEDDAH NAMES' in c['t'].upper()]
        if stop:
            cs = [c for c in cs if c['y'] < stop[0]]
        cs = [c for c in cs if not re.fullmatch(r'[\s\d.]+', c['t'])]
        cs = [c for c in cs if not re.fullmatch(
            r'(English|Veddah|Singhalese|Remarks)\.?', c['t'])]
        if not cs:
            continue

        xs = sorted(c['x'] for c in cs)
        for b in BOUNDS:
            below = max([x for x in xs if x < b], default=None)
            above = min([x for x in xs if x >= b], default=None)
            if below is None or above is None or above - below < 100:
                problems.append(
                    'leaf %d: boundary %d not in a clean gap (%s..%s)'
                    % (leaf, b, below, above))

        for row in group_rows(cs):
            cells_by_col = {i: [] for i in range(4)}
            for c in row:
                cells_by_col[col_of(c['x'])].append(c['t'])
            eng = ' '.join(cells_by_col[0]).strip()
            # A real English gloss is short ('The sun', 'Lightning'). Long
            # column-0 text is running prose or a footnote, not a headword.
            if eng and len(eng) > 35 and not cells_by_col[1] and not cells_by_col[2]:
                continue
            if eng and len(eng) > 35:
                eng = ''
            if eng:
                if cur:
                    blocks.append(cur)
                cur = {'leaf': leaf, 'page': 314 + (leaf - 338), 'english': eng,
                       'veddah': list(cells_by_col[1]),
                       'singhalese': list(cells_by_col[2]),
                       'remarks': list(cells_by_col[3])}
            elif cur is not None:
                for i in (1, 2, 3):
                    if cells_by_col[i]:
                        cur[COLS[i]].extend(cells_by_col[i])
            else:
                problems.append('leaf %d: fragment before any headword: %r'
                                % (leaf, ' '.join(c['t'] for c in row)[:60]))
    if cur:
        blocks.append(cur)

    json.dump({'blocks': blocks, 'problems': problems},
              open(BUILD_DIR + '/bailey_blocks.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)

    nv = sum(1 for b in blocks if b['veddah'])
    print('headwords            : %d' % len(blocks))
    print('  with a Veddah form : %d' % nv)
    print('  with a remark      : %d' % sum(1 for b in blocks if b['remarks']))
    print('problems             : %d' % len(problems))
    for p in problems[:8]:
        print('   !', p)
    print('\n--- first 16 ---')
    for b in blocks[:16]:
        print('  p%d %-18s V=%-26s S=%-18s R=%s'
              % (b['page'], b['english'][:18], str(b['veddah'])[:26],
                 str(b['singhalese'])[:18], ' '.join(b['remarks'])[:44]))


main()
