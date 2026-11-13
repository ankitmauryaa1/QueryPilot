
import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


def get_groq_client():

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is missing from .env"
        )

    return Groq(api_key=api_key)


def generate_response(prompt):

    client = get_groq_client()

    model = os.getenv(
        "GROQ_MODEL",
        "openai/gpt-oss-20b"
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are QueryPilot, an expert SQL assistant."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content


def correct_sql(question, failed_sql, error_message, schema):

    from ai_engine.prompt_builder import build_sql_prompt

    correction_prompt = f"""
You are QueryPilot's SQL debugging assistant.

USER QUESTION:
{question}

FAILED SQL:
{failed_sql}

MYSQL ERROR:
{error_message}

DATABASE SCHEMA:
{schema}

TASK:
Correct the failed SQL query so it answers the user's original question.

RULES:
1. Generate MySQL 8.0 compatible SQL.
2. Use only existing tables and columns.
3. Generate exactly one read-only SELECT query.
4. Never generate INSERT, UPDATE, DELETE, DROP,
   ALTER, CREATE or TRUNCATE.
5. Preserve the original business requirement.
6. Return only the corrected SQL query.
"""

    return generate_response(correction_prompt)



def generate_conversational_response(messages):

    client = get_groq_client()

    model = os.getenv(
        "GROQ_MODEL",
        "openai/gpt-oss-20b"
    )

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0
    )

    return response.choices[0].message.content


