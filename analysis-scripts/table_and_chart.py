# Creating summary table and chart for the all_results_with_scores.jsonl file generated from result_score.py

import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

records = []
with open("eval-results/all_results_with_scores.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        records.append(json.loads(line))
  
# Building a summary table with average latency, average BERTScore, average LLM judge score, total cost, and count of questions for each model and test type      
table = pd.DataFrame(records)

summary = table.groupby(["model", "test"]).agg(
    avg_latency_ms = ("latency_ms", "mean"),
    avg_bert_score = ("bert_score", "mean"),
    avg_judge_score = ("score", "mean"),
    total_cost = ("cost", "sum"),
    count = ("gold_question", "count")
).round(2)

print(summary.to_string())
summary.to_csv("eval-results/summary_table.csv")

# Graphing the average LLM judge score, average BERTScore, and average latency for each model and test type in a bar chart for easier comparison
fig, axes = plt.subplots(1, 3, figsize=(14, 6))
for ax, metric, label in zip(axes, ["avg_judge_score", "avg_bert_score", "avg_latency_ms"], ["LLM Judge Score", "BERTScore F1", "Latency (ms)"]):
    
    data = summary.reset_index()
    for test, grp in data.groupby("test"):
        ax.bar([r["model"] for _, r in grp.iterrows()],
               grp[metric], label=test)
    ax.set_title(label)
    ax.legend()
    
plt.tight_layout()
plt.savefig("eval-results/comparison_chart.png", dpi=150)
print("Chart saved to eval-results/comparison_chart.png")

# Scatter graph of cost vs accuracy
fig2, ax2 = plt.subplots(figsize=(14, 6))
fig2.suptitle("Cost vs Accuracy", fontsize=12)

data = summary.reset_index()

for test, grp in data.groupby("test"):
    ax2.scatter(grp["total_cost"], grp["avg_judge_score"], label=test, s=100)
    for _, r in grp.iterrows():
        ax2.annotate(r["model"], (r["total_cost"], r["avg_judge_score"]), textcoords="offset points", xytext=(8, 4), fontsize=9)
        
ax2.set_xlabel("Total Cost ($)")
ax2.set_ylabel("Average LLM Judge Score")
ax2.legend()

plt.tight_layout()
plt.savefig("eval-results/cost_vs_accuracy.png", dpi=150)
print("Cost vs Accuracy chart saved to eval-results/cost_vs_accuracy.png")