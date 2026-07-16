# Integration Validation Guide

## Running the validator

### Module-only (CI / no running stack)

```bash
PYTHONPATH=sos_orchestrator python3 tests/integration_validation.py --no-live
```

### Full live validation

Start the backend stack first:

```bash
cd infrastructure
docker compose -f docker-compose.full.yml up -d --build
# Optional: seed demo data
python3 database/seed_demo.py
```

Then run:

```bash
PYTHONPATH=sos_orchestrator python3 tests/integration_validation.py --base http://localhost:8080
```

## Checks performed

| Check | Requires live stack |
|---|---|
| Hungarian MRTA allocation | No |
| Auction MRTA allocation | No |
| Paris-law RUL calculation | No |
| EVOC dispatch logic | No |
| `/health` API endpoint | Yes |
| `/turbines` API endpoint | Yes |
| `/patches` API endpoint | Yes |
| `/rul/estimate` API endpoint | Yes |
| `/decision/evoc` API endpoint | Yes |

## Demo seed data

The seed script inserts 2 turbines (WTG-01, WTG-02) and 6 blade patches spanning all three defect urgency levels.

```bash
pip install psycopg[binary]
python3 database/seed_demo.py
```

After seeding, the dashboard patch table and severity chart will populate with real-looking data.
