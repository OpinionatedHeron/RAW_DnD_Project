# Converting JSON files to excel files for easier data manipulation and analysis

import json
import pathlib
import pandas as pd

INPUT = pathlib.Path("eval-results/context_stuffing_results.jsonl")
OUTPUT = pathlib.Path("eval-results/context_stuffing_results.xlsx")

# Can adjust the file paths as needed
with open(INPUT) as file:
    data = [json.loads(line) for line in file if line.strip()]
    
df = pd.DataFrame(data)
df.to_excel(OUTPUT, index=False)