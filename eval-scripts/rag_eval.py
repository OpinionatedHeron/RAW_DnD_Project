# Assessing models on retrieval-augmented generation (RAG) tasks

import json
import pathlib

from model_wrap import (
    call_gpt,
    call_claude,
    call_gemini, 
)
from rag_pipeline import retrieve

RAG_SYSTEM_PROMPT = """You are a Dungeons & Dragons 5th edition rules expert, with specific knowledge and focus on the System Reference Document v5.1.
Answer the following question based on the retrieved context from the SRD 5.1 document. Only use the provided context to answer questions, and do not rely on any other knowledge you may have.
If you do not know the answer to a question based on the provided context, say "I cannot find the answer to this question in the retrieved context from the SRD 5.1 document."
"""


def build_rag_prompt(question: str, retrieved_chunks: list[str]) -> str:
    context = "\n\n".join(retrieved_chunks)
    return f"""Here is the retrieved context from the SRD 5.1 document:
{context}

Question: {question}"""


# Very similar to context stuffing, but with the retrieved chunks as context instead of the entire document
questions = []
with open("eval-questions/eval_questions_3.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        questions.append(json.loads(line))

results = []
MODELS = {
    "gpt-5.4": call_gpt,
    "claude-opus-4-6": call_claude,
    "gemini-3.1-pro-preview": call_gemini,
}

for model_name, call_fn in MODELS.items():
    print(f"Evaluating model: {model_name}")
    for i, q in enumerate(questions):
        print(f"  Question {i+1}/{len(questions)}", end="\r")
        try:
            retrieved_chunks = retrieve(q["gold_question"])
            rag_prompt = build_rag_prompt(q["gold_question"], retrieved_chunks)
            result = call_fn(rag_prompt, system=RAG_SYSTEM_PROMPT)
            results.append(
                {
                    "test": "rag",
                    "model": model_name,
                    "q_id": q["q_id"],
                    "gold_question": q["gold_question"],
                    "gold_answer": q["gold_answer"],
                    "origin": q["origin"],
                    "model_answer": result["answer"],
                    "input_tokens": result["input_tokens"],
                    "output_tokens": result["output_tokens"],
                    "latency_ms": result["latency_ms"],
                    "cost": result["cost"],
                    "finish_reason": result["finish_reason"],
                }
            )
        except Exception as e:
            print(f"Error evaluating question {q['q_id']} with model {model_name}: {e}")
            results.append(
                {
                    "test": "rag",
                    "model": model_name,
                    "q_id": q["q_id"],
                    "gold_question": q["gold_question"],
                    "error": str(e),
                }
            )

pathlib.Path("eval-results").mkdir(exist_ok=True)
with open("eval-results/rag_results_3.jsonl", "a", encoding="utf-8") as f:
    for result in results:
        f.write(json.dumps(result) + "\n")

print(
    f"Completed evaluation of {len(questions)} questions across {len(MODELS)} models. Results saved to eval-results/rag_results_3.jsonl"
)
