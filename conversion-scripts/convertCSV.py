import csv
import json
import pathlib
import sys

# Can change name to whatever csv file you want to convert, make sure to change the output path as well
CSV_PATH = "eval-questions/eval_questions_2.csv"
OUTPUT_PATH = "eval-questions/eval_questions_2.jsonl"

REQUIRED_FIELDS = {"q_id", "gold_question", "gold_answer", "origin"}

records = []
with open(CSV_PATH, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    # Check for header fields
    missing = REQUIRED_FIELDS - set(reader.fieldnames or [])
    if missing:
        print(f"Missing required fields: {missing}")
        print(f"Found fields: {reader.fieldnames}")
        sys.exit(1)

    for i, row in enumerate(reader, start=2):
        question = row["gold_question"].strip()
        answer = row["gold_answer"].strip()

        # Skip any blank rows
        if not question or not answer:
            print(f"Skipping blank row {i}")
            continue

        # Add the record to the list
        records.append({
            "q_id": row["q_id"].strip(),
            "gold_question": question,
            "gold_answer": answer,
            "origin": row["origin"].strip()
        })

# Write the records to a JSONL file
pathlib.Path("eval-questions").mkdir(exist_ok=True)
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    for record in records:
        f.write(json.dumps(record) + "\n")

print(f"Converted {len(records)} records from {CSV_PATH} to {OUTPUT_PATH}")
print(f"Sample record: {records[0] if records else 'No records found'}")