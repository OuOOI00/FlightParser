# Flight Schedule Parser

Python CLI tool for parsing, validating, and querying flight schedule CSV files.

## Usage

```bash
# Parse CSV
python flight_parser.py -i data/db.csv

# Parse folder
python flight_parser.py -d data/flights/

# Query existing database
python flight_parser.py -j data/db.json -q data/query.json
```

## Output

- `db.json` — valid flights
- `errors.txt` — invalid records with reasons
- `response_<id>_<name>_<YYYYMMDD_HHMM>.json` — query results
