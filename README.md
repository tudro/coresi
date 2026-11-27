# Invoice expenses by type

Monthly charts of the expenses on the Immo Lila SRL (Adminos) invoices, one chart per
expense type, plus totals. Output is a single static page: `docs/index.html`.

## Rebuild
1. Put the invoice PDFs in `invoices/` (kept out of git by `.gitignore`).
2. Run `./run.sh` (needs `poppler-utils` for `pdftotext`, and Python 3).

## Files
- `src/parse.py` – reads the invoice text and extracts the line items
- `src/build.py` – groups the lines by expense name and builds the data
- `src/post.py` – totals, row layout, legends; writes `index.html` from `tpl.html`
- `src/tpl.html` – chart rendering (plain SVG + JS, no dependencies)

## Rules used
- Administrative services are shown by invoice month; all other maintenance
  expenses are shown for the month before the invoice date (the consumption month).
- Amounts are in RON including VAT.

## Hosting
`docs/index.html` is static. For GitHub Pages: Settings → Pages → branch `main`, folder `/docs`.
Note: GitHub Pages on a free account needs a public repo, and the page contains the invoice amounts.
