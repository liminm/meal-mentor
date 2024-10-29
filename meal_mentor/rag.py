import json
import os
from time import time
from typing import Optional, Dict, Callable

from dotenv import load_dotenv
# from elasticsearch import Elasticsearch
from openai import OpenAI

from meal_mentor import ingest

# Load environment variables from the .env file
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# Access the environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if OPENAI_API_KEY is not None:
    print("Loaded OPENAI_API_KEY")
    client = OpenAI(api_key=OPENAI_API_KEY)
else:
    print("Something went wrong; Make sure you have added the OPENAI_API_KEY in the .env file")

documents = ingest.ingest_data()
text_fields = [
    "recipe_name",
    "diet_type",
    "cuisine_type",
    "protein(g)",
    "carbs(g)",
    "fat(g)",
]
keyword_fields = ["id"]

index = ingest.load_index(
    documents=documents,
    text_fields=text_fields,
    keyword_fields=keyword_fields
)


def search(
        query: str,
        search_function: Callable,
        boost: Optional[Dict[str, float]] = None,
        num_results: int = 10,
):
    # Set default boost values if not provided
    if boost is None:
        boost = {
            'recipe_name': 3,
            'cuisine_type': 2,
            'diet_type': 0,
            'protein(g)': 2,
            'carbs(g)': 1,
            'fat(g)': 1
        }

    # Perform the search using the query and boost settings
    results = search_function(
        query=query,
        filter_dict={},
        boost_dict=boost,
        num_results=num_results
    )

    return results


prompt_template = """
You're a healthy recipe recommender. Answer the QUESTION based on the CONTEXT from our recipe database.
Use only the facts from the CONTEXT when answering the QUESTION. Do not ask any follow up questions.

QUESTION: {question}

CONTEXT:
{context}
""".strip()

entry_template = """
recipe_name: {recipe_name}
diet_type: {diet_type}
protein: {protein(g)}g
carbs: {carbs(g)}g
fat: {fat(g)}g
cuisine_type: {cuisine_type}
""".strip()


def build_prompt(query, search_results):
    context = ""

    for doc in search_results:
        context = context + entry_template.format(**doc) + "\n\n"

    return prompt_template.format(question=query, context=context).strip()


def llm(prompt, model="gpt-4o-mini"):
    response = client.chat.completions.create(
        model=model, messages=[{"role": "user", "content": prompt}]
    )

    answer = response.choices[0].message.content

    token_stats = {
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
    }

    return answer, token_stats


evaluation_prompt_template = """
You are an expert evaluator for a RAG system.
Your task is to analyze the relevance of the generated answer to the given question.
Based on the relevance of the generated answer, you will classify it
as "NON_RELEVANT", "PARTLY_RELEVANT", or "RELEVANT".

Here is the data for evaluation:

Question: {question}
Generated Answer: {answer}

Please analyze the content and context of the generated answer in relation to the question
and provide your evaluation in parsable JSON without using code blocks:

{{
  "Relevance": "NON_RELEVANT" | "PARTLY_RELEVANT" | "RELEVANT",
  "Explanation": "[Provide a brief explanation for your evaluation]"
}}
""".strip()


def evaluate_relevance(question, answer):
    prompt = evaluation_prompt_template.format(question=question, answer=answer)
    evaluation, tokens = llm(prompt, model="gpt-4o-mini")

    try:
        json_eval = json.loads(evaluation)
        return json_eval, tokens
    except json.JSONDecodeError:
        result = {"Relevance": "UNKNOWN", "Explanation": "Failed to parse evaluation"}
        return result, tokens


def calculate_openai_cost(model, tokens):
    openai_cost = 0

    if model == "gpt-4o-mini":
        openai_cost = (
                              tokens["prompt_tokens"] * 0.00015 + tokens["completion_tokens"] * 0.0006
                      ) / 1000
    elif model == "gpt-4o":
        openai_cost = (
                              tokens["prompt_tokens"] * 0.0025 + tokens["completion_tokens"] * 0.01
                      ) / 1000

    else:
        print("Model not recognized. OpenAI cost calculation failed.")

    return openai_cost


def rag(query: str,
        search_function: Callable = index.search,
        model: str = "gpt-4o-mini"
        ):
    t0 = time()

    search_results = search(query=query, search_function=search_function)
    prompt = build_prompt(query, search_results)
    answer, token_stats = llm(prompt, model=model)

    relevance, rel_token_stats = evaluate_relevance(query, answer)

    t1 = time()
    took = t1 - t0

    openai_cost_rag = calculate_openai_cost(model, token_stats)
    openai_cost_eval = calculate_openai_cost(model, rel_token_stats)

    openai_cost = openai_cost_rag + openai_cost_eval

    answer_data = {
        "answer": answer,
        "model_used": model,
        "response_time": took,
        "relevance": relevance.get("Relevance", "UNKNOWN"),
        "relevance_explanation": relevance.get(
            "Explanation", "Failed to parse evaluation"
        ),
        "prompt_tokens": token_stats["prompt_tokens"],
        "completion_tokens": token_stats["completion_tokens"],
        "total_tokens": token_stats["total_tokens"],
        "eval_prompt_tokens": rel_token_stats["prompt_tokens"],
        "eval_completion_tokens": rel_token_stats["completion_tokens"],
        "eval_total_tokens": rel_token_stats["total_tokens"],
        "openai_cost": openai_cost,
    }

    return answer_data
