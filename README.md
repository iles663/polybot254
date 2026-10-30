# polybot254

Polymarket bot for sports awards and other awards markets.

## How it works
- Scans Polymarket Gamma API for active awards markets (Oscars, esports awards, MVP, etc.)
- Filters by keyword list in `bot.py`
- Runs every 6 hours via GitHub Actions
- Set `DRY_RUN=false` in the workflow to enable real trading

## Setup
1. Add repo secret `POLY_PRIVATE_KEY` (wallet private key)
2. Add repo secret `POLY_FUNDER` (only if using a proxy/Magic wallet)
3. Trigger the workflow manually from the Actions tab