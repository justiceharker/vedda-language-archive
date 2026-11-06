#!/usr/bin/env bash
# Download the source scans. They are large and re-downloadable, so they are
# gitignored rather than committed. Run this once before ./build.sh.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p sources

get () {  # get <url> <dest> <min-bytes>
  if [ -s "sources/$2" ] && [ "$(wc -c < "sources/$2")" -ge "$3" ]; then
    echo "  have  $2"; return
  fi
  echo "  get   $2"
  curl -sSL --fail --max-time 900 "$1" -o "sources/$2"
  actual=$(wc -c < "sources/$2")
  if [ "$actual" -lt "$3" ]; then
    echo "REFUSING: $2 is $actual bytes, expected at least $3. Deleting." >&2
    rm -f "sources/$2"; exit 1
  fi
}

echo "Parker 1909, Ancient Ceylon (word coordinates)"
get "https://archive.org/download/ancientceylonacc00park/ancientceylonacc00park_djvu.xml" \
    parker.xml 15000000

echo "Bailey 1863, Trans. Ethnological Soc. London vol. II (word coordinates)"
get "https://archive.org/download/transactionseth01londgoog/transactionseth01londgoog_djvu.xml" \
    bailey.xml 15000000

echo "Seligmann 1911, The Veddas (text layer; the vocabulary is single-column)"
get "https://archive.org/download/veddas__00seliuoft/veddas__00seliuoft_djvu.txt" \
    selig.txt 900000

echo
echo "Done. Sources in ./sources (gitignored). Next: ./build.sh"
