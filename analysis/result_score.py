# Script to score the responses from the context stuffing and RAG evaluations completed.
# Useful for larger data sets. Smaller sets can be scored manually, but can be time consuming.
from dotenv import load_dotenv
load_dotenv() 

import json
import os

from bert_score import (
    score as bert_score,
)  # Use BERTScore for automatic evaluation of model responses against gold answers
from openai import OpenAI

# For LLM-as-judge evaluation
JUDGE_MODEL = "gpt-5.4-mini"  # Using smaller model for judging to save on costs, can adjust as needed

JUDGE_SYSTEM_PROMPT = """You are to evaluate the quality of a model response to a D&D 5th Edition rules question.

The question is: {gold_question}
The expected answer is: {gold_answer}
The model's answer is: {model_answer}

Score the models answer on a scale of 0 to 2 compared to the expected answer, where:
0 = The answer is completely incorrect or irrelevant to the question.
1 = The answer is partially correct, but has some inaccuracies or missing information.
2 = The answer is fully correct and accurately addresses the question.

Reply with the score as a single digit (0, 1, or 2) and a brief explanation for the score you gave."""


def call_judge(gold_question, gold_answer, model_answer, client) -> dict:
    prompt = JUDGE_SYSTEM_PROMPT.format(
        gold_question=gold_question, gold_answer=gold_answer, model_answer=model_answer
    )
    response = client.chat.completions.create(
        model=JUDGE_MODEL,
        messages=[
            {"role": "system", "content": "You are a evaluation assistant."},
            {"role": "user", "content": prompt},
        ],
        max_completion_tokens=100,  # Adjust as needed
        temperature=0.0,  # Deterministic for evaluation
    )
    text = response.choices[0].message.content.strip()
    try:
        score = int(text.strip()[0])
    except (ValueError, IndexError):
        score = -1  # Setting invalid score to -1 to indicate an error in judging
    return {"score": score, "reason": text}


def all_scores():
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    all_results = []
    for path in [
        "eval-results/context_stuffing_results.jsonl",
        "eval-results/rag_results.jsonl",
    ]:
        with open(path, encoding="utf-8") as f:
            all_results.extend([json.loads(line) for line in f if line.strip()])

    valid = [
        r
        for r in all_results
        if "model_answer" in r and "gold_answer" in r and "gold_question" in r
    ]

    # Get BERTScore
    print("Calculating BERTScore for all valid results...")
    candidates = [r["model_answer"] for r in valid]
    references = [r["gold_answer"] for r in valid]
    _, _, F1 = bert_score(candidates, references, lang="en", verbose=True)
    for r, f1 in zip(valid, F1.tolist()):
        r["bert_score"] = round(f1, 4)

    # Get LLM-as-judge scores
    print("Calculating LLM-as-judge scores for all valid results...")
    for i, r in enumerate(valid):
        print(f"Evaluating result {i+1}/{len(valid)} with LLM judge...", end="\r")
        judge_result = call_judge(
            r["gold_question"], r["gold_answer"], r["model_answer"], client
        )
        r.update(judge_result)

    # Save all results with scores to a new JSONL file
    with open("eval-results/all_results_with_scores.jsonl", "a", encoding="utf-8") as f:
        for r in all_results:
            f.write(json.dumps(r) + "\n")
    print(
        f"\nCompleted scoring of {len(valid)} results. All results with scores saved to eval-results/all_results_with_scores.jsonl"
    )

all_scores()
