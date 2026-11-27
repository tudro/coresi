#!/usr/bin/env bash
# Rebuild docs/index.html from the invoice PDFs in invoices/ (needs poppler-utils + python3)
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build docs
for f in invoices/*.[Pp][Dd][Ff]; do
  id=$(basename "$f" | grep -oE 'IMLL[0-9]+')
  pdftotext -layout "$f" "build/$id.txt"
done
cp src/* build/
( cd build && python3 parse.py >/dev/null && python3 build.py >/dev/null && python3 post.py )
cp build/index.html docs/index.html
echo "Built docs/index.html"
