
import re

from ai_engine.llm_client import generate_response, correct_sql
from ai_engine.prompt_builder import build_sql_prompt
from database.connection import get_engine
from database.schema_detector import detect_schema


def clean_sql_response(response):
    response = response.strip()

    # Remove Markdown SQL code fences
    response = re.sub(
        r"^```(?:sql)?\s*",
        "",
        response,
        flags=re.IGNORECASE
    )

    response = re.sub(r"\s*```$", "", response)

    return response.strip()


def generate_sql(question, history=None):
    engine = get_engine()

    try:
        schema = detect_schema(engine)

        # Pass conversation history to the prompt builder
        prompt = build_sql_prompt(
            question,
            schema,
            history
        )

        response = generate_response(prompt)

        return clean_sql_response(response)

    finally:
        engine.dispose()


def regenerate_sql(question, failed_sql, error_message):
    engine = get_engine()

    try:
        schema = detect_schema(engine)

        response = correct_sql(
            question,
            failed_sql,
            error_message,
            str(schema)
        )

        return clean_sql_response(response)

    finally:
        engine.dispose()
