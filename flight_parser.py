# Murad Hashimov 241ADB148

import argparse
import csv
import json
import os
import sys
from datetime import datetime

# datetime format
DATETIME_FORMAT = "%Y-%m-%d %H:%M"
DEFAULT_DB_JSON = "db.json"
ERRORS_FILE = "errors.txt"

VALID_AIRPORTS = {
    "HEL", "DXB", "CDG", "BER", "MAD",
    "ARN", "AMS", "IST", "CPH", "ATH", "ZAG",
    "FCO", "BER", "BRU","LHR", "JFK", "FRA", "RIX", "OSL",
    "LAX", "DFW", "MIA", "MEX", "NBO", "DUB", "BCN", "LTN", "DOH", "SYD"
}


def parse_args():
    # parse command line arguments
    parser = argparse.ArgumentParser(description="Flight schedule parser")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-i", "--input", help="CSV file path")
    group.add_argument("-d", "--directory", help="Folder with CSV files")

    parser.add_argument("-o", "--output", help="Output JSON file (default db.json)")

    return parser.parse_args()


def parse_datetime(text):
    # convert string to datetime object
    try:
        return datetime.strptime(text, DATETIME_FORMAT)
    except:
        return None


def validate_record(fields):
    # validate one CSV row
    errors = []

    # must have exactly 6 fields
    if len(fields) != 6:
        errors.append("missing required fields")
        return False, {}, errors

    flight_id = fields[0].strip()
    origin = fields[1].strip()
    destination = fields[2].strip()
    dep = fields[3].strip()
    arr = fields[4].strip()
    price = fields[5].strip()

    # flight id: 2–8 alphanumeric characters
    if not (2 <= len(flight_id) <= 8 and flight_id.isalnum()):
        if len(flight_id) > 8:
            errors.append("flight_id too long (more than 8 characters)")
        else:
            errors.append("invalid flight_id (must be 2–8 alphanumeric)")

    # origin: must be in VALID_AIRPORTS
    if not origin:
        errors.append("missing origin field")
    elif origin not in VALID_AIRPORTS:
        errors.append("invalid origin code (not real airport)")

    # destination: must be in VALID_AIRPORTS
    if not destination:
        errors.append("missing destination field")
    elif destination not in VALID_AIRPORTS:
        errors.append("invalid destination code (not real airport)")

    # departure and arrival datetime
    dep_dt = parse_datetime(dep)
    arr_dt = parse_datetime(arr)

    if dep_dt is None:
        errors.append("invalid departure datetime")
    if arr_dt is None:
        errors.append("invalid arrival datetime")

    if dep_dt and arr_dt and arr_dt <= dep_dt:
        errors.append("arrival before departure")

    # price positive float
    try:
        price_value = float(price)
        if price_value < 0:
            errors.append("negative price value")
        elif price_value == 0:
            errors.append("price must be positive")
    except:
        errors.append("invalid price value")

    # if any errors record is invalid
    if errors:
        return False, {}, errors

    # valid record
    record = {
        "flight_id": flight_id,
        "origin": origin,
        "destination": destination,
        "departure_datetime": dep,
        "arrival_datetime": arr,
        "price": float(price)
    }

    return True, record, []


def parse_csv_file(filename):
    # parse a single CSV file
    if not os.path.exists(filename):
        print("ERROR: file not found:", filename, file=sys.stderr)
        sys.exit(1)

    valid = []
    errors = []

    with open(filename, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)

        for line_no, row in enumerate(reader, start=1):
            # skip header row
            if line_no == 1 and row and row[0].strip().lower() == "flight_id":
                continue

            # skip empty lines
            if not row or all(c.strip() == "" for c in row):
                continue

            line_text = ",".join(row)

            # comment line starting with #
            if row[0].strip().startswith("#"):
                errors.append(f"Line {line_no}: {line_text} \u2192 comment line, ignored for data parsing")
                continue

            # validate normal data row
            ok, record, errs = validate_record(row)
            if ok:
                valid.append(record)
            else:
                errors.append(f"Line {line_no}: {line_text} \u2192 " + "; ".join(errs))

    return valid, errors


def parse_directory(dir_path):
    # parse all CSV files in a folder
    if not os.path.isdir(dir_path):
        print("ERROR: not a directory:", dir_path, file=sys.stderr)
        sys.exit(1)

    all_valid = []
    all_errors = []

    files = sorted(os.listdir(dir_path))
    for name in files:
        if name.lower().endswith(".csv"):
            full_path = os.path.join(dir_path, name)
            valid, errors = parse_csv_file(full_path)
            # add file name prefix to errors
            for e in errors:
                all_errors.append(f"{name}: {e}")
            all_valid.extend(valid)

    if not all_valid and not all_errors:
        print("WARNING: no CSV data found in directory", dir_path, file=sys.stderr)

    return all_valid, all_errors


def write_json_db(records, filename):
    # write valid flights to JSON file
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)


def write_errors(errors, filename):
    # write invalid lines and messages to text file
    with open(filename, "w", encoding="utf-8") as f:
        for e in errors:
            f.write(e + "\n")


def main():
    args = parse_args()

    # must have -i or -d
    if not args.input and not args.directory:
        print("ERROR: you must use -i <file> or -d <folder>", file=sys.stderr)
        sys.exit(1)

    # choose input source
    if args.input:
        valid, errors = parse_csv_file(args.input)
    else:
        valid, errors = parse_directory(args.directory)

    # choose output JSON name
    out_json = args.output if args.output else DEFAULT_DB_JSON

    # write results
    write_json_db(valid, out_json)
    write_errors(errors, ERRORS_FILE)

    # small console info
    print("Valid flights written to", out_json)
    print("Errors written to", ERRORS_FILE)


if __name__ == "__main__":
    main()
