# Script to load markdown source files into chosen models
# NB - GPT and Claude may have a context limit and may not load entire file

import json
import pathlib

from model_wrap import call_gpt, call_claude # call_gemini - commented out for now since Gemini API is currently broken and causing errors

# Load the source document as context for the models
SOURCE_DOC = pathlib.Path("data/D&D_5e_OGL_1.md").read_text(encoding="utf-8")

SYSTEM_PROMPT = f"""You are a Dungeons & Dragons 5th edition rules expert, with specific knowledge and focus on the System Reference Document v5.1.
You have been given the full text of the SRD 5.1 as context, and will be asked questions about the rules of D&D 5e based on that document.
Only use the provided context to answer questions, and do not rely on any other knowledge you may have.
If you do not know the answer to a question based on the provided context, say "The answer to this question is not available in the SRD 5.1 document."
Here is the context:

=== D&D 5e SRD 5.1 START ===
{SOURCE_DOC}
=== D&D 5e SRD 5.1 END ==="""

# Load the evaluation questions
questions = []
with open("eval-questions/eval_questions_1.jsonl", "r", encoding="utf-8") as f:
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
            result = call_fn(q["gold_question"], system=SYSTEM_PROMPT)
            results.append(
                {
                    "test": "context-stuffing",
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
                    "test": "context-stuffing",
                    "model": model_name,
                    "q_id": q["q_id"],
                    "gold_question": q["gold_question"],
                    "error": str(e),
                }
            )

pathlib.Path("eval-results").mkdir(exist_ok=True)
with open("eval-results/context_stuffing_results.jsonl", "a", encoding="utf-8") as f:
    for result in results:
        f.write(json.dumps(result) + "\n")

print(
    f"Completed evaluation of {len(questions)} questions across {len(MODELS)} models. Results saved to eval-results/context_stuffing_results.jsonl"
)
