#!/usr/bin/env bash
# Rebuild every dataset in data/ from the scans in sources/.
# Run ./fetch-sources.sh first.
set -euo pipefail
cd "$(dirname "$0")"
for f in sources/parker.xml sources/bailey.xml sources/selig.txt; do
  [ -s "$f" ] || { echo "missing $f - run ./fetch-sources.sh" >&2; exit 1; }
done
echo "== Parker 1909 =="   && python extract/extract_parker.py    && python extract/normalise_parker.py
echo "== Bailey 1863 =="   && python extract/extract_bailey.py    && python extract/normalise_bailey.py
echo "== Seligmann 1911 ==" && python extract/extract_seligmann.py
echo "== De Silva 1972 (via ASJP) ==" && python extract/fetch_desilva_asjp.py
echo && echo "Rebuilt. Datasets in ./data"
