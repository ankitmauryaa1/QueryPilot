
from ai_engine.llm_client import generate_response

if __name__ == "__main__":

    answer = generate_response(
        "Explain what a SQL JOIN is in simple language."
    )

    print("\nQueryPilot AI Response:\n")
    print(answer)
